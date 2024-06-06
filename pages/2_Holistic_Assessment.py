import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.sidebar.success("Select page above.")
#st.sidebar.image('images/logo.jpg', use_column_width=True)
st.title('Holistic Assessment :recycle:')
st.markdown("""This section of the dashboard aims to provide insight into how the changes proposed may impact the current network through:""")
st.markdown("""
            - Generalised Cost of Travel :dollar:
            - Travel Time Saved :watch:
            - Mode Shift :car: **>** :train: """)


heatmap = pd.read_excel('New_Routes_2024.xlsx').dropna()
heatmap = heatmap[~heatmap['Local Auth'].eq('South Holland')]
heatmap = heatmap[~heatmap['Local Auth'].eq('Angus')]

#chosen = st.selectbox(label = 'Compare the Generalised cost before and after proposals:', options=['GC Old Rail', 'GC New Rail'])

fig = go.Figure(data=go.Scattermapbox(
        lat=heatmap['lat'],
        lon=heatmap['lng'],
        showlegend=False,
        mode='markers',
        marker=dict(
            size=heatmap['GC Old Rail']-heatmap['GC New Rail'],
            color=heatmap['GC Old Rail']-heatmap['GC New Rail'],
            colorscale='Inferno',
            showscale = True,
            cmin = 0,
            cmax = (heatmap['GC Old Rail']-heatmap['GC New Rail']).max(),
            sizemode='area',
            sizeref= (heatmap['GC Old Rail']-heatmap['GC New Rail']).max()/50**2,
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
            zoom=7,
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




#time saved

fig2 = go.Figure(data=go.Scattermapbox(
        lat=heatmap['lat'],
        lon=heatmap['lng'],
        showlegend=False,
        mode='markers',
        marker=dict(
            size=heatmap['Rail time saved in minutes'],
            color=heatmap['Rail time saved in minutes'],
            colorscale='Inferno',
            showscale = True,
            cmin = 0,
            cmax = heatmap['Rail time saved in minutes'].max(),
            sizemode='area',
            sizeref= heatmap['Rail time saved in minutes'].max()/50**2,
            sizemin=1
        ),
        text=heatmap['Local Auth'],
        hovertemplate='%{text}<br>' +
                      'Time Saved in Minutes: %{marker.size}<br>' +
                      '<extra></extra>',
    ))

fig2.update_layout(
        title=f'Rail time saved in Minutes (Higher is better)',
        mapbox=dict(
            style='open-street-map',
            zoom=7,
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

st.plotly_chart(fig2)
st.plotly_chart(fig)