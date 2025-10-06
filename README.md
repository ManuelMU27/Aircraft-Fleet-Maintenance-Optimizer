Aircraft Fleet Maintenance & Logistics Optimizer

A self-contained project that simulates aircraft fleet and parts inventory data, builds optimized maintenance schedules (minimizing downtime while respecting crew capacity and part availability), and provides both a command-line summary and an interactive Streamlit dashboard.
What this demonstrates: data engineering + SQLite, optimization with OR-Tools, inventory allocation, and visualization (Plotly / Altair / Streamlit).

📂 Project Structure

AircraftFleetMaintenance_Optimizer/
├─ assets/                        # auto-created CSVs (fleet.csv, parts_inventory.csv)
├─ src/
│  ├─ __pycache__/                # Python cache (auto)
│  ├─ app.py                      # Streamlit web app (interactive dashboard)
│  ├─ check_parts.py              # small helper to preview parts (dev/test)
│  ├─ dashboard.py                # CLI summary (dev/debug)
│  ├─ data_sim.py                 # generates fleet.csv and parts_inventory.csv into assets/
│  ├─ db_setup.py                 # creates SQLite schema (fleet_maintenance.db)
│  ├─ ingest.py                   # loads CSVs from assets/ into the DB
│  ├─ optimizer.py                # the scheduling + allocation optimizer (creates maintenance_records)
│  ├─ records_available.py        # helper / dev script
│  ├─ test_db.py                  # test helper (dev)
│  ├─ utils.py                    # DB connection + helper functions (used by scripts)
│  └─ validate_setup.py           # quick validation checks (dev)
├─ fleet_maintenance.db           # main SQLite DB (production data)
├─ requirements.txt               # Python dependencies (see below)
├─ .gitignore
└─ venv/                          # virtual environment (do NOT commit)

⚙️ Quick install (Windows, from project root)

    1. Activate your virtual environment (if you already created it): 

        venv\Scripts\activate

    2. Install dependencies:

        pip install -r requirements.txt

▶️ Execution order (run these in this exact order from the project root)

Each command should be run from the project root (where src/ and fleet_maintenance.db live):

    1. Generate CSVs (fleet + parts) — writes assets/fleet.csv and assets/parts_inventory.csv:

        python src\data_sim.py

    2. Create / reset the DB schema (creates fleet_maintenance.db tables fleet and parts_inventory):

        python src\db_setup.py

    3. Load CSVs into the DB (ingest into fleet and parts_inventory):

        python src\ingest.py

    4. Run the optimizer (creates maintenance_records table in fleet_maintenance.db and prints schedule):

        python src\optimizer.py

    5. Quick console summary (optional check):

        python src\dashboard.py

    6. Interactive dashboard (Streamlit web UI):

        streamlit run src\app.py

            - Streamlit will occupy the terminal while running. Open the Local URL shown in the terminal (usually http://localhost:8501).
            - When finished, stop the Streamlit server with Ctrl+C in the terminal.

Quick validation & debugging tips

    - If app.py complains no such table: maintenance_records, make sure you ran python src\optimizer.py and that fleet_maintenance.db is the expected DB file used by app.py.

    - To inspect tables in the DB quickly:

        python -c "from src.utils import get_db_connection; import pandas as pd; conn=get_db_connection(); print(pd.read_sql_query('SELECT name FROM sqlite_master WHERE type=''table''', conn)); conn.close()"

    - To preview schedule rows:

        python -c "from src.utils import get_db_connection; import pandas as pd; conn=get_db_connection(); print(pd.read_sql_query('SELECT * FROM maintenance_records LIMIT 10', conn)); conn.close()"
