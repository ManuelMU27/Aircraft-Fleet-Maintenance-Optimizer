# ingest.py
import pandas as pd
from pathlib import Path
from utils import get_db_connection

# Define project root and assets directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = PROJECT_ROOT / "assets"

def ingest_csv_to_table(csv_path: Path, table_name: str):
    """
    Reads a CSV file and ingests its contents into a specified SQLite table.
    If the table already exists, it will be replaced.

    Args:
        csv_path (Path): Path to the CSV file containing data.
        table_name (str): Name of the database table to load the data into.
    """
    csv_path = Path(csv_path)
    # Ensure the CSV file exists before attempting ingestion
    if not csv_path.exists():
        raise FileNotFoundError(f"{csv_path} not found")
    # Load CSV data into a pandas DataFrame
    df = pd.read_csv(csv_path)
    # Establish database connection
    conn = get_db_connection()
    # Insert DataFrame into SQLite database
    # if_exists="replace" ensures old data is overwritten with the new data
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    # Close connection to free resources
    conn.close()
    # Confirmation log with row count
    print(f"Ingested {csv_path.name} -> {table_name} ({len(df)} rows)")

if __name__ == "__main__":
    # Ingest generated CSVs into the database
    ingest_csv_to_table(ASSETS_DIR / "fleet.csv", "fleet")
    ingest_csv_to_table(ASSETS_DIR / "parts_inventory.csv", "parts_inventory")
