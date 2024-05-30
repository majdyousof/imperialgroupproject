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
    heatmap['Vehicle Demand'] = heatmap['Total Annual Demand'].multiply((heatmap['Mode Share Car']+heatmap['Mode Share Taxi'])).round()
    heatmap['Other'] = heatmap['Total Annual Demand'].multiply(heatmap['Mode Share Other']).round()

    chosen = st.selectbox(label = 'Choose mode:', options=['Total Annual Demand','Car Demand','Taxi Demand','Vehicle Demand','Rail Demand', 'Other'])

    fig = px.scatter_mapbox(
                            heatmap,
                            lat="lat",
                            lon="lng",
                            size=f"{chosen}",
                            hover_name="Local Auth",
                            hover_data=f"{chosen}",
                            size_max=50,
                            zoom=5,
                            mapbox_style="open-street-map",
                            color=f"{chosen}",
                            color_continuous_scale=px.colors.cyclical.IceFire
                            )
    
    fig.update_layout(title = f'{chosen} to Heathrow in 2019',
                      height = 600,
                      width = 1000)
    
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

    st.plotly_chart(fig)

if __name__ == "__main__":
    main()