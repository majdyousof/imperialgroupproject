import streamlit as st
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def main():
    # Set the title and layout of the dashboard
    st.title('Heathrow Trips: A review :book:')
    st.sidebar.success("Select page above.")
    st.sidebar.image('images/logo.jpg', use_column_width='always')

    heatmap = pd.read_excel('heathrowflow.xlsx')

    heatmap['Mode Share Other'] = 1-(heatmap['Mode Share Car']+heatmap['Mode Share Taxi']+heatmap['Mode Share Rail'])

    heatmap['Car Demand'] = heatmap['Total Annual Demand'].multiply(heatmap['Mode Share Car']).round()
    heatmap['Rail Demand'] = heatmap['Total Annual Demand'].multiply(heatmap['Mode Share Rail']).round()
    heatmap['Taxi Demand'] = heatmap['Total Annual Demand'].multiply(heatmap['Mode Share Taxi']).round()
    heatmap['Vehicle Demand'] = heatmap['Taxi Demand']+heatmap['Car Demand']
    heatmap['Other'] = heatmap['Total Annual Demand'].multiply(heatmap['Mode Share Other']).round()

    chosen = st.selectbox(label = 'Choose mode:', options=['Total Annual Demand','Car Demand','Taxi Demand','Vehicle Demand','Rail Demand', 'Other'])

    fig = go.Figure(data=go.Scattermapbox(
        lat=heatmap['lat'],
        lon=heatmap['lng'],
        showlegend=False,
        mode='markers',
        marker=dict(
            size=heatmap[chosen],
            color=heatmap[chosen],
            colorscale='Inferno',
            sizemode='area',
            sizeref= 0.5*heatmap['Total Annual Demand'].max()/50**2,
            sizemin=1
        ),
        text=heatmap['Local Auth'],
        hovertemplate='%{text}<br>' +
                      'Demand: %{marker.size}<br>' +
                      '<extra></extra>'
    ))

    fig.update_layout(
        title=f'{chosen} to Heathrow in 2019',
        mapbox=dict(
            style='open-street-map',
            zoom=7.5,
            center=dict(lat=51.470020, lon=-0.454295)
        ),
        height=600,
        legend=dict(y=0, x=0),
        margin=dict(l=0, r=0, t=30, b=0),
    )

    
    fig.add_scattermapbox(lat=[51.470020],
                          lon =[-0.454295],
                          marker=go.scattermapbox.Marker(
                                                        size=25,
                                                        color='purple'),
                            name='',
                            showlegend=False
    )
    
    fig.add_scattermapbox(lat=[51.470020],
                          lon =[-0.454295],
                          marker=go.scattermapbox.Marker(
                                                        size=18,
                                                        color='pink'),
                            name='Heathrow'
    )

    fig.update_coloraxes(colorbar = dict(orientation = 'h', y = -0.15))

    barchart = px.bar(heatmap.sort_values('Total Annual Demand', ascending= False),
                       x = 'Local Auth',
                       y = ['Car Demand','Taxi Demand','Rail Demand', 'Other'],
                       title = 'Total Annual trips and mode share per local authority INCLUDING London')

    st.plotly_chart(fig)
    st.plotly_chart(barchart)

if __name__ == "__main__":
    main()