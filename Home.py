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
    #st.sidebar.image('images/logo.jpg', use_column_width='always')

    heatmap = pd.read_excel('heathrowflow.xlsx')

    heatmap['Mode Share Other'] = 1-(heatmap['Mode Share Car']+heatmap['Mode Share Taxi']+heatmap['Mode Share Rail'])

    heatmap['Car Demand'] = heatmap['Total Annual Demand'].multiply(heatmap['Mode Share Car']).round()
    heatmap['Rail Demand'] = heatmap['Total Annual Demand'].multiply(heatmap['Mode Share Rail']).round()
    heatmap['Taxi Demand'] = heatmap['Total Annual Demand'].multiply(heatmap['Mode Share Taxi']).round()
    heatmap['Vehicle Demand'] = heatmap['Taxi Demand']+heatmap['Car Demand']
    heatmap['Other'] = heatmap['Total Annual Demand'].multiply(heatmap['Mode Share Other']).round()

    heatmap['Car Travel minutes per km'] = (1/60)*heatmap['Car Time Taken [s]'].div(heatmap['Car Distance [m]']/1000)
    heatmap['Transit Travel minutes per km'] = (1/60)*heatmap['Transit Time Taken [s]'].div(heatmap['Transit Distance [m]']/1000)
    heatmap2 = heatmap.dropna()

    chosen = st.selectbox(label = 'Choose mode to compare demand:', options=['Total Annual Demand','Car Demand','Taxi Demand','Vehicle Demand','Rail Demand', 'Other'])

    fig = go.Figure(data=go.Scattermapbox(
        lat=heatmap['lat'],
        lon=heatmap['lng'],
        showlegend=False,
        mode='markers',
        marker=dict(
            size=heatmap[chosen],
            color=heatmap[chosen],
            colorscale='Inferno',
            showscale = True,
            cmin = 0,
            cmax = heatmap['Total Annual Demand'].max(),
            sizemode='area',
            sizeref= 0.5*heatmap['Total Annual Demand'].max()/50**2,
            sizemin=1
        ),
        text=heatmap['Local Auth'],
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
        height=600,
        legend=dict(y=0, x=0),
        margin=dict(l=0, r=0, t=30, b=0),
    )

    
    fig.add_scattermapbox(lat=[51.470020],
                          lon =[-0.454295],
                          marker=go.scattermapbox.Marker(
                                                        size=25,
                                                        color='black'),
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

    fig.update_coloraxes(colorbar = dict(orientation = 'h', y = -0.15,))



    st.plotly_chart(fig)


    chosen2 = st.selectbox(label = 'Choose mode to compare travel time to distance ratio:', options=['Car Travel minutes per km','Transit Travel minutes per km'])

    fig2 = go.Figure(data=go.Scattermapbox(
        lat=heatmap2['lat'],
        lon=heatmap2['lng'],
        showlegend=False,
        mode='markers',
        marker=dict(
            size=heatmap2[chosen2],
            color=heatmap2[chosen2],
            colorscale='Inferno',
            showscale = True,
            
            cmin = 0,
            cmax = max(heatmap2['Transit Travel minutes per km'].max(),heatmap2['Car Travel minutes per km'].max())-15,
            sizemode='area',
            sizeref= max(heatmap2['Transit Travel minutes per km'].max(),heatmap2['Car Travel minutes per km'].max())/50**2,
            sizemin=1
        ),
        text=heatmap2['Local Auth'],
        hovertemplate='%{text}<br>' +
                      'Minutes/Kilometer ratio: %{marker.size}<br>' +
                      '<extra></extra>',
    ))

    fig2.update_layout(
        title=f'{chosen2} to Heathrow (Source: Google Distance Matrix API)',
        mapbox=dict(
            style='open-street-map',
            zoom=7.5,
            center=dict(lat=51.470020, lon=-0.454295)
        ),
        height=600,
        legend=dict(y=0, x=0),
        margin=dict(l=0, r=0, t=30, b=0),
    )

    fig2.add_scattermapbox(lat=[51.470020],
                          lon =[-0.454295],
                          marker=go.scattermapbox.Marker(
                                                        size=25,
                                                        color='black'),
                            name='',
                            showlegend=False
    )
    
    fig2.add_scattermapbox(lat=[51.470020],
                          lon =[-0.454295],
                          marker=go.scattermapbox.Marker(
                                                        size=18,
                                                        color='pink'),
                            name='Heathrow'
    )

    fig2.update_coloraxes(colorbar = dict(orientation = 'h', y = -0.15))

    st.plotly_chart(fig2)


    barchart = px.bar(heatmap.sort_values('Total Annual Demand', ascending= False),
                    x = 'Local Auth',
                    y = ['Car Demand','Taxi Demand','Rail Demand', 'Other'],
                    title = 'Total Annual trips and mode share per local authority INCLUDING London')

    st.plotly_chart(barchart)

if __name__ == "__main__":
    main()