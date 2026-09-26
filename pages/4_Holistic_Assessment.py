"""Explore the recalculated network-wide scenario outputs."""

import streamlit as st

from heathrow.analysis import ASSUMPTIONS, LINKS
from heathrow.data import load_network
from heathrow.ui import chart, download, location_map, page


def main() -> None:
    page("Holistic Assessment")
    st.write(
        "The four proposed hub connections are assessed together by comparing public "
        "transport journey times and Generalised Cost of Travel with the existing routes "
        "to Heathrow. The maps and table show the savings per passenger for each origin."
    )
    st.subheader("Generalised Cost of Travel")
    st.write(
        "Generalised Cost of Travel expresses the fare, journey time and carbon emissions "
        "in 2024 pounds per passenger. Time saved is valued because it can be used "
        "for work or leisure."
    )
    st.latex(r"GC = F + VOT \times T + Cost_{CO_2} \times emissions")
    st.caption(
        "F is the fare; VOT is the Value of Time; T is journey duration; "
        "Cost CO₂ is the monetary cost per unit of carbon emissions."
    )
    with st.expander("Values and sources used in the comparison"):
        st.caption(
            "Both assessments use the same fares, emissions factors and link distances. "
            "Source publications may now contain revised values."
        )
        st.markdown(
            "| Input | Value used | Source or assumption |\n"
            "| --- | --- | --- |\n"
            f"| Rail fare | £{ASSUMPTIONS.rail_fare_per_mile:.2f} per passenger-mile | Attributed to "
            "[ORR Table 1210](https://dataportal.orr.gov.uk/statistics/usage/passenger-rail-usage/"
            "table-1210-revenue-per-passenger-kilometres-and-per-passenger-journey/), "
            "accessed June 2024. |\n"
            f"| Trolleybus fare | £{ASSUMPTIONS.trolleybus_fare:.2f} per journey | Project assumption "
            "based on the [DfT £2 fare cap through 2024](https://www.gov.uk/government/news/"
            "major-150-million-funding-boost-for-local-bus-services-as-fare-cap-set-to-be-extended). |\n"
            f"| Working Value of Time | £{ASSUMPTIONS.working_value_of_time:.2f} per hour | Attributed to the "
            "[DfT TAG Data Book](https://www.gov.uk/government/publications/tag-data-book) "
            "(2023). |\n"
            f"| Non-working Value of Time | £{ASSUMPTIONS.nonworking_value_of_time:.5f} per hour |"
            "Retrieved from client. |\n"
            f"| Journey-purpose weights | {ASSUMPTIONS.business_share:.1%} business; "
            f"{1 - ASSUMPTIONS.business_share:.1%} non-working | Attributed to "
            "[DfT AVI0108: purpose of travel, 2012–2022]"
            "(https://assets.publishing.service.gov.uk/media/6579e81b095987001295e052/avi0108.ods). "
            "Used to weight the two Values of Time. |\n"
            f"| Carbon value | £{ASSUMPTIONS.carbon_gbp_per_tonne_2024:g} per tonne CO₂ | Attributed to the "
            "[DfT TAG Data Book](https://www.gov.uk/government/publications/tag-data-book) "
            "(2023), using the core value for 2024. |\n"
            f"| Rail emissions | {ASSUMPTIONS.rail_co2_g_per_passenger_mile:g} g CO₂ per passenger-mile | "
            "Attributed to the "
            "[DfT TAG Data Book](https://www.gov.uk/government/publications/tag-data-book) "
            "(2023). |\n"
            f"| Trolleybus emissions | {ASSUMPTIONS.trolleybus_co2_g_per_passenger_mile:g} g CO₂ "
            "per passenger-mile | Same TAG attribution and source-table limitation. |"
        )
        st.write(
            "Journey times and distances come from archived Google Distance Matrix "
            "responses, with project estimates added for the proposed hub-to-Heathrow "
            "legs. Including a carbon cost in passengers' choice of route is a model assumption."
        )
        st.table(
            [
                {
                    "Hub": route.title(),
                    "Selected mode": "Rail" if link.selected_mode == "train" else "Trolleybus",
                    "Link distance [km]": link.length_km(link.selected_mode),
                    "Link time [minutes]": link.proposed_minutes,
                }
                for route, link in LINKS.items()
            ]
        )
        st.caption(
            "Distances and times are project estimates. The original Staines estimate of "
            "6 minutes is retained as an assumption, not a verified trolleybus timetable."
        )
    st.write(
        "For each origin, the journey to each proposed hub is combined with the "
        "new link to Heathrow. The existing public transport route is also retained "
        "as an option. Comparing Generalised Cost of Travel identifies the preferred "
        "route under the model assumptions."
    )
    st.caption(
        "Reading, Uxbridge and Woking use rail; Staines uses trolleybus. The access legs "
        "to the hubs retain the original rail fare and emissions approximation for Google "
        "public transport journeys. The complementary Maidenhead night service and "
        "park-and-ride are outside this four-hub calculation."
    )
    st.write("Positive savings indicate an improvement over the existing journey.")
    data = load_network()
    selected = st.multiselect(
        "Focus on local authorities", sorted(data["Local Auth"].dropna().unique())
    )
    if selected:
        data = data[data["Local Auth"].isin(selected)]
    metric = st.radio(
        "Compare",
        ["Travel time saved [minutes]", "Generalised cost saving"],
        format_func=lambda value: (
            "Time Saved in Minutes"
            if value == "Travel time saved [minutes]"
            else "Change in Generalised Cost of Travel"
        ),
        horizontal=True,
    )
    if metric is None:
        st.stop()
    valid = data.dropna(subset=[metric])
    a, b, c = st.columns(3)
    a.metric("Authorities with observations", len(valid))
    b.metric("Authorities with an improvement", int((valid[metric] > 0).sum()))
    unit = "minutes" if metric == "Travel time saved [minutes]" else "£ per passenger"
    c.metric(f"Median saving ({unit})", f"{valid[metric].median():,.2f}" if len(valid) else "—")
    fig = location_map(data, metric, unit, signed=True)
    title = (
        "Public transport time saved [minutes]"
        if metric == "Travel time saved [minutes]"
        else "Public transport generalised cost saving [£ per passenger]"
    )
    fig.update_layout(title=title)
    chart(fig)
    st.caption(
        "Time and cost savings are calculated independently, so they can refer to different routes."
    )
    with st.expander("Compare authorities and download results", expanded=True):
        columns = [
            "Local Auth",
            "Travel time saved [minutes]",
            "GC Existing Public Transport",
            "GC Proposed Public Transport",
            "Generalised cost saving",
            "Best Public Transport Route",
        ]
        shown = data[columns].sort_values(metric, ascending=False)
        st.dataframe(shown, use_container_width=True, hide_index=True)
        download(shown, "heathrow-network-benefits.csv")


if __name__ == "__main__":
    main()
