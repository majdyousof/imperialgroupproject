import streamlit as st
import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

def load_data():
    heatmap = pd.read_excel('New_Routes_2024.xlsx').dropna()
    heatmap = heatmap[~heatmap['Local Auth'].eq('South Holland')]
    heatmap = heatmap[~heatmap['Local Auth'].eq('Angus')]
    return heatmap

def create_generalised_cost_map(heatmap):
    fig = go.Figure(data=go.Scattermapbox(
        lat=heatmap['lat'],
        lon=heatmap['lng'],
        showlegend=False,
        mode='markers',
        marker=dict(
            size=heatmap['GC Old Rail'] - heatmap['GC New Rail'],
            color=heatmap['GC Old Rail'] - heatmap['GC New Rail'],
            colorscale='Inferno',
            showscale=True,
            cmin=0,
            cmax=(heatmap['GC Old Rail'] - heatmap['GC New Rail']).max(),
            sizemode='area',
            sizeref=(heatmap['GC Old Rail'] - heatmap['GC New Rail']).max() / 50 ** 2,
            sizemin=1
        ),
        text=heatmap['Local Auth'],
        hovertemplate='%{text}<br>' +
                      'Change in Generalised Cost of Travel: %{marker.size}<br>' +
                      '<extra></extra>',
    ))

    fig.update_layout(
        title=f'Change in Generalised Cost of Travel: Rail (Higher is better)',
        mapbox=dict(
            style='open-street-map',
            zoom=6,
            center=dict(lat=51.470020, lon=-0.454295)
        ),
        height=400,
        legend=dict(y=0, x=0),
        margin=dict(l=0, r=0, t=30, b=0),
    )

    fig.add_scattermapbox(lat=[51.470020],
                          lon=[-0.454295],
                          marker=go.scattermapbox.Marker(
                              size=15,
                              color='black'),
                          name='',
                          showlegend=False
                          )

    fig.add_scattermapbox(lat=[51.470020],
                          lon=[-0.454295],
                          marker=go.scattermapbox.Marker(
                              size=12,
                              color='pink'),
                          name='Heathrow'
                          )

    return fig

def create_time_saved_map(heatmap):
    fig = go.Figure(data=go.Scattermapbox(
        lat=heatmap['lat'],
        lon=heatmap['lng'],
        showlegend=False,
        mode='markers',
        marker=dict(
            size=heatmap['Rail time saved in minutes'],
            color=heatmap['Rail time saved in minutes'],
            colorscale='Inferno',
            showscale=True,
            cmin=0,
            cmax=heatmap['Rail time saved in minutes'].max(),
            sizemode='area',
            sizeref=heatmap['Rail time saved in minutes'].max() / 50 ** 2,
            sizemin=1
        ),
        text=heatmap['Local Auth'],
        hovertemplate='%{text}<br>' +
                      'Time Saved in Minutes: %{marker.size}<br>' +
                      '<extra></extra>',
    ))

    fig.update_layout(
        title=f'Rail time saved in Minutes (Higher is better)',
        mapbox=dict(
            style='open-street-map',
            zoom=6,
            center=dict(lat=51.470020, lon=-0.454295)
        ),
        height=400,
        legend=dict(y=0, x=0),
        margin=dict(l=0, r=0, t=30, b=0),
    )

    fig.add_scattermapbox(lat=[51.470020],
                          lon=[-0.454295],
                          marker=go.scattermapbox.Marker(
                              size=15,
                              color='black'),
                          name='',
                          showlegend=False
                          )

    fig.add_scattermapbox(lat=[51.470020],
                          lon=[-0.454295],
                          marker=go.scattermapbox.Marker(
                              size=12,
                              color='pink'),
                          name='Heathrow'
                          )

    return fig

def main():
    st.sidebar.success("Select page above.")
    st.title('Holistic Assessment :recycle:')
    st.markdown("""This section of the dashboard aims to provide insight into how the changes proposed may impact the current network through:""")
    st.markdown("""
                - Generalised Cost of Travel :dollar:
                - Travel Time Saved :watch:
                - Mode Shift :car: **>** :train: """)

    heatmap = load_data()

    fig_generalised_cost = create_generalised_cost_map(heatmap)
    fig_time_saved = create_time_saved_map(heatmap)

    st.plotly_chart(fig_time_saved, use_container_width=True)
    st.plotly_chart(fig_generalised_cost, use_container_width=True)

if __name__ == '__main__':
    main()
