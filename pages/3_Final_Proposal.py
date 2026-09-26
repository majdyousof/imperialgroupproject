"""Explain the final surface-access proposal developed in the 2024 coursework."""

import streamlit as st

from heathrow.paths import IMAGES
from heathrow.ui import page


def main() -> None:
    page("Final Proposal")
    st.write(
        "The final proposal combines three rail extensions for longer-distance journeys "
        "with two trolleybus routes for local and 24-hour access, and a park-and-ride at Langley."
    )
    st.image(
        str(IMAGES / "proposed-network.jpg"),
        caption="Final routes for trolleybus and train routes",
        use_column_width=True,
    )

    st.subheader("Final Summary of Links and Modes")
    st.table(
        [
            {
                "Proposed link": "Reading > Heathrow",
                "Mode": "Elizabeth Line extension",
            },
            {
                "Proposed link": "Uxbridge > Heathrow",
                "Mode": "Piccadilly Line extension",
            },
            {
                "Proposed link": "Woking > Heathrow",
                "Mode": "Heathrow Express extension",
            },
            {
                "Proposed link": "Heathrow > Staines / Ashford / Thorpe Park",
                "Mode": "Trolleybus",
            },
            {
                "Proposed link": "Heathrow > Slough > Maidenhead",
                "Mode": "Trolleybus",
            },
        ]
    )
    st.caption(
        "These are the final project selections. Changing the Link-to-link Assessment "
        "sliders explores alternative assumptions; it does not change this proposal."
    )

    st.subheader("Rail Network Expansion")
    st.markdown("**Elizabeth Line extension from Reading**")
    st.write(
        "The proposed extension connects Reading to Heathrow via Maidenhead and Slough. "
        "A new connection branches south at Iver towards Heathrow Terminal 5. "
        "At the initial 10% passenger share and 100% cost multiplier, the rail solution "
        "has higher initial costs but greater earnings over time than the trolleybus "
        "alternative. Rail does not run 24/7, so the proposal also includes a "
        "complementary trolleybus service from Maidenhead and Slough."
    )
    st.markdown("**Piccadilly Line extension from Uxbridge**")
    st.write(
        "The proposed extension connects Uxbridge directly to Heathrow, creating a loop "
        "in the Piccadilly Line, with the new connection running via Iver to Terminal 5. "
        "New underground platforms are proposed at Uxbridge, while Metropolitan Line "
        "services continue to terminate at the existing surface platforms. "
        "Rail is selected for its capacity and greater long-term earnings, supported "
        "by the qualitative assessment."
    )
    st.markdown("**Heathrow Express extension to Woking**")
    st.write(
        "Woking provides connections to the South of England through the South Western "
        "Railway network. The proposed Heathrow Express extension connects Terminal 5 "
        "to this network. Rail is selected for its capacity and greater long-term earnings. "
        "The lack of space for suitable bus lanes at Woking also limits the trolleybus "
        "alternative, which would otherwise be slowed by road traffic."
    )

    st.subheader("Trolleybuses")
    st.image(
        str(IMAGES / "proposed-trolleybus-routes.jpg"),
        caption="Final trolleybus routes and proposed stops",
        width=793,
    )
    st.markdown("**Staines, Ashford and Thorpe Park**")
    st.write(
        "The proposed Heathrow Express extension to Staines is replaced by a trolleybus "
        "connection serving Staines Station, with connections to Ashford and Thorpe Park. "
        "For this shorter link, the trolleybus solution reaches break-even substantially "
        "earlier than rail in the initial comparison. The qualitative assessment also "
        "favours trolleybus for Staines."
    )
    st.markdown("**Maidenhead, Slough and Langley park-and-ride**")
    st.write(
        "A complementary route serves Maidenhead, Slough, Langley Car Park and Brands Hill. "
        "It is proposed to operate 24/7, providing access for employees and passengers "
        "with night flights when the rail service is not running. Existing bus lanes "
        "reduce the amount of new infrastructure required. Langley Car Park allows "
        "passengers to park away from Heathrow and complete their journey by trolleybus."
    )
    st.markdown("**In-Motion Charging (IMC)**")
    st.write(
        "Overhead wires are proposed along selected bus-lane sections and Stanwell Moor "
        "Road, limiting installation in residential areas. In-Motion Charging allows "
        "battery operation elsewhere without charging breaks."
    )

    with st.expander("Construction sequence"):
        st.write(
            "The Staines and Ashford trolleybus connections are proposed first, followed "
            "by the Maidenhead route, to limit simultaneous construction around Slough "
            "and Maidenhead during the Elizabeth Line works."
        )
        st.markdown(
            "The trainline roadmap has four phases:\n\n"
            "1. Increase capacity between Reading and Iver for additional Elizabeth Line services.\n"
            "2. Construct the Elizabeth and Piccadilly Line connections between Iver "
            "and Heathrow Terminal 5.\n"
            "3. Complete the Piccadilly Line extension between Iver and Uxbridge.\n"
            "4. Construct the Heathrow Express extension between Terminal 5 and Woking."
        )

    with st.expander("Development of the final proposal"):
        st.write(
            "The proposed new station at Iver was removed because there was insufficient "
            "demand evidence to justify it and an additional stop would slow the rail "
            "extensions. The rail connection at Iver remains part of the scheme. "
            "The Iver park-and-ride proposal was replaced by Langley."
        )
        st.write(
            "A floating car park on King George VI Reservoir was also considered and "
            "discontinued. Risks to drinking-water quality, construction and maintenance "
            "costs, and its limited contribution to improving surface access outweighed "
            "its potential benefits."
        )

    st.write(
        "The Holistic Assessment compares journey times and Generalised Cost of Travel "
        "with the four hub connections in place."
    )


if __name__ == "__main__":
    main()
