# optimizer.py
import pandas as pd
from ortools.sat.python import cp_model
from utils import get_db_connection
from datetime import datetime
import random

# Planning parameters (tunable)
PLANNING_HORIZON_DAYS = 30    # Number of days to plan ahead
MAINT_DURATION_MIN = 1        # Minimum maintenance duration (days)
MAINT_DURATION_MAX = 2        # Maximum maintenance duration (days)
CREW_AVAILABLE = 2            # Limits how many aircraft can be in maintenance same day

# Load fleet and parts data
def load_data():
    """
    Connects to the database and retrieves fleet and parts inventory data.
    Returns:
        fleet_df (DataFrame): Fleet information
        parts_df (DataFrame): Parts inventory information
    """
    conn = get_db_connection()
    fleet_df = pd.read_sql_query("SELECT * FROM fleet", conn)
    parts_df = pd.read_sql_query("SELECT * FROM parts_inventory", conn)
    conn.close()
    return fleet_df, parts_df

# Generate optimized maintenance schedule
def generate_schedule(fleet_df, parts_df):
    """
    Creates a maintenance schedule using OR-Tools CP-SAT solver.
    The schedule respects crew availability, urgency (hours until maintenance due),
    and available parts.
    
    Args:
        fleet_df (DataFrame): Fleet information
        parts_df (DataFrame): Parts inventory information
    
    Returns:
        df_schedule (DataFrame): Scheduled maintenance for each aircraft
    """
    model = cp_model.CpModel()
    horizon = PLANNING_HORIZON_DAYS

    # List of all aircraft IDs
    aircraft_list = fleet_df["aircraft_id"].tolist()

    # Decision variables
    start_day = {}            # start day of maintenance per aircraft
    duration = {}             # maintenance duration per aircraft
    is_scheduled_on_day = {}  # boolean matrix: (aircraft, day) -> scheduled or not

    for aid in aircraft_list:
        start_day[aid] = model.NewIntVar(0, horizon - 1, f"start_{aid}")
        duration[aid] = model.NewIntVar(MAINT_DURATION_MIN, MAINT_DURATION_MAX, f"dur_{aid}")
        for d in range(horizon):
            is_scheduled_on_day[(aid, d)] = model.NewBoolVar(f"on_{aid}_d{d}")

        # Reified constraints to link start_day/duration with daily schedule
        for d in range(horizon):
            before = model.NewBoolVar(f"before_{aid}_d{d}")
            after = model.NewBoolVar(f"after_{aid}_d{d}")

            # before = start_day <= d
            model.Add(start_day[aid] <= d).OnlyEnforceIf(before)
            model.Add(start_day[aid] > d).OnlyEnforceIf(before.Not())

            # after = start_day + duration > d
            model.Add(start_day[aid] + duration[aid] > d).OnlyEnforceIf(after)
            model.Add(start_day[aid] + duration[aid] <= d).OnlyEnforceIf(after.Not())

            # aircraft is scheduled on day d if both before and after are true
            model.AddBoolAnd([before, after]).OnlyEnforceIf(is_scheduled_on_day[(aid, d)])
            model.AddBoolOr([before.Not(), after.Not()]).OnlyEnforceIf(is_scheduled_on_day[(aid, d)].Not())

    # Capacity constraint
    # Ensures no more aircraft are in maintenance than crew available on any day
    for d in range(horizon):
        model.Add(sum(is_scheduled_on_day[(aid, d)] for aid in aircraft_list) <= CREW_AVAILABLE)

    # Build a weighted objective that pushes urgent aircraft earlier:
    # urgency = smaller hours_until_due => higher weight
    max_hours = int(fleet_df["hours_until_due"].max()) if len(fleet_df) else 1
    weights = {}
    for _, row in fleet_df.iterrows():
        aid = row["aircraft_id"]
        # weight proportional to (max_hours - hours_until_due)
        urgency = int(row["hours_until_due"])
        # Normalize to [1..100]
        weight = max(1, int(((max_hours - urgency) / max_hours) * 100))
        weights[aid] = weight

    # Objective: minimize weighted sum of start days
    model.Minimize(sum(start_day[aid] * weights[aid] for aid in aircraft_list))

    # Solve the model
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("No feasible solution found")

    # Build schedule result (DataFrame)
    schedule_rows = []
    # copy parts for in-memory allocation and sort by quantity descending for distribution
    parts_copy = parts_df.copy().sort_values("quantity_on_hand", ascending=False).reset_index(drop=True)
    part_idx = 0  # round-robin index for allocating parts

    # total available parts sum
    total_parts_available = int(parts_copy["quantity_on_hand"].sum()) if not parts_copy.empty else 0

    for i, row in fleet_df.iterrows():
        aid = row["aircraft_id"]
        s = int(solver.Value(start_day[aid]))
        dur = int(solver.Value(duration[aid]))
        # Defaults if no parts allocated
        part_id = None
        part_quantity = 0
        cost = 0.0

        # Allocate one unit if parts available
        if total_parts_available > 0 and not parts_copy.empty:
            attempts = 0
            allocated = False
            while attempts < len(parts_copy) and not allocated:
                # wrap index
                if part_idx >= len(parts_copy):
                    part_idx = 0
                prow = parts_copy.loc[part_idx]
                avail = int(prow["quantity_on_hand"])
                if avail > 0:
                    part_id = prow["part_id"]
                    # Random consumption: 1..min(3, available stock)
                    part_quantity = random.randint(1, min(3, avail))
                    unit_cost = float(prow["unit_cost"])
                    cost = unit_cost * part_quantity
                    # Update (decrement) in-memory stock
                    parts_copy.at[part_idx, "quantity_on_hand"] = avail - part_quantity
                    total_parts_available -= part_quantity
                    allocated = True
                    # move part_idx forward for next allocation
                    part_idx = (part_idx + 1) % len(parts_copy)
                else:
                    part_idx = (part_idx + 1) % len(parts_copy)
                    attempts += 1
            # if no allocation found, defaults remain

        schedule_rows.append({
            "aircraft_id": aid,
            "schedule_start": pd.Timestamp.now().normalize() + pd.Timedelta(days=s),
            "schedule_end": pd.Timestamp.now().normalize() + pd.Timedelta(days=s + dur),
            "part_id": part_id,
            "part_quantity": part_quantity,
            "cost": cost,
            "status": "SCHEDULED"
        })

    df_schedule = pd.DataFrame(schedule_rows)
    return df_schedule

# Save schedule to database
def save_schedule_to_db(schedule_df):
    """
    Persists the maintenance schedule to the database.
    Replaces existing schedule if any.
    """
    conn = get_db_connection()
    schedule_df.to_sql("maintenance_records", conn, if_exists="replace", index=False)
    conn.close()
    print("Maintenance schedule saved to database")

# Run script directly
if __name__ == "__main__":
    fleet_df, parts_df = load_data()
    schedule_df = generate_schedule(fleet_df, parts_df)
    print(schedule_df)
    save_schedule_to_db(schedule_df)
