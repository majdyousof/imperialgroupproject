"""Plotly figures without Streamlit rendering or data loading."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from heathrow.analysis import SHARES, YEARS


def earnings_chart(
    data: dict[str, pd.DataFrame], percentage_val: int, linkoption: str
) -> go.Figure:
    year = list(YEARS)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=year,
            y=data["rail"][percentage_val - 1],
            mode="lines",
            name="Rail solution",
            line={"width": 3},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=year,
            y=data["trolley"][percentage_val - 1],
            mode="lines",
            name="Trolley Bus solution",
            line={"width": 3},
        )
    )

    fig.update_layout(
        yaxis_range=[
            min(
                data["rail"][percentage_val - 1].min(),
                data["trolley"][percentage_val - 1].min(),
            ),
            max(
                data["rail"][percentage_val - 1].max(),
                data["trolley"][percentage_val - 1].max(),
            ),
        ]
    )

    fig.add_hline(y=0, line_dash="dash", line_width=1)

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Total Earnings [£ million]",
        title=f"{linkoption} Mode comparison for {percentage_val}% share of total Heathrow passengers",
        legend={"title": "Mode type:"},
    )

    return fig


def earnings_surfaces(data: dict[str, pd.DataFrame], route: str) -> go.Figure:
    year = list(YEARS)
    poppercent = list(SHARES)
    fig2 = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "surface"}, {"type": "surface"}]],
        subplot_titles=("Rail solution", "Trolley Bus solution"),
        horizontal_spacing=0.12,
    )
    fig2.add_trace(
        go.Surface(
            z=data["rail"],
            y=year,
            x=poppercent,
            name="Rail Solution",
            showscale=False,
        ),
        row=1,
        col=1,
    )
    fig2.add_trace(
        go.Surface(
            z=data["trolley"],
            y=year,
            x=poppercent,
            name="Trolley Bus Solution",
            showscale=False,
        ),
        row=1,
        col=2,
    )

    fig2.update_layout(
        title_text="",
        height=600,
        margin={"l": 30, "r": 30, "t": 55, "b": 30},
        uirevision=route,
    )

    fig2.update_scenes(
        xaxis={"title": "Passenger share [%]", "nticks": 5},
        yaxis={"title": "Year", "nticks": 5, "tickformat": "d"},
        zaxis={"title": "Earnings [£ million]", "nticks": 5, "tickformat": ",.0f"},
        camera={
            "eye": {"x": 1.5, "y": -1.6, "z": 1.3},
            "up": {"x": 0, "y": 0, "z": 1},
            "projection": {"type": "orthographic"},
        },
        aspectmode="manual",
        aspectratio={"x": 1, "y": 1, "z": 0.75},
    )

    return fig2


def qualitative_chart(
    scores: dict[str, dict[str, float]], labels: list[str], title: str, axis: str
) -> go.Figure:
    fig = go.Figure(
        [
            go.Bar(
                name=name,
                y=labels,
                x=[scores[label.lower()][mode] for label in labels],
                orientation="h",
            )
            for mode, name in [("rail", "Rail solution"), ("trolley", "Trolley Bus solution")]
        ]
    )
    fig.update_layout(
        title=title,
        xaxis_title="Average score",
        yaxis_title=axis,
        legend_title_text="Mode",
        xaxis_range=[0, 4],
    )
    return fig
