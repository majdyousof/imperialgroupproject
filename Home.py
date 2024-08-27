import streamlit as st
import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

def load_data():
    heatmap = pd.read_excel('heathrowflow.xlsx')
    heatmap = heatmap[~heatmap['Local Auth'].eq('South Holland')]
    heatmap = heatmap[~heatmap['Local Auth'].eq('Westminster')]
    heatmap['Mode Share Other'] = 1 - (heatmap['Mode Share Car'] + heatmap['Mode Share Taxi'] + heatmap['Mode Share Rail'])
    heatmap['Car Demand'] = heatmap['Total Annual Demand'].multiply(heatmap['Mode Share Car']).round()
    heatmap['Rail Demand'] = heatmap['Total Annual Demand'].multiply(heatmap['Mode Share Rail']).round()
    heatmap['Taxi Demand'] = heatmap['Total Annual Demand'].multiply(heatmap['Mode Share Taxi']).round()
    heatmap['Vehicle Demand'] = heatmap['Taxi Demand'] + heatmap['Car Demand']
    heatmap['Other'] = heatmap['Total Annual Demand'].multiply(heatmap['Mode Share Other']).round()
    heatmap['Car Travel minutes per km'] = (1/60) * heatmap['Car Time Taken [s]'].div(heatmap['Car Distance [m]'] / 1000)
    heatmap['Transit Travel minutes per km'] = (1/60) * heatmap['Transit Time Taken [s]'].div(heatmap['Transit Distance [m]'] / 1000)
    heatmap = heatmap.dropna()
    return heatmap

def create_scattermapbox(data, chosen, title):
    fig = go.Figure(data=go.Scattermapbox(
        lat=data['lat'],
        lon=data['lng'],
        showlegend=False,
        mode='markers',
        marker=dict(
            size=data[chosen],
            color=data[chosen],
            colorscale='Inferno',
            showscale=True,
            cmin=0,
            cmax=data['Total Annual Demand'].max(),
            sizemode='area',
            sizeref=0.4 * data['Total Annual Demand'].max() / 50**2,
            sizemin=1
        ),
        text=data['Local Auth'],
        hovertemplate='%{text}<br>' +
                      'Demand: %{marker.size}<br>' +
                      '<extra></extra>',
    ))

    fig.update_layout(
        title=f'{chosen} to Heathrow in 2019 (Source: ARUP)',
        mapbox=dict(
            style='open-street-map',
            zoom=7.5,
            center=dict(lat=51.470020, lon=-0.454295)
        ),
        height=400,  # Adjust the height for mobile devices
        legend=dict(y=0, x=0),
        margin=dict(l=0, r=0, t=30, b=0),
    )

    fig.add_scattermapbox(lat=[51.470020],
                          lon=[-0.454295],
                          marker=go.scattermapbox.Marker(
                              size=15,  # Adjust the size for mobile devices
                              color='black'),
                          name='',
                          showlegend=False
                          )

    fig.add_scattermapbox(lat=[51.470020],
                          lon=[-0.454295],
                          marker=go.scattermapbox.Marker(
                              size=12,  # Adjust the size for mobile devices
                              color='pink'),
                          name='Heathrow'
                          )

    fig.update_coloraxes(colorbar=dict(orientation='h', y=-0.15))

    return fig

def create_barchart(data):
    barchart = px.bar(data.sort_values('Total Annual Demand', ascending=False),
                      x='Local Auth',
                      y=['Car Demand', 'Taxi Demand', 'Rail Demand', 'Other'],
                      title='Total Annual trips and mode share per local authority INCLUDING London')

    return barchart

def main():
    st.title('Heathrow Trips: A review :book:')
    st.sidebar.success("Select page above.")

    heatmap = load_data()

    chosen = st.selectbox(label='Choose mode to compare demand:', options=['Total Annual Demand', 'Car Demand', 'Taxi Demand', 'Vehicle Demand', 'Rail Demand', 'Other'])
    fig = create_scattermapbox(heatmap, chosen, f'{chosen} to Heathrow in 2019 (Source: ARUP)')
    st.plotly_chart(fig, use_container_width=True)  # Use container width for mobile devices

    chosen2 = st.selectbox(label='Choose mode to compare travel time to distance ratio:', options=['Car Travel minutes per km', 'Transit Travel minutes per km'])
    fig2 = create_scattermapbox(heatmap, chosen2, f'{chosen2} to Heathrow (Source: Google Distance Matrix API)')
    st.plotly_chart(fig2, use_container_width=True)  # Use container width for mobile devices

    barchart = create_barchart(heatmap)
    st.plotly_chart(barchart, use_container_width=True)  # Use container width for mobile devices

if __name__ == "__main__":
    main()
