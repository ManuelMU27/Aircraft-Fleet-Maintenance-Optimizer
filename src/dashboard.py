"""
dashboard.py
-------------
Console-based dashboard for summarizing maintenance schedules.

This script queries the `maintenance_records` table from the database
and provides a text-based overview of the fleet’s maintenance status.

Run with:
    python src/dashboard.py
"""

import pandas as pd
from utils import get_db_connection

def load_schedule():
    """
    Load maintenance records from the database.

    Returns:
        pd.DataFrame: A DataFrame containing maintenance records.
                      If the table does not exist, returns an empty DataFrame.
    """
    conn = get_db_connection()
    # Display available tables in the database for debugging
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type = 'table';", conn)
    print("\nAvailable tables in DB:", tables["name"].tolist())

    try:
        # Attempt to read the maintenance records
        df = pd.read_sql_query("SELECT * FROM maintenance_records", conn)
    except Exception as e:
        print("Error loading schedule:", e)
        df = pd.DataFrame()  # Return empty DataFrame if query fails
    conn.close()
    return df

def summarize_schedule(df):
    """
    Print a summary of the maintenance schedule to the console.

    Args:
        df (pd.DataFrame): DataFrame of maintenance records.
    """
    if df.empty:
        print("\nNo maintenance records found in database. Did you run optimizer.py?")
        return
    
    print("\n--- Maintenance Schedule Summary ---\n")
    print(f"Total scheduled maintenance: {len(df)}")
    print(f"Unique aircraft: {df['aircraft_id'].nunique()}")
    print(f"Total parts needed: {df['part_quantity'].sum()}")
    print(f"Total estimated cost: ${df['cost'].sum():,.2f}\n")

    print("Next 10 maintenance tasks:")
    print(df.sort_values("schedule_start").head(10)[
        ["aircraft_id", "schedule_start", "schedule_end", "part_id", "part_quantity", "cost", "status"]
    ])

def main():
    # Main entry point: load schedule and print summary.
    df_schedule = load_schedule()
    summarize_schedule(df_schedule)

if __name__ == "__main__":
    main()
