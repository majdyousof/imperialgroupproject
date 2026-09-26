"""Link earnings and qualitative assessment page."""

import streamlit as st

from heathrow.analysis import ASSUMPTIONS, MULTIPLIERS, SHARES, YEARS
from heathrow.charts import earnings_chart, earnings_surfaces, qualitative_chart
from heathrow.data import first_break_even, load_scenario
from heathrow.models import ScenarioSelection
from heathrow.qualitative import FACTOR_SCORES, LINK_SCORES
from heathrow.ui import chart, download, page


def main() -> None:
    page(
        "Link-to-link Quantitative Assessment",
    )
    st.write(
        "Rail and trolleybus alternatives are compared by their cumulative earnings "
        "and break-even year. The qualitative assessment below considers stakeholder "
        "satisfaction, social factors and feasibility."
    )
    st.markdown("Toggle between link options using the **dropdown menu** in the **sidebar**.")
    st.subheader("Earnings equation")
    st.write(
        "For each mode, cumulative earnings deduct construction costs from the sum "
        "of annual fare earnings less operating and carbon costs, with the adjustments below:"
    )
    st.latex(
        r"\mathrm{Earnings}_{(i,y)} = -N_i \times D \times M + "
        r"\sum_{j=2026}^{y} "
        r"\left(F_{(i,j)} - \left(O_{(i,j)} + C_{(i,j)}\right) \times D \times M\right) "
        r"\times I_{(j)}"
    )
    st.markdown(
        "| Factor | Meaning in the calculation |\n"
        "| --- | --- |\n"
        "| $N$ | **Initial cost of the mode construction:** the cost of establishing the link, "
        "estimated from past case studies and infrastructure cost data, typically depending "
        "on the distance covered. |\n"
        f"| $D$ | **Optimism bias uplift:** costs are multiplied by "
        f"**{ASSUMPTIONS.optimism_bias:.2f}**. |\n"
        "| $M$ | **Cost multiplier:** accounts for possible differences in costs. "
        "A slider value of 100% corresponds to $M=1$. |\n"
        "| $F$ | **Fare earnings:** annual revenue based on passenger trips and link distance. "
        f"Both assessments use £{ASSUMPTIONS.rail_fare_per_mile:.2f} per passenger-mile "
        f"for rail and £{ASSUMPTIONS.trolleybus_fare:.2f} per journey for trolleybus. |\n"
        "| $O$ | **Operating costs:** annual employee salaries, maintenance and other running "
        f"costs, including refurbishment every {ASSUMPTIONS.trolleybus_refurbishment_years} "
        f"years for trolleybuses and every {ASSUMPTIONS.rail_refurbishment_years} years for rail. |\n"
        "| $C$ | **Carbon costs:** the monetary cost of emissions from operating the link, "
        "based on passenger trips, distance, emissions per passenger-mile and carbon "
        "cost per tonne. |\n"
        "| $I$ | **Inflation deflator:** adjusts each year's earnings relative to the initial "
        "year, using the TAG data book series. |\n"
        "| $y$ | **Current year of analysis:** annual contributions are summed from "
        "$j=2026$ to this year; 2025 contains initial expenditure only. |\n"
        "| $i$ | **Percentage share of total Heathrow passengers travelling through the link:** "
        "the assumed proportion of forecast Heathrow passenger trips using this connection. |"
    )
    with st.expander("Sources of values and assumptions"):
        st.caption(
            "Recalculated using shared 2024 assumptions. The source publications may "
            "now contain revised values."
        )
        st.markdown(
            "- **Optimism bias and inflation:** the original source cited for the 1.56 "
            "factor and inflation deflator is the "
            "[DfT TAG Data Book](https://www.gov.uk/government/publications/tag-data-book), "
            "accessed in May 2024. The exact table supporting 56% was not recorded, so "
            "this remains the adopted project assumption rather than a verified rate "
            "for every proposed mode.\n"
            f"- **Rail fare (£{ASSUMPTIONS.rail_fare_per_mile:.2f} per passenger-mile):** "
            "the common fare is attributed to "
            "[ORR Table 1210](https://dataportal.orr.gov.uk/statistics/usage/passenger-rail-usage/"
            "table-1210-revenue-per-passenger-kilometres-and-per-passenger-journey/)\n"
            "- **Trolleybus fare (£2 per passenger):** a project assumption based "
            "on DfT's £2 bus fare cap. The "
            "[2023 extension announcement](https://www.gov.uk/government/news/"
            "major-150-million-funding-boost-for-local-bus-services-as-fare-cap-set-to-be-extended) "
            "confirms the cap through December 2024; applying it to a proposed "
            "trolleybus service is a modelling choice.\n"
            "- **Carbon valuation:** the cited basis for the annual carbon cost series is "
            "[UK Government greenhouse gas valuation guidance (2021)]"
            "(https://www.gov.uk/government/publications/valuing-greenhouse-gas-emissions-in-policy-appraisal/"
            "valuation-of-greenhouse-gas-emissions-for-policy-appraisal-and-evaluation).\n"
            f"- **Emissions:** {ASSUMPTIONS.rail_co2_g_per_passenger_mile:g} g CO₂ per "
            f"passenger-mile for rail and {ASSUMPTIONS.trolleybus_co2_g_per_passenger_mile:g} "
            "for trolleybus. These are estimates inferred from the [DfT TAG Data Book](https://www.gov.uk/government/publications/tag-data-book) \n"
            "- **Refurbishment intervals:** the 15-year trolleybus and 60-year rail "
            "intervals are project assumptions."
        )
        st.markdown(
            "**Other project assumptions**\n\n"
            f"- Passenger demand grows linearly from {ASSUMPTIONS.passengers_2024 / 1e6:g} "
            f"million in 2024 to {ASSUMPTIONS.passengers_2036 / 1e6:g} million in 2036, "
            "then continues at the same rate for the longer link comparison. Each link "
            "carries the selected share of that total. This is a project scenario, "
            "not a capacity-constrained demand forecast.\n"
            "- Emissions are specified per passenger-mile and are not divided by vehicle capacity.\n"
            "- Operating costs and fares per person remain constant apart from inflation "
            "adjustments.\n"
            "- Annual carbon values and the inflation index use the original cost workbook.\n"
            "- Only first-order flows to Heathrow are considered."
        )
    st.write(
        "Vary the passenger share and cost multiplier to explore uncertainty in demand "
        "and costs. Both modes use the same settings, initially 10% and 100% respectively."
    )

    st.caption(
        "These recalculated earnings use common inputs with the Holistic Assessment. "
        "They retain the original inflation adjustment."
    )
    year = list(YEARS)
    poppercent = list(SHARES)
    multipliers = list(MULTIPLIERS)

    linkoption = st.sidebar.selectbox(
        "*Select link for comparison:*",
        options=[
            "Heathrow-Reading",
            "Heathrow-Woking",
            "Heathrow-Uxbridge",
            "Heathrow-Staines",
        ],
    )

    percentage_val = st.select_slider(
        "*Select percentage [%] of total Heathrow passenger demand on link:*",
        value=10,
        options=poppercent,
    )

    multval = st.select_slider("*Select cost multiplier [%]:*", value=100, options=multipliers)

    if linkoption is None:
        st.stop()
    if not isinstance(percentage_val, int) or not isinstance(multval, int):
        st.error("Choose one passenger share and one cost multiplier.")
        st.stop()

    route = linkoption.removeprefix("Heathrow-").lower()
    selections = {
        label: ScenarioSelection.model_validate(
            {
                "route": route,
                "mode": mode,
                "cost_multiplier_pct": multval,
                "passenger_share_pct": percentage_val,
            }
        )
        for label, mode in [("rail", "train"), ("trolley", "trolley")]
    }
    data = {label: load_scenario(selection) for label, selection in selections.items()}
    for label, mode in zip(st.columns(2), ["rail", "trolley"]):
        crossing = first_break_even(year, data[mode][selections[mode].share_index])
        label.metric(
            f"{mode.title()} · first non-negative year",
            str(crossing) if crossing else f"Not by {YEARS[-1]}",
        )
    st.caption("Break-even is the first calculated year with non-negative cumulative earnings.")

    chart(earnings_chart(data, percentage_val, linkoption))
    with st.expander("Explore all passenger shares in 3D"):
        if st.checkbox("Show 3D comparison", value=False):
            st.caption(f"{linkoption} · Drag to rotate; use the camera controls to reset the view.")
            st.plotly_chart(
                earnings_surfaces(data, route),
                use_container_width=True,
                theme="streamlit",
                key=f"link-surfaces-{route}",
                config={"displayModeBar": True},
            )

    export = data["rail"][[percentage_val - 1]].copy()
    export.columns = ["Rail earnings [GBP million]"]
    export["Trolleybus earnings [GBP million]"] = data["trolley"][percentage_val - 1]
    export.insert(0, "Year", year)
    download(export, f"{route}-{percentage_val}percent-cost{multval}.csv")

    # qualitative
    st.title("Link-to-link Qualitative Assessment")
    st.write(
        "Ten factors are assessed for each link and mode: six stakeholder satisfaction "
        "factors, three social factors and one feasibility factor. Each factor is rated "
        "by at least four assessors to reduce individual bias, and the scores are averaged. "
        "The scale is 1 (unsatisfactory), 2 (somewhat unsatisfactory), "
        "3 (somewhat satisfactory) and 4 (satisfactory), with no neutral midpoint."
    )
    st.write(
        "The scores were obtained from the clients and project supervisors through the methodology proposal. They remain "
        "fixed when the quantitative assessment sliders change."
    )
    with st.expander("Qualitative assessment framework"):
        st.write(
            "Stakeholder satisfaction is assessed separately for TfL, DfT, the London "
            "Mayor, Network Rail, local government and other stakeholders. A London "
            "Mayor satisfaction score below 3 is a reason to reconsider a proposal "
            "within this assessment framework, because of the importance of Mayoral "
            "involvement in construction and planning permission."
        )
        st.markdown(
            "**Social factors**\n\n"
            "- **Accessibility:** how accommodating the mode is and how easily passengers "
            "can get into and out of it.\n"
            "- **Safety:** safety of the transport mode, its construction and associated "
            "infrastructure.\n"
            "- **Comfort:** seating, air conditioning, charging facilities and the passenger "
            "experience.\n\n"
            "**Feasibility**\n\n"
            "- **Deliverability:** whether the link can be delivered in a reasonable time "
            "and at a reasonable cost, and whether it will be used."
        )

    chart(
        qualitative_chart(
            LINK_SCORES,
            ["Reading", "Uxbridge", "Staines", "Woking"],
            "Average Qualitative Assessment Scores per Link",
            "Link",
        )
    )
    chart(
        qualitative_chart(
            FACTOR_SCORES,
            ["Accessibility", "Comfort", "Safety", "Deliverability"],
            "Average Qualitative Assessment Scores per Social and Feasibility Factor",
            "Factor",
        )
    )
    st.write(
        "The average assessments favour rail for Reading, Uxbridge and Woking, and "
        "trolleybus for Staines. Rail receives higher scores for accessibility, comfort "
        "and deliverability, while trolleybuses are rated more highly for safety. "
        "These scores also need to be considered alongside the requirement for "
        "24-hour employee access where rail services do not run around the clock."
    )
    st.write(
        "The Final Proposal brings the selected links together with the complementary "
        "services, park-and-ride and construction sequence."
    )


if __name__ == "__main__":
    main()
