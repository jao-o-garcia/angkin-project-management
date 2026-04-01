"""Page 2: Scope-by-scope extraction loop."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import streamlit as st
import pandas as pd
from angkin.extraction.vision import extract_scope_from_pages
from angkin.db.database import (
    get_drawing_pages, get_scope_items, insert_scope_items,
    update_scope_items, delete_scope_items_for_scope,
    lock_scope, unlock_scope, get_locked_scopes, delete_scope_item,
)
from angkin.config import SCOPE_TYPES, TRADES

st.set_page_config(page_title="Extract", page_icon="🔍", layout="wide")
st.title("🔍 Extract BOQ — Scope by Scope")

if "project_id" not in st.session_state:
    st.warning("Please select or create a project on the Home page first.")
    st.stop()

project_id = st.session_state["project_id"]
st.caption(f"Project: **{st.session_state['project_name']}**")

pages = get_drawing_pages(project_id)
if not pages:
    st.warning("No drawings loaded. Go to **Upload** first.")
    st.stop()

locked_scopes = get_locked_scopes(project_id)

st.markdown(
    "Select a scope, choose which drawing pages are relevant, then run the AI analysis. "
    "Review and confirm each scope before moving to the next."
)
st.divider()

# ── Scope selector ──────────────────────────────────────────
scope = st.selectbox(
    "Select scope to analyze",
    SCOPE_TYPES,
    format_func=lambda s: f"{'🔒 ' if s in locked_scopes else ''}{s}",
)

is_locked = scope in locked_scopes

if is_locked:
    st.success(f"**{scope}** is confirmed and locked.")
    if st.button("Unlock to re-analyze", type="secondary"):
        unlock_scope(project_id, scope)
        delete_scope_items_for_scope(project_id, scope)
        st.rerun()
    st.divider()

# ── Page selector ───────────────────────────────────────────
st.subheader(f"Select drawings for: {scope}")

page_labels = [f"Page {p['page_number']} — {p['drawing_type']}" for p in pages]
selected_indices = st.multiselect(
    "Which pages show information relevant to this scope?",
    range(len(pages)),
    format_func=lambda i: page_labels[i],
    key=f"pages_{scope}",
    disabled=is_locked,
)

if selected_indices and not is_locked:
    # Show thumbnails of selected pages
    thumb_cols = st.columns(min(len(selected_indices), 4))
    for col, idx in zip(thumb_cols, selected_indices[:4]):
        with col:
            st.image(pages[idx]["image_data"], caption=page_labels[idx], use_container_width=True)
    if len(selected_indices) > 4:
        st.caption(f"...and {len(selected_indices) - 4} more page(s) selected")

st.divider()

# ── Run extraction ──────────────────────────────────────────
if not is_locked:
    use_heavy = st.checkbox(
        "Use high-accuracy model (claude-opus-4-6) — slower, better for complex structural drawings",
        value=False,
    )

    col_run, col_info = st.columns([1, 3])
    with col_run:
        run_btn = st.button(
            "Analyze selected pages",
            type="primary",
            disabled=not selected_indices,
        )
    with col_info:
        if not selected_indices:
            st.caption("Select at least one page to enable analysis.")

    if run_btn and selected_indices:
        selected_pages = [pages[i] for i in selected_indices]
        images = [p["image_data"] for p in selected_pages]
        drawing_types = [p["drawing_type"] for p in selected_pages]

        with st.spinner(f"Analyzing {len(images)} page(s) for {scope}..."):
            try:
                result = extract_scope_from_pages(
                    images=images,
                    scope=scope,
                    drawing_types=drawing_types,
                    use_heavy_model=use_heavy,
                )
            except ValueError as e:
                st.error(str(e))
                st.stop()
            except Exception as e:
                st.error(f"Extraction failed: {e}")
                st.stop()

        if result.items:
            delete_scope_items_for_scope(project_id, scope)
            insert_scope_items(project_id, [it.to_dict() for it in result.items])
            st.success(f"Extracted **{len(result.items)}** items for **{scope}**. Review and confirm below.")
            st.rerun()
        else:
            st.warning("No items extracted. Try selecting different pages or use the heavy model.")
            if result.skipped > 0:
                st.caption(f"{result.skipped} item(s) were returned but failed schema validation.")
            with st.expander("🔍 Raw Claude response (debug)", expanded=True):
                st.code(result.raw_response or "(empty response)", language="json")

st.divider()

# ── Review table ────────────────────────────────────────────
st.subheader(f"Review: {scope}")

scope_items = get_scope_items(project_id, scope=scope)

if not scope_items:
    st.info("No items for this scope yet. Select pages and run analysis above.")
else:
    df = pd.DataFrame(scope_items)
    display_cols = ["id", "trade", "work_item", "quantity", "unit", "basis"]
    df_edit = df[display_cols].copy()

    edited = st.data_editor(
        df_edit,
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "trade": st.column_config.SelectboxColumn("Trade", options=TRADES, required=True),
            "work_item": st.column_config.TextColumn("Work Item", required=True, width="large"),
            "quantity": st.column_config.NumberColumn("Qty", min_value=0, required=True, width="small"),
            "unit": st.column_config.TextColumn("Unit", width="small"),
            "basis": st.column_config.TextColumn("Basis (AI source note)", width="large", disabled=True),
        },
        num_rows="dynamic",
        use_container_width=True,
        disabled=is_locked,
        key=f"editor_{scope}",
    )

    st.divider()

    if not is_locked:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Confirm & Lock this scope", type="primary"):
                existing_ids = {it["id"] for it in scope_items}
                records = edited.to_dict("records")
                to_update = [r for r in records if r.get("id") in existing_ids]
                to_insert = [r for r in records if r.get("id") not in existing_ids and r.get("work_item")]
                to_delete_ids = existing_ids - {r["id"] for r in to_update}

                if to_update:
                    update_scope_items(to_update)
                if to_insert:
                    new_items = [
                        {**r, "scope": scope, "source": "manual"}
                        for r in to_insert
                    ]
                    insert_scope_items(project_id, new_items)
                for item_id in to_delete_ids:
                    delete_scope_item(item_id)

                lock_scope(project_id, scope)
                st.success(f"Scope **{scope}** confirmed and locked.")
                st.rerun()
        with col2:
            st.metric("Items", len(edited))
        with col3:
            total_qty = edited["quantity"].sum() if not edited.empty else 0
            st.metric("Total Qty", f"{total_qty:,.1f}")

# ── Progress summary ────────────────────────────────────────
st.divider()
st.subheader("Extraction Progress")
progress_cols = st.columns(3)
for i, s in enumerate(SCOPE_TYPES):
    items_for_scope = get_scope_items(project_id, scope=s)
    status = "🔒 Locked" if s in locked_scopes else (f"📋 {len(items_for_scope)} items" if items_for_scope else "⬜ Not started")
    with progress_cols[i % 3]:
        st.markdown(f"**{s}**  \n{status}")
