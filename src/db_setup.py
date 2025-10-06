# db_setup.py
from utils import execute_script

# SQL schema definition for the fleet maintenance database.
# Includes fleet data, parts inventory, and maintenance scheduling tables.
SQL_SCRIPT = """
-- Drop existing tables to ensure a clean setup
DROP TABLE IF EXISTS fleet;
DROP TABLE IF EXISTS parts_inventory;

-- Fleet table: stores aircraft-level operational and maintenance data
CREATE TABLE fleet (
    aircraft_id TEXT PRIMARY KEY,                             -- Unique identifier for each aircraft
    flight_hours INTEGER,                                     -- Total flight hours logged
    maint_interval_hours INTEGER,                             -- Interval (in hours) at which maintenance is required
    last_maintenance_date TEXT,                               -- Last date when maintenance was performed
    hours_since_last_maintenance INTEGER,                     -- Derived field: hours accumulated since last maintenance
    hours_until_due INTEGER                                   -- Derived field: hours remaining until next maintenance is due
);

-- Parts inventory table: tracks availability and details of critical parts
CREATE TABLE parts_inventory (
    part_id TEXT PRIMARY KEY,                                 -- Unique identifier for each part
    description TEXT,                                         -- Description of the part
    lead_time_days INTEGER,                                   -- Supplier lead time (in days) to restock the part
    unit_cost REAL,                                           -- Cost per unit of the part
    quantity_on_hand INTEGER                                  -- Current stock level
);

-- Maintenance records table: logs scheduled maintenance activities
CREATE TABLE IF NOT EXISTS maintenance_records (
    maintenance_id INTEGER PRIMARY KEY AUTOINCREMENT,         -- Unique ID for each maintenance record
    aircraft_id TEXT NOT NULL,                                -- Aircraft undergoing maintenance
    schedule_start TEXT NOT NULL,                             -- Scheduled start date/time
    schedule_end TEXT NOT NULL,                               -- Scheduled end date/time
    part_id TEXT,                                             -- Part required for this task (if applicable)
    part_quantity INTEGER,                                    -- Quantity of the part required
    cost REAL,                                                -- Estimated/actual cost of the maintenance
    status TEXT DEFAULT 'SCHEDULED',                          -- Status of the task (SCHEDULED, COMPLETED, etc.)
    -- Define relationships to enforce referential integrity
    FOREIGN KEY (aircraft_id) REFERENCES fleet(aircraft_id),
    FOREIGN KEY (part_id) REFERENCES parts_inventory(part_id)
);
"""

if __name__ == "__main__":
    # Execute the SQL script to create or reset the database schema
    execute_script(SQL_SCRIPT)
    print("Database schema created (fleet_maintenance.db)")
