"""Manpower loading chart and table generation."""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd


def create_manpower_chart(weekly_loading: list[dict]) -> go.Figure:
    """Build a stacked bar chart of weekly crew counts per trade."""
    if not weekly_loading:
        fig = go.Figure()
        fig.add_annotation(text="No manpower data", showarrow=False, font=dict(size=20))
        return fig

    df = pd.DataFrame(weekly_loading)

    fig = go.Figure()

    trades = df["trade"].unique()
    colors = {"Civil / Structural": "#2563eb", "Architectural / Finishing": "#d97706"}

    for trade in trades:
        trade_data = df[df["trade"] == trade]
        fig.add_trace(go.Bar(
            x=[f"Week {w}" for w in trade_data["week"]],
            y=trade_data["crew_count"],
            name=trade,
            marker_color=colors.get(trade, "#6b7280"),
        ))

    fig.update_layout(
        barmode="stack",
        title="Manpower Loading Plan — Weekly Crew Count",
        xaxis_title="Week",
        yaxis_title="Crew Count",
        height=400,
        font=dict(size=12),
    )

    return fig


def manpower_to_dataframe(weekly_loading: list[dict]) -> pd.DataFrame:
    """Pivot weekly loading into a table: weeks as rows, trades as columns."""
    if not weekly_loading:
        return pd.DataFrame()

    df = pd.DataFrame(weekly_loading)
    pivot = df.pivot_table(index="week", columns="trade", values="crew_count", fill_value=0)
    pivot.index.name = "Week"
    pivot["Total"] = pivot.sum(axis=1)
    return pivot.reset_index()
