"""
app.py 
--------
Streamlit dashboard for visualizing aircraft fleet maintenance data.

This script connects to the SQLite databse (fleet_maintenance.db), loads maintenance records, and displays key metrics, upcoming tasks, and interactive charts for insights.

Run with:
    streamlit run src/app.py
"""

import sqlite3
import pandas as pd
import streamlit as st
import altair as alt
import os

# Path to the SQLite database (placed at project root level)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "fleet_maintenance.db")

def load_schedule():
    """
    Load maintenance schedule from the database.
    
    Returns:
        pd.DataFrame: DataFrame containing all recorrds from the maintenance_records table.
    """
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM maintenance_records"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def main():
    """
    Main entry point for the Streamlit dashboard.
    
    Displays:
        - Key performance indicators (KPIs).
        - Upcoming maintenance tasks table.
        - Charts (cost per aircraft, parts usage, maintenance timeline).
    """
    # Page Title
    st.title("Aircraft Fleet Maintenance Dashboard")
    # Style tweak: ensure KPI metric values display fully without truncation
    st.markdown("""
        <style>
        [data-testid = "stMetricValue"] {
                font-size: 20px;
                text-overflow: unset !important;
                white-space: nowrap !important;
        }
        </style>
    """, unsafe_allow_html = True)

    # Load data
    df = load_schedule()

    # Handle empty database
    if df.empty:
        st.warning("No maintenance records found. Please run data_sim.py and optimizer.py first.")
        return
    
    # KPIs Section
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    # Total number of maintenance tasks
    col1.metric("Total Maintenance Tasks", len(df))
    # Number of unique aircraft
    col2.metric("Unique Aircraft", df["aircraft_id"].nunique())
    # Total quantity of parts required
    col3.metric("Total Parts Needed", df["part_quantity"].sum())
    # Total estimated cost (formatted with commas and 2 decimal places)
    total_cost = df["cost"].sum()
    col4.metric("Total Estimated Cost", f"${format(total_cost, ',.2f')}")

    # Upcoming Tasks Table
    st.subheader("🛠️ Upcoming Maintenance Tasks")
    # Show next 20 tasks sorted by start date
    df_sorted = df.sort_values("schedule_start").head(20)
    st.dataframe(df_sorted)

    # Charts Section
    st.subheader("📈 Visual Insights")

    # 1. Cost per Aircraft
    cost_chart = alt.Chart(df).mark_bar().encode(
        x = "aircraft_id",
        y = "cost",
        tooltip = ["aircraft_id", "cost"]
    ).properties(title = "Cost per Aircraft", width = 700)
    st.altair_chart(cost_chart, use_container_width = True)

    # 2. Parts Usage
    parts_chart = alt.Chart(df).mark_bar().encode(
        x = "part_id",
        y = "part_quantity",
        tooltip = ["part_id", "part_quantity"] 
    ).properties(title = "Parts Usage", width = 700)
    st.altair_chart(parts_chart, use_container_width = True)

    # 3. Maintenance Timeline
    timeline_chart = alt.Chart(df).mark_bar().encode(
        x = "schedule_start:T",
        x2 = "schedule_end:T",
        y = "aircraft_id",
        tooltip = ["aircraft_id", "schedule_start", "schedule_end", "part_id", "cost"] 
    ).properties(title = "Maintenance Timeline", width = 700, height = 600)
    st.altair_chart(timeline_chart, use_container_width = True)

if __name__ == "__main__":
    main()
