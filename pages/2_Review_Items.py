"""Page 2: PM Review & Edit extracted scope items."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import streamlit as st
import pandas as pd
from angkin.db.database import get_scope_items, update_scope_items, insert_scope_items
from angkin.config import TRADES

st.set_page_config(page_title="Review Items", page_icon="✅", layout="wide")
st.title("✅ Review Extracted Items")

if "project_id" not in st.session_state:
    st.warning("Please select or create a project on the Home page first.")
    st.stop()

project_id = st.session_state["project_id"]
st.caption(f"Project: **{st.session_state['project_name']}**")

items = get_scope_items(project_id)

if not items:
    st.info("No extracted items yet. Upload a PDF first.")
    st.stop()

st.markdown(
    "Review and correct the extracted items below. "
    "**Nothing is computed until you confirm.**"
)
st.divider()

df = pd.DataFrame(items)
display_cols = ["id", "trade", "work_item", "quantity", "unit", "source"]
df_edit = df[display_cols].copy()

edited = st.data_editor(
    df_edit,
    column_config={
        "id": st.column_config.NumberColumn("ID", disabled=True),
        "trade": st.column_config.SelectboxColumn("Trade", options=TRADES, required=True),
        "work_item": st.column_config.TextColumn("Work Item", required=True),
        "quantity": st.column_config.NumberColumn("Quantity", min_value=0, required=True),
        "unit": st.column_config.TextColumn("Unit", required=True),
        "source": st.column_config.TextColumn("Source", disabled=True),
    },
    num_rows="dynamic",
    use_container_width=True,
    key="scope_editor",
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("Confirm Items", type="primary"):
        confirmed = edited.to_dict("records")
        existing_ids = {it["id"] for it in items}
        to_update = [r for r in confirmed if r.get("id") in existing_ids]
        to_insert = [r for r in confirmed if r.get("id") not in existing_ids and r.get("work_item")]

        if to_update:
            update_scope_items(to_update)
        if to_insert:
            insert_scope_items(project_id, to_insert)

        st.session_state["items_confirmed"] = True
        st.success(f"Confirmed {len(to_update) + len(to_insert)} items. Proceed to Compute.")

with col2:
    st.metric("Total items", len(edited))
    st.metric("Trades", edited["trade"].nunique() if not edited.empty else 0)
