# validate_setup.py
# Script to verify the project setup, including folder structure and database tables

from pathlib import Path
from utils import get_db_connection
import pandas as pd

# Define project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]       # Root folder of the project
ASSETS_DIR = PROJECT_ROOT / "assets"                     # Folder containing CSV asset files
DB_PATH = PROJECT_ROOT / "fleet_maintenance.db"          # Path to main SQLite database

# Display project structure
print("Project root:", PROJECT_ROOT)
print("Assets folder:", ASSETS_DIR)
print("DB path:", DB_PATH)

# List CSV files in the assets folder
print("\nFiles in assets:")
for p in sorted(ASSETS_DIR.glob("*.csv")):
    print("-", p.name)

# Verify database tables
# Connect to the database and check each expected table for row counts
conn = get_db_connection()
for t in ["fleet", "parts_inventory", "maintenance_records"]:
    try:
        df = pd.read_sql_query(f"SELECT COUNT(*) as c FROM {t}", conn)
        print(f"Table {t}: {int(df['c'].iloc[0])} rows")
    except Exception as e:
        print(f"Table {t}: error -> {e}")
conn.close()
