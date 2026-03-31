"""Page 5: Outputs — Gantt chart, manpower loading, downloads."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import streamlit as st
import pandas as pd
from datetime import datetime

from angkin.db.database import get_schedule
from angkin.computation.scheduling import compute_manpower_loading
from angkin.export.gantt import create_gantt_chart
from angkin.export.manpower import create_manpower_chart, manpower_to_dataframe
from angkin.export.msproject import export_to_msproject_xml

st.set_page_config(page_title="Export", page_icon="📥", layout="wide")
st.title("📥 Export & Outputs")

if "project_id" not in st.session_state:
    st.warning("Please select or create a project on the Home page first.")
    st.stop()

project_id = st.session_state["project_id"]
project_name = st.session_state["project_name"]
st.caption(f"Project: **{project_name}**")

schedule = get_schedule(project_id)

if not schedule:
    st.info("No schedule computed yet. Run Compute first.")
    st.stop()

project_start = st.date_input("Project start date", value=datetime.now().date())
project_start_dt = datetime.combine(project_start, datetime.min.time())

st.divider()

# ── Gantt Chart ────────────────────────────────────────────
st.subheader("Gantt Chart")
gantt_fig = create_gantt_chart(schedule, project_start=project_start_dt)
st.plotly_chart(gantt_fig, use_container_width=True)

st.divider()

# ── Manpower Loading ───────────────────────────────────────
st.subheader("Manpower Loading Plan")
weekly = compute_manpower_loading(schedule)
manpower_fig = create_manpower_chart(weekly)
st.plotly_chart(manpower_fig, use_container_width=True)

manpower_df = manpower_to_dataframe(weekly)
if not manpower_df.empty:
    st.dataframe(manpower_df, use_container_width=True, hide_index=True)

st.divider()

# ── Cost Summary ───────────────────────────────────────────
st.subheader("Cost & Manhour Summary")
sched_df = pd.DataFrame(schedule)
total_mh = sched_df["adjusted_manhours"].sum()
total_days = max(it["end_day"] for it in schedule) if schedule else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Manhours", f"{total_mh:,.0f}")
with col2:
    st.metric("Duration", f"{total_days} days ({total_days / 6:.0f} weeks)")
with col3:
    total_crew = sched_df["crew_size"].max()
    st.metric("Peak Crew Size", total_crew)

st.divider()

# ── Downloads ──────────────────────────────────────────────
st.subheader("Downloads")

col1, col2, col3 = st.columns(3)

with col1:
    xml_content = export_to_msproject_xml(schedule, project_name, project_start_dt)
    st.download_button(
        "Download MS Project XML",
        data=xml_content,
        file_name=f"{project_name.replace(' ', '_')}_schedule.xml",
        mime="application/xml",
    )

with col2:
    csv_schedule = sched_df.to_csv(index=False)
    st.download_button(
        "Download Schedule CSV",
        data=csv_schedule,
        file_name=f"{project_name.replace(' ', '_')}_schedule.csv",
        mime="text/csv",
    )

with col3:
    if not manpower_df.empty:
        csv_manpower = manpower_df.to_csv(index=False)
        st.download_button(
            "Download Manpower CSV",
            data=csv_manpower,
            file_name=f"{project_name.replace(' ', '_')}_manpower.csv",
            mime="text/csv",
        )
