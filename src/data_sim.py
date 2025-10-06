# src/data_sim.py
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Define the root directory of the project and create an "assets" folder for storing generated data files.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = PROJECT_ROOT / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Set a fixed random seed for reproducibility of generated data.
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
# Default number of aircraft to generate for the fleet dataset.
NUM_AIRCRAFT = 50 # Can be scaled to generate more aircraft if needed.

def generate_fleet(num_aircraft: int = NUM_AIRCRAFT):
    """
    Generate a simulated dataset representing a fleet of aircraft.

    Args:
        num_aircraft (int): Number of aircraft records to generate.

    Returns:
        pd.DataFrame: DataFrame containing aircraft IDs, flight hours,
                      maintenance intervals, last maintenance dates,
                      and calculated maintenance metrics.
    """
    # Create aircraft IDs in the format "AIR-####"
    aircraft_ids = [f"AIR-{1001 + i}" for i in range(num_aircraft)]
    # Randomize operational and maintenance attributes
    flight_hours = np.random.randint(500, 5000, size=num_aircraft) # Total flight hours logged
    maint_interval_hours = np.random.randint(400, 1200, size=num_aircraft) # Maintenance interval thresholds
    days_since_maint = np.random.randint(1, 400, size=num_aircraft) # Days since last maintenance
    # Calculate last maintenance date based on days since last maintenance
    last_maintenance_date = [(datetime.utcnow() - pd.Timedelta(days=int(d))).date().isoformat() for d in days_since_maint]

    # Build fleet dataset
    df = pd.DataFrame({
        "aircraft_id": aircraft_ids,
        "flight_hours": flight_hours,
        "maint_interval_hours": maint_interval_hours,
        "last_maintenance_date": last_maintenance_date
    })
    # Derived fields: maintenance metrics
    df["hours_since_last_maintenance"] = df["flight_hours"] % df["maint_interval_hours"]
    df["hours_until_due"] = df["maint_interval_hours"] - df["hours_since_last_maintenance"]
    return df

def generate_parts_inventory(num_parts: int = 20): # Can change the amount of parts required
    """
    Generate a simulated dataset representing an aircraft parts inventory.

    Args:
        num_parts (int): Number of parts to generate.

    Returns:
        pd.DataFrame: DataFrame containing part IDs, descriptions, lead times,
                      unit costs, and quantities on hand.
    """
    # Create part IDs in the format "PART-###"
    part_ids = [f"PART-{101 + i}" for i in range(num_parts)]
    # Randomize part attributes
    lead_time_days = np.random.randint(1, 30, size=num_parts) # Lead time for ordering replacements
    unit_cost = np.round(np.random.uniform(100.0, 5000.0, size=num_parts), 2) # Cost per unit
    quantity_on_hand = np.random.randint(5, 50, size=num_parts) # Inventory available
    # Build parts inventory dataset
    df = pd.DataFrame({
        "part_id": part_ids,
        "description": [f"critical part {i}" for i in range(num_parts)],
        "lead_time_days": lead_time_days,
        "unit_cost": unit_cost,
        "quantity_on_hand": quantity_on_hand
    })
    return df

if __name__ == "__main__":
    # Generate fleet and parts datasets
    df_fleet = generate_fleet()
    df_parts = generate_parts_inventory()
    # Save the datasets as CSV files inside the assets directory
    df_fleet.to_csv(ASSETS_DIR / "fleet.csv", index=False)
    df_parts.to_csv(ASSETS_DIR / "parts_inventory.csv", index=False)
    # Notify user that files were successfully created
    print("Generated:", ASSETS_DIR / "fleet.csv", ASSETS_DIR / "parts_inventory.csv")
