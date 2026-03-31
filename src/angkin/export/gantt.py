"""Gantt chart generation using Plotly."""

from __future__ import annotations

from datetime import datetime, timedelta

import plotly.figure_factory as ff
import plotly.graph_objects as go
import pandas as pd


TRADE_COLORS = {
    "Civil / Structural": "#2563eb",
    "Architectural / Finishing": "#d97706",
}


def create_gantt_chart(
    schedule: list[dict],
    project_start: datetime | None = None,
) -> go.Figure:
    """Build a Plotly Gantt chart from schedule items."""
    if project_start is None:
        project_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    df_rows = []
    for item in schedule:
        start = project_start + timedelta(days=item["start_day"] - 1)
        end = project_start + timedelta(days=item["end_day"])
        df_rows.append({
            "Task": item["work_item"],
            "Start": start,
            "Finish": end,
            "Trade": item["trade"],
            "Crew": item["crew_size"],
            "Manhours": item["adjusted_manhours"],
        })

    if not df_rows:
        fig = go.Figure()
        fig.add_annotation(text="No schedule data", showarrow=False, font=dict(size=20))
        return fig

    df = pd.DataFrame(df_rows)

    fig = ff.create_gantt(
        df,
        colors=TRADE_COLORS,
        index_col="Trade",
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True,
        title="Project Schedule — Gantt Chart",
    )

    fig.update_layout(
        height=max(400, len(df_rows) * 35 + 100),
        xaxis_title="Date",
        font=dict(size=12),
        margin=dict(l=250),
    )

    return fig
