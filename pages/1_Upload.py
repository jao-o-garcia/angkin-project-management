"""Page 1: PDF Upload & Page Labeling."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import streamlit as st
from angkin.extraction.rasterizer import rasterize_pdf, page_count
from angkin.db.database import save_drawing_pages, get_drawing_pages, update_drawing_type
from angkin.config import DRAWING_TYPES

st.set_page_config(page_title="Upload", page_icon="📄", layout="wide")
st.title("📄 Upload Drawings")

if "project_id" not in st.session_state:
    st.warning("Please select or create a project on the Home page first.")
    st.stop()

project_id = st.session_state["project_id"]
project_name = st.session_state["project_name"]
st.caption(f"Project: **{project_name}**")

# ── Check for existing pages ────────────────────────────────
existing_pages = get_drawing_pages(project_id)
if existing_pages:
    st.info(
        f"This project has **{len(existing_pages)}** drawing pages loaded. "
        "You can update drawing type labels below, or upload a new PDF to replace them."
    )

st.divider()

# ── Upload ──────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Upload architectural/structural PDF drawings",
    type=["pdf"],
    accept_multiple_files=False,
    help="Upload the full set of drawings as a single PDF. Multi-page PDFs are supported.",
)

if uploaded is not None:
    pdf_bytes = uploaded.read()
    n_pages = page_count(pdf_bytes)
    st.markdown(f"**{uploaded.name}** — {n_pages} page(s), {len(pdf_bytes) / 1024:.0f} KB")

    if st.button(f"Rasterize {n_pages} page(s)", type="primary"):
        progress = st.progress(0, text="Rasterizing pages...")
        with st.spinner("Converting PDF to images..."):
            images = rasterize_pdf(pdf_bytes)

        pages_data = []
        for i, img_bytes in enumerate(images):
            pages_data.append({
                "page_number": i + 1,
                "drawing_type": "Unknown",
                "image_data": img_bytes,
            })
            progress.progress((i + 1) / len(images), text=f"Page {i + 1} of {len(images)}")

        save_drawing_pages(project_id, pages_data)
        progress.empty()
        st.success(f"Saved {len(images)} pages. Now label each drawing type below.")
        st.rerun()

st.divider()

# ── Drawing type labeling ───────────────────────────────────
pages = get_drawing_pages(project_id)
if not pages:
    st.info("No drawings loaded yet. Upload a PDF above.")
    st.stop()

st.subheader(f"Label Drawing Types ({len(pages)} pages)")
st.markdown(
    "Tell the AI what each page shows. This helps it analyze the right scope from the right drawing."
)

# Show pages in a grid with type selectors
cols_per_row = 3
for row_start in range(0, len(pages), cols_per_row):
    row_pages = pages[row_start : row_start + cols_per_row]
    cols = st.columns(cols_per_row)
    for col, page in zip(cols, row_pages):
        with col:
            st.image(
                page["image_data"],
                caption=f"Page {page['page_number']}",
                use_container_width=True,
            )
            current_type = page.get("drawing_type", "Unknown")
            new_type = st.selectbox(
                f"Page {page['page_number']} type",
                DRAWING_TYPES,
                index=DRAWING_TYPES.index(current_type) if current_type in DRAWING_TYPES else 0,
                key=f"dtype_{page['id']}",
                label_visibility="collapsed",
            )
            if new_type != current_type:
                update_drawing_type(page["id"], new_type)
                st.rerun()

st.divider()
st.markdown("Labels are saved automatically. Proceed to **Extract** to start the BOQ analysis.")
