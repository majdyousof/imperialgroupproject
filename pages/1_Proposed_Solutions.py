"""Introduce the rail and trolleybus alternatives before the link-to-link assessment."""

import streamlit as st

from heathrow.ui import page


def main() -> None:
    page("Proposed Solutions")
    st.write(
        "To improve the connections identified in the initial analysis, two modes of "
        "transport are considered: extensions of the existing rail network and the introduction of a trolleybus service. This is done for each of our identified links."
    )

    st.subheader("Links considered for assessment")
    st.table(
        [
            {
                "Link to Heathrow": "Reading",
                "Purpose of the connection": "Improve access from the west, including Maidenhead and Slough.",
                "Rail alternative": "Elizabeth Line extension",
            },
            {
                "Link to Heathrow": "Uxbridge (Hillingdon)",
                "Purpose of the connection": "Connect Uxbridge and improve access from north-west London.",
                "Rail alternative": "Piccadilly Line extension",
            },
            {
                "Link to Heathrow": "Woking",
                "Purpose of the connection": "Connect Heathrow to the South Western Railway hub serving the South of England.",
                "Rail alternative": "Heathrow Express extension",
            },
            {
                "Link to Heathrow": "Staines (Spelthorne)",
                "Purpose of the connection": "Improve access from the Waterloo rail network, including Richmond and Hounslow.",
                "Rail alternative": "Heathrow Express extension",
            },
        ]
    )
    st.subheader("Rail Network Expansion")
    st.write(
        "Extending the existing rail network would allow a greater number of passengers "
        "to travel to Heathrow without adding vehicles to the surrounding roads. Additionally, trains "
        "have a higher passenger capacity than trolleybuses and operate on dedicated "
        "tracks, which makes them less affected by road congestion. This is particularly "
        "relevant for links with high demand, where capacity and reliability are "
        "important considerations for passengers travelling to the airport."
    )
    st.write(
        "However, rail requires a higher initial investment, and the construction of "
        "new tracks, tunnels and station infrastructure can disrupt existing services. "
        "The proposed extensions therefore need to consider how they integrate with "
        "the current network, as well as their speed and efficiency, capacity, "
        "reliability and punctuality, and passenger comfort."
    )

    st.subheader("Trolleybuses")
    st.write(
        "Trolleybuses provide an alternative which can use the existing road network, "
        "requiring less initial investment than new railway infrastructure; this makes "
        "them worth considering for shorter connections and smaller locations where "
        "the demand may not justify a rail link. In-Motion Charging would allow the "
        "vehicles to charge while travelling under overhead wires and use batteries "
        "on the remaining sections, reducing the length of route that needs to be wired."
    )
    st.write(
        "A 24-hour trolleybus service would also address the need for travel during "
        "unsociable hours, particularly for employees and passengers with night flights. "
        "However, the suitability of each route depends on passenger capacity and the "
        "availability of bus lanes. Where dedicated lanes cannot be provided, road "
        "congestion could affect journey times, so the feasibility of road alterations "
        "must also be considered."
    )

    st.write(
        "The Link-to-link Assessment compares the two alternatives to select a mode "
        "for each connection."
    )


if __name__ == "__main__":
    main()
