"""Page 3: Historical Efficiency Rate Import."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import streamlit as st
import pandas as pd
from angkin.db.database import upsert_efficiency_rate, get_efficiency_rates
from angkin.config import TRADES, DEFAULT_EFFICIENCY_RATE

st.set_page_config(page_title="Historical Data", page_icon="📊", layout="wide")
st.title("📊 Historical Efficiency Rates")

st.markdown(
    "Upload past project Excel files to extract actual site efficiency rates, "
    "or manually set rates per trade."
)
st.divider()

# ── Current rates ──────────────────────────────────────────
st.subheader("Current Efficiency Rates")

current_rates = get_efficiency_rates()
for trade in TRADES:
    if trade not in current_rates:
        current_rates[trade] = DEFAULT_EFFICIENCY_RATE

rate_df = pd.DataFrame([
    {"Trade": t, "Efficiency Rate": r, "Meaning": f"Crew operates at {r*100:.0f}% of standard pace"}
    for t, r in current_rates.items()
])
st.dataframe(rate_df, use_container_width=True, hide_index=True)

st.divider()

# ── Manual override ────────────────────────────────────────
st.subheader("Adjust Rates Manually")

with st.form("manual_rates"):
    cols = st.columns(len(TRADES))
    new_rates: dict[str, float] = {}
    for i, trade in enumerate(TRADES):
        with cols[i]:
            new_rates[trade] = st.slider(
                trade,
                min_value=0.3,
                max_value=1.5,
                value=current_rates.get(trade, DEFAULT_EFFICIENCY_RATE),
                step=0.05,
                help="1.0 = standard pace. Below 1.0 = slower crew. Above 1.0 = faster crew.",
            )
    if st.form_submit_button("Save Rates"):
        for trade, rate in new_rates.items():
            upsert_efficiency_rate(trade, rate, source_file="manual")
        st.success("Efficiency rates updated.")
        st.rerun()

st.divider()

# ── Excel import ───────────────────────────────────────────
st.subheader("Import from Historical Excel")

uploaded = st.file_uploader(
    "Upload a past project Excel file",
    type=["xlsx", "xls"],
    accept_multiple_files=False,
)

if uploaded is not None:
    try:
        xl = pd.ExcelFile(uploaded)
        sheet_name = st.selectbox("Select sheet", xl.sheet_names)
        df = xl.parse(sheet_name)
        st.dataframe(df.head(20), use_container_width=True)

        st.markdown(
            "Map columns to extract efficiency data. "
            "Look for columns with actual vs planned manhours or productivity rates."
        )

        cols_available = df.columns.tolist()
        trade_col = st.selectbox("Trade column", ["(none)"] + cols_available)
        actual_col = st.selectbox("Actual manhours column", ["(none)"] + cols_available)
        planned_col = st.selectbox("Planned manhours column", ["(none)"] + cols_available)

        if st.button("Compute Efficiency from Excel"):
            if trade_col == "(none)" or actual_col == "(none)" or planned_col == "(none)":
                st.error("Please map all three columns.")
            else:
                df_clean = df[[trade_col, actual_col, planned_col]].dropna()
                df_clean[actual_col] = pd.to_numeric(df_clean[actual_col], errors="coerce")
                df_clean[planned_col] = pd.to_numeric(df_clean[planned_col], errors="coerce")
                df_clean = df_clean.dropna()

                if df_clean.empty:
                    st.error("No valid numeric rows found.")
                else:
                    grouped = df_clean.groupby(trade_col).agg(
                        actual=(actual_col, "sum"),
                        planned=(planned_col, "sum"),
                    )
                    grouped["efficiency"] = grouped["planned"] / grouped["actual"]

                    for trade_name, row in grouped.iterrows():
                        eff = round(min(max(row["efficiency"], 0.3), 1.5), 2)
                        upsert_efficiency_rate(str(trade_name), eff, source_file=uploaded.name)

                    st.success("Efficiency rates imported from Excel.")
                    st.dataframe(grouped, use_container_width=True)
                    st.rerun()
    except Exception as e:
        st.error(f"Error reading Excel: {e}")
