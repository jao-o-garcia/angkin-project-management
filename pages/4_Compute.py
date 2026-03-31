"""Page 4: Manhour Computation & Schedule Generation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import streamlit as st
import pandas as pd
from angkin.db.database import (
    get_scope_items, get_efficiency_rates, get_manhour_norms,
    save_schedule, get_schedule,
)
from angkin.computation.manhours import compute_manhours
from angkin.computation.scheduling import generate_schedule, compute_manpower_loading
from angkin.config import DEFAULT_EFFICIENCY_RATE, TRADES

st.set_page_config(page_title="Compute", page_icon="🔧", layout="wide")
st.title("🔧 Compute Schedule")

if "project_id" not in st.session_state:
    st.warning("Please select or create a project on the Home page first.")
    st.stop()

project_id = st.session_state["project_id"]
st.caption(f"Project: **{st.session_state['project_name']}**")

items = get_scope_items(project_id)
if not items:
    st.info("No scope items found. Upload and review a PDF first.")
    st.stop()

efficiency_rates = get_efficiency_rates()
for trade in TRADES:
    if trade not in efficiency_rates:
        efficiency_rates[trade] = DEFAULT_EFFICIENCY_RATE

norms = get_manhour_norms()

st.markdown(f"**{len(items)}** scope items | **{len(norms)}** labor norms loaded")
st.divider()

# ── Compute parameters ─────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    target_crew = st.number_input(
        "Target crew size per activity", min_value=1, max_value=50, value=8
    )
with col2:
    st.markdown("**Efficiency rates in use:**")
    for trade, rate in efficiency_rates.items():
        st.write(f"- {trade}: {rate*100:.0f}%")

st.divider()

if st.button("Compute Manhours & Schedule", type="primary"):
    with st.spinner("Computing..."):
        computed = compute_manhours(items, norms, efficiency_rates)
        schedule = generate_schedule(computed, target_crew_size=target_crew)
        weekly = compute_manpower_loading(schedule)

    save_schedule(project_id, schedule)
    st.session_state["computed"] = computed
    st.session_state["schedule"] = schedule
    st.session_state["weekly_loading"] = weekly

    st.success("Computation complete!")

# ── Display results ────────────────────────────────────────
if "computed" in st.session_state:
    computed = st.session_state["computed"]
    schedule = st.session_state["schedule"]

    st.subheader("Manhour Summary")
    comp_df = pd.DataFrame(computed)
    display_cols = ["trade", "work_item", "quantity", "unit", "base_manhours",
                    "efficiency_rate", "adjusted_manhours", "estimated_cost", "norm_matched"]
    st.dataframe(comp_df[display_cols], use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        total_mh = comp_df["adjusted_manhours"].sum()
        st.metric("Total Adjusted Manhours", f"{total_mh:,.0f}")
    with col2:
        total_cost = comp_df["estimated_cost"].sum()
        st.metric("Estimated Labor Cost", f"₱{total_cost:,.0f}")
    with col3:
        unmatched = comp_df[~comp_df["norm_matched"]].shape[0]
        if unmatched:
            st.metric("Unmatched Items", unmatched, delta="needs norms", delta_color="inverse")
        else:
            st.metric("Unmatched Items", 0)

    st.divider()
    st.subheader("Schedule")
    sched_df = pd.DataFrame(schedule)
    st.dataframe(
        sched_df[["trade", "work_item", "crew_size", "duration_days",
                   "adjusted_manhours", "start_day", "end_day"]],
        use_container_width=True, hide_index=True,
    )

    if schedule:
        total_days = max(it["end_day"] for it in schedule)
        st.metric("Project Duration", f"{total_days} working days ({total_days / 6:.0f} weeks)")

    st.markdown("→ Go to **Export** for Gantt chart, manpower plan, and downloads.")
