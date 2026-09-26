"""Explore the historical Heathrow surface-access demand dataset."""

import math

import plotly.express as px
import streamlit as st

from heathrow.data import LONDON_AUTHORITIES, MODES, load_demand, rail_share
from heathrow.ui import chart, download, location_map, page


def main() -> None:
    page("Heathrow Trips: A review")
    st.caption("A 3 week design project conducted at Imperial College London")
    st.subheader("Current Surface Access at Heathrow")
    st.write(
        "It is expected that the proposed expansion of Heathrow would increase demand for international travel substantially, "
        "which will likely increase the congestion of the surrounding road networks, decreasing both the efficiency of transport and the air quality of the area (which is already affected by the extensive flights as Heathrow is one of the Largest International airports in the world). "
        "The aim of this project is to improve surface access to address this, particularly from the south "
        "and south-west of England, and to encourage a mode shift from private vehicles to public transport. This page explores the current demand and mode shares for travel to Heathrow."
    )
    st.write(
        "The starting point is where passengers travel from and how they reach Heathrow. "
        "The figures below use 2019 demand data supplied by ARUP and archived Google "
        "journey estimates."
    )
    with st.expander("Data sources"):
        st.markdown(
            "- **Passenger demand and mode shares:** 2019 origin–destination data "
            "supplied by ARUP for the coursework. The original survey publication "
            "has not been identified.\n"
            "- **Journey times and distances:** archived Google Distance Matrix "
            "estimates collected during the project. These are separate from the "
            "2019 demand observations. "
            "[Google's service documentation](https://developers.google.com/maps/"
            "documentation/distance-matrix/distance-matrix) explains the journey estimates."
        )
    with st.expander("Passenger travel"):
        st.write(
            "Ease of travel with luggage, quick journey time, value for money and "
            "flexibility are key factors in passengers' choice of transport, and directly contribute to the utility of a journey. Improving "
            "surface access therefore involves both the journey itself and how easily "
            "passengers can use the service."
        )
    data = load_demand()
    modes = MODES
    include_london = st.sidebar.toggle(
        "Include London",
        value=True,
        help=(
            "Applies to all Home maps, totals, charts and the data download. "
            "London includes all 32 boroughs and the City of London."
        ),
    )
    selected = st.multiselect(
        "Focus on local authorities",
        sorted(data["Local Auth"].dropna().unique()),
        help="Leave empty to show all available authorities.",
    )
    if selected:
        data = data[data["Local Auth"].isin(selected)]
    if not include_london:
        data = data[~data["Local Auth"].isin(LONDON_AUTHORITIES)]
    if data.empty:
        st.info(
            "No authorities match these filters. Adjust the authority selection or include London."
        )
    total = data["Total Annual Demand"].sum(min_count=1)
    a, b, c = st.columns(3)
    a.metric("Annual journeys in selection", f"{total:,.0f}" if math.isfinite(total) else "—")
    b.metric("Local authorities", f"{len(data):,}")
    share = rail_share(data)
    c.metric("Rail share of journeys", f"{share:.1%}" if share is not None else "—")
    missing = int(data["Mode Share Rail"].isna().sum())
    if missing:
        st.info(
            f"{missing} authorities lack a valid modal split and are excluded from the rail-share calculation."
        )
    demand, times, table = st.tabs(["Journey demand", "Travel efficiency", "Explore data"])
    with demand:
        st.write(
            "The 2019 demand data shows high vehicle demand in London and in some areas "
            "to the west and south-west. Outside London, rail demand is much lower than "
            "vehicle demand. Passengers may travel through London to reach Heathrow by "
            "public transport, or travel directly by car or taxi."
        )
        st.info(
            "This initial analysis takes into account only first-order origin-destination flows "
            "to Heathrow, which considers some journeys which are done via London, "
            "as the passenger's original starting point. In the UK, it is often the case that passengers, "
            "even if they live closer to Heathrow, will use London as a hub to reach the airport. This is particularly true for passengers from the south-west of England, "
            "where public transport connections to Heathrow are limited. This is a limitation of the dataset used which is acknowledged in the analysis"
            " and accepted due to time constraints."
        )
        chosen = st.selectbox(
            "Choose mode to compare demand:",
            [
                "Total Annual Demand",
                "Car Demand",
                "Taxi Demand",
                "Car + taxi demand",
                "Rail Demand",
                "Other Demand",
            ],
            format_func=lambda value: {
                "Other Demand": "Other",
                "Car + taxi demand": "Vehicle Demand",
            }.get(value, value),
        )
        if chosen is not None:
            fig = location_map(data, chosen, "journeys/year")
            label = {"Other Demand": "Other", "Car + taxi demand": "Vehicle Demand"}.get(
                chosen, chosen
            )
            fig.update_layout(title=f"{label} to Heathrow in 2019 (Source: ARUP)")
            chart(fig)
        st.subheader("Total Annual trips and mode share per local authority")
        selected_modes = []
        for mode, column in zip(modes, st.columns(len(modes))):
            if column.checkbox(mode, value=True, key=f"demand_{mode.lower()}"):
                selected_modes.append(mode)
        if not selected_modes:
            st.info("Select at least one transport mode to show the demand chart.")
        else:
            selected_columns = [f"{mode} Demand" for mode in selected_modes]
            ranked = data.dropna(subset=selected_columns).copy()
            ranked["Selected-mode demand"] = ranked[selected_columns].sum(axis=1)
            top = (
                ranked.sort_values(["Selected-mode demand", "Local Auth"], ascending=[False, True])
                .head(15)
                .iloc[::-1]
            )
            st.caption(
                f"Up to 15 authorities ranked by combined annual journeys for "
                f"{', '.join(selected_modes)}, "
                + ("including London." if include_london else "excluding London.")
            )
            if top.empty:
                st.info(
                    "No authorities with valid demand and mode shares match this chart selection."
                )
            else:
                fig = px.bar(
                    top,
                    y="Local Auth",
                    x=selected_columns,
                    orientation="h",
                    labels={
                        "value": "Annual journeys (selected modes)",
                        "variable": "Mode",
                        "Local Auth": "Local authority",
                    },
                    title="Annual journeys by local authority",
                )
                fig.update_layout(height=500, legend_title_text="Mode")
                chart(fig)
    with times:
        st.write(
            "The journey estimates show that public transport travel time per kilometre "
            "is on average higher than for cars, particularly in the south-western area "
            "near London. Even areas close to Heathrow can have a much longer journey "
            "by public transport. Lower values on this map mean less time travelling "
            "per kilometre."
        )
        chosen = st.radio(
            "Choose mode to compare travel time to distance ratio:",
            ["Car minutes per km", "Transit minutes per km"],
            format_func=lambda value: value.replace(" minutes per km", " Travel minutes per km"),
            horizontal=True,
        )
        if chosen is not None:
            fig = location_map(data, chosen, "min/km")
            label = chosen.replace(" minutes per km", " Travel minutes per km")
            fig.update_layout(title=f"{label} to Heathrow (Source: Google Distance Matrix API)")
            chart(fig)
    with table:
        st.dataframe(data, use_container_width=True, hide_index=True)
        download(data, "heathrow-demand.csv")

    st.write(
        "This baseline assessment identifies Reading, Woking, Uxbridge (Hillingdon) and Staines (Spelthorne) as good candidate "
        "links to investigate. This is due to their strategic location and potential for integration "
        "with the proposed transport infrastructure, as well as their high demand for travel to Heathrow, with high vehicle usage mode shares."
    )


if __name__ == "__main__":
    main()
