"""Page 3: Confirmed BOQ summary across all locked scopes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import streamlit as st
import pandas as pd
from angkin.db.database import get_scope_items, get_locked_scopes
from angkin.config import SCOPE_TYPES

st.set_page_config(page_title="BOQ Summary", page_icon="📋", layout="wide")
st.title("📋 BOQ Summary")

if "project_id" not in st.session_state:
    st.warning("Please select or create a project on the Home page first.")
    st.stop()

project_id = st.session_state["project_id"]
st.caption(f"Project: **{st.session_state['project_name']}**")

locked_scopes = get_locked_scopes(project_id)
all_items = get_scope_items(project_id)

if not all_items:
    st.info("No items confirmed yet. Go to **Extract** to analyze drawings scope by scope.")
    st.stop()

# ── Summary metrics ─────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Confirmed scopes", f"{len(locked_scopes)} / {len(SCOPE_TYPES)}")
with col2:
    st.metric("Total BOQ items", len(all_items))
with col3:
    pending = [s for s in SCOPE_TYPES if s not in locked_scopes and get_scope_items(project_id, scope=s)]
    st.metric("Scopes in review", len(pending))

st.divider()

# ── Full BOQ table ──────────────────────────────────────────
st.subheader("Full Bill of Quantities")

df = pd.DataFrame(all_items)
display_cols = ["scope", "trade", "work_item", "quantity", "unit", "basis", "source"]
available_cols = [c for c in display_cols if c in df.columns]
df_display = df[available_cols].copy()

# Highlight locked vs unlocked
if "scope" in df_display.columns:
    df_display.insert(0, "status", df_display["scope"].map(
        lambda s: "🔒" if s in locked_scopes else "📝"
    ))

st.dataframe(
    df_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "status": st.column_config.TextColumn("", width="small"),
        "scope": st.column_config.TextColumn("Scope", width="medium"),
        "trade": st.column_config.TextColumn("Trade", width="medium"),
        "work_item": st.column_config.TextColumn("Work Item", width="large"),
        "quantity": st.column_config.NumberColumn("Qty", width="small"),
        "unit": st.column_config.TextColumn("Unit", width="small"),
        "basis": st.column_config.TextColumn("AI Basis", width="large"),
        "source": st.column_config.TextColumn("Source", width="small"),
    },
)

st.divider()

# ── Breakdown by scope ──────────────────────────────────────
st.subheader("By Scope")
if "scope" in df.columns:
    scope_summary = (
        df.groupby("scope")
        .agg(items=("id", "count"))
        .reset_index()
    )
    scope_summary["locked"] = scope_summary["scope"].map(lambda s: "🔒 Yes" if s in locked_scopes else "📝 In review")
    st.dataframe(scope_summary, use_container_width=True, hide_index=True)

st.divider()

# ── Export BOQ as CSV ───────────────────────────────────────
csv = df_display.drop(columns=["status"], errors="ignore").to_csv(index=False)
project_name = st.session_state.get("project_name", "project")
st.download_button(
    "Download BOQ as CSV",
    data=csv,
    file_name=f"{project_name.replace(' ', '_')}_BOQ.csv",
    mime="text/csv",
)

st.markdown("When all scopes are confirmed, proceed to **History** then **Compute**.")
