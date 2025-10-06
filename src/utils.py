# utils.py 
# Centralized utility functions for database operations

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Tuple

# Project database path
# Resolves the root directory of the project and constructs path to the main SQLite database
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = str(PROJECT_ROOT / "fleet_maintenance.db")

# Database connection helper
def get_db_connection() -> sqlite3.Connection:
    """
    Returns an SQLite database connection with foreign keys enforcement enabled.
    Foreign key support ensures referential integrity between fleet, parts_inventory, and maintenance_records tables.
    """
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Execute SELECT queries returning pandas DataFrame
def df_from_query(query: str, params: tuple = ()) -> pd.DataFrame:
    """
    Executes a SQL SELECT query and returns results as a pandas DataFrame.
    
    Args:
        query (str): SQL query string
        params (tuple, optional): Query parameters for placeholders (default empty)
    
    Returns:
        pd.DataFrame: Query results
    """
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Execute multi-statement SQL scripts
def execute_script(script: str):
    """
    Executes a multi-statement SQL script (e.g., creating or resetting tables).
    
    Args:
        script (str): SQL script containing one or more SQL statements
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.executescript(script)
    conn.commit()
    conn.close()
