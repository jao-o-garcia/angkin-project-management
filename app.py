"""Angkin — Streamlit entry point (home page)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
from angkin.db.database import list_projects, create_project, get_connection
from angkin.db.models import init_db
from angkin.computation.norms import DEFAULT_NORMS
from angkin.db.database import seed_default_norms
from angkin.config import DB_PATH

init_db(DB_PATH)
seed_default_norms(DEFAULT_NORMS)

st.set_page_config(
    page_title="Angkin — Construction Scheduler",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏗️ Angkin")
st.subheader("Residential Construction Project Scheduler")

st.markdown("""
**Workflow:** Upload PDF → Review extracted items → Import historical data → Compute schedule → Export

Use the sidebar to navigate between steps.
""")

st.divider()

# ── Project selector / creator ──────────────────────────────
st.header("Projects")

projects = list_projects()

col1, col2 = st.columns([2, 1])

with col1:
    if projects:
        options = {p["id"]: f"{p['name']} (created {p['created_at'][:10]})" for p in projects}
        selected_id = st.selectbox(
            "Select a project",
            options.keys(),
            format_func=lambda x: options[x],
        )
        st.session_state["project_id"] = selected_id
        st.session_state["project_name"] = next(
            p["name"] for p in projects if p["id"] == selected_id
        )
    else:
        st.info("No projects yet. Create one to get started.")

with col2:
    with st.form("new_project"):
        st.markdown("**New Project**")
        name = st.text_input("Project name")
        desc = st.text_input("Description (optional)")
        if st.form_submit_button("Create"):
            if name.strip():
                pid = create_project(name.strip(), desc.strip())
                st.session_state["project_id"] = pid
                st.session_state["project_name"] = name.strip()
                st.rerun()
            else:
                st.error("Project name is required.")

if "project_id" in st.session_state:
    st.success(f"Active project: **{st.session_state['project_name']}**")
    st.markdown("👈 Use the sidebar to proceed to **Upload PDF**.")
