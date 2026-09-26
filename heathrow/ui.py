"""Shared dashboard layout and charts."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from heathrow.data import map_rows
from heathrow.paths import IMAGES


def page(title: str, description: str = "") -> None:
    st.set_page_config(page_title=title, page_icon=str(IMAGES / "logo.jpg"), layout="wide")
    st.markdown(
        """
        <style>
        [data-testid="stImage"],
        [data-testid="stTable"] table,
        [data-testid="stMarkdownContainer"] table,
        [data-testid="stDataFrame"],
        [data-testid="stPlotlyChart"] {
            margin-inline: auto;
        }
        [data-testid="stImage"],
        [data-testid="stImage"] img,
        [data-testid="stImageCaption"] {
            max-width: 100%;
        }
        [data-testid="stImage"] img {
            height: auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title(title)
    if description:
        st.markdown(description)


def chart(fig: go.Figure) -> None:
    title_text = fig.to_dict().get("layout", {}).get("title", {}).get("text") or ""
    fig.update_layout(
        font={"size": 13},
        margin={"l": 20, "r": 20, "t": 45, "b": 20},
        title={"text": title_text, "x": 0.5, "xanchor": "center"},
    )
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def location_map(frame: pd.DataFrame, column: str, unit: str, signed: bool = False) -> go.Figure:
    """Keep missing values local to the selected metric and sizes non-negative."""
    data = frame.replace([float("inf"), -float("inf")], float("nan"))
    data = map_rows(data, column)
    omitted = len(frame) - len(data)
    if omitted:
        st.caption(
            f"{omitted} authorities omitted from this map because the selected value or coordinates are unavailable."
        )
    if data.empty:
        st.info("No mapped observations for this selection. Heathrow is shown for reference.")
    values = data[column]
    maximum = max(float(values.abs().max()), 1) if len(data) else 1
    fig = go.Figure(
        go.Scattermapbox(
            lat=data["lat"],
            lon=data["lng"],
            text=data["Local Auth"],
            customdata=values,
            mode="markers",
            showlegend=False,
            marker={
                "size": values.abs(),
                "color": values,
                "sizemode": "area",
                "sizeref": maximum / 28**2,
                "sizemin": 4,
                "showscale": True,
                "cmin": -maximum if signed else 0,
                "cmax": maximum,
                "colorbar": {"title": unit},
            },
            hovertemplate="%{text}<br>%{customdata:,.2f} " + unit + "<extra></extra>",
        )
    )
    # A dark backing circle keeps the airport marker distinct against the map and data.
    fig.add_scattermapbox(
        lat=[51.470020],
        lon=[-0.454295],
        mode="markers",
        marker={"size": 22, "color": "#202124", "opacity": 1},
        showlegend=False,
        hoverinfo="skip",
    )
    fig.add_scattermapbox(
        lat=[51.470020],
        lon=[-0.454295],
        mode="markers",
        marker={"size": 16, "color": "#FF8C00", "opacity": 1},
        showlegend=True,
        name="Heathrow",
        text=["Heathrow Airport"],
        hovertemplate="%{text}<extra></extra>",
    )
    fig.update_layout(
        mapbox={
            "style": "open-street-map",
            "zoom": 5.5,
            "center": {"lat": 52, "lon": -1.2},
        },
        legend={
            "orientation": "h",
            "x": 0,
            "xanchor": "left",
            "y": -0.05,
            "yanchor": "top",
        },
        height=480,
    )
    return fig


def download(frame: pd.DataFrame, filename: str) -> None:
    st.download_button(
        "Download displayed data (CSV)",
        frame.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )
