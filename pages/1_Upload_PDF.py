"""Page 1: PDF Upload & Extraction."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import streamlit as st
from angkin.extraction.confidence import extract_scope_items
from angkin.db.database import insert_scope_items, get_scope_items

st.set_page_config(page_title="Upload PDF", page_icon="📄", layout="wide")
st.title("📄 Upload PDF")

if "project_id" not in st.session_state:
    st.warning("Please select or create a project on the Home page first.")
    st.stop()

project_id = st.session_state["project_id"]
project_name = st.session_state["project_name"]
st.caption(f"Project: **{project_name}**")

existing = get_scope_items(project_id)
if existing:
    st.info(f"This project already has {len(existing)} extracted items. "
            "Uploading a new PDF will replace them.")

st.divider()

uploaded = st.file_uploader(
    "Upload a construction PDF (Bill of Quantities, Scope of Work, etc.)",
    type=["pdf"],
    accept_multiple_files=False,
)

if uploaded is not None:
    pdf_bytes = uploaded.read()
    st.markdown(f"**File:** {uploaded.name} ({len(pdf_bytes) / 1024:.0f} KB)")

    if st.button("Extract Scope Items", type="primary"):
        with st.spinner("Analyzing PDF... This may take a moment for scanned documents."):
            try:
                items, method = extract_scope_items(pdf_bytes)
            except ValueError as e:
                st.error(str(e))
                st.stop()
            except Exception as e:
                st.error(f"Extraction failed: {e}")
                st.stop()

        st.success(f"Extracted **{len(items)}** items using **{method}** method.")

        if items:
            insert_scope_items(project_id, items)
            st.session_state["extraction_method"] = method
            st.session_state["extraction_count"] = len(items)

            st.markdown("### Preview")
            import pandas as pd
            df = pd.DataFrame(items)[["trade", "work_item", "quantity", "unit", "source"]]
            st.dataframe(df, use_container_width=True)
            st.markdown("→ Go to **Review Items** to confirm and edit.")
        else:
            st.warning("No items could be extracted. Try a different PDF or check the document format.")
