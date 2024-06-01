import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#st.set_page_config(layout="wide")

st.sidebar.success("Select page above.")
#st.sidebar.image('images/logo.jpg', use_column_width='always')
st.title('Link-to-Link Quantitative Assessment :train:')

st.markdown(""" This page of the dashboard aims to assess
            a select number of links to work out the year
            when the implementations of the different 
            transportation modes break even. :chart:""")

st.markdown("""
            *The different links include:*
            - Heathrow **>** Reading
            - Heathrow **>** Uxbridge
            - Heathrow **>** Staines
            - Heathrow **>** Woking
            """)

st.markdown("""
Toggle between link options using the **dropdown menu** in the **sidebar**.
""")

# arrays needed for plotting
year = np.arange(2025,2101)
poppercent = np.arange(1,101)
multipliers = np.arange(50,201,5)


linkoption = st.selectbox('*Select link for comparison:*',
                                    options=['Heathrow-Reading',
                                             'Heathrow-Woking',
                                            'Heathrow-Uxbridge',
                                            'Heathrow-Staines',])

percentage_val = st.select_slider("*Select percentage [%] of total Heathrow passenger demand on link:*",
                                  value = 20,
                                  options = poppercent)

multval = st.select_slider("*Select cost multiplier [%]:*",
                                  value = 100,
                                  options = multipliers)

val1 = str(int(multval/100))[0]
#Data import

if multval == 200 or multval == 100:
    reading = pd.read_excel('data/readingtrain.xlsx',sheet_name=val1,header=None)
    woking = pd.read_excel('data/wokingtrain.xlsx',sheet_name=val1,header=None)
    uxbridge = pd.read_excel('data/uxbridgetrain.xlsx',sheet_name=val1,header=None)
    staines = pd.read_excel('data/stainestrain.xlsx',sheet_name=val1,header=None)

    readingtr = pd.read_excel('data/readingtrolley.xlsx',sheet_name=val1,header=None)
    wokingtr = pd.read_excel('data/wokingtrolley.xlsx',sheet_name=val1,header=None)
    uxbridgetr = pd.read_excel('data/uxbridgetrolley.xlsx',sheet_name=val1,header=None)
    stainestr = pd.read_excel('data/stainestrolley.xlsx',sheet_name=val1,header=None)
else:
    reading = pd.read_excel('data/readingtrain.xlsx',sheet_name=str(multval/100),header=None)
    woking = pd.read_excel('data/wokingtrain.xlsx',sheet_name=str(multval/100),header=None)
    uxbridge = pd.read_excel('data/uxbridgetrain.xlsx',sheet_name=str(multval/100),header=None)
    staines = pd.read_excel('data/stainestrain.xlsx',sheet_name=str(multval/100),header=None)

    readingtr = pd.read_excel('data/readingtrolley.xlsx',sheet_name=str(multval/100),header=None)
    wokingtr = pd.read_excel('data/wokingtrolley.xlsx',sheet_name=str(multval/100),header=None)
    uxbridgetr = pd.read_excel('data/uxbridgetrolley.xlsx',sheet_name=str(multval/100),header=None)
    stainestr = pd.read_excel('data/stainestrolley.xlsx',sheet_name=str(multval/100),header=None)

if linkoption == 'Heathrow-Reading':

    fig = go.Figure()
    fig.add_trace(go.Scatter(x = year, y = reading[percentage_val-1], 
                             mode='lines',
                             name='Rail solution'))
    
    fig.add_trace(go.Scatter(x = year, y = readingtr[percentage_val-1],
                             mode='lines',
                             name='Trolley Bus solution'))
    
    fig.update_layout(yaxis_range=[min(reading[percentage_val-1].min().min(),readingtr[percentage_val-1].min().min()),
                                   max(reading[percentage_val-1].max().max(),readingtr[percentage_val-1].max().max())])

    #3d plot
    fig2 = make_subplots(rows=1,cols=2, specs=[[{'type': 'surface'}, {'type': 'surface'}]],
                         subplot_titles=('Rail solution','Trolley Bus solution'),
                         horizontal_spacing=0.01,
                         vertical_spacing=0.1)
    fig2.add_trace(go.Surface(z=reading,y=year,x=poppercent,name='Rail Solution', showscale=False), row=1,col=1)
    fig2.add_trace(go.Surface(z=readingtr,y=year,x=poppercent,name='Trolley Bus Solution', showscale=False), row=1,col=2)

    
elif linkoption == 'Heathrow-Uxbridge':
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = year, y = uxbridge[percentage_val-1], 
                             mode='lines',
                             name='Rail solution'))
    
    fig.add_trace(go.Scatter(x = year, y = uxbridgetr[percentage_val-1],
                             mode='lines',
                             name='Trolley Bus solution'))
    
    fig.update_layout(yaxis_range=[min(uxbridge[percentage_val-1].min().min(),uxbridgetr[percentage_val-1].min().min()),
                                       max(uxbridge[percentage_val-1].max().max(),uxbridgetr[percentage_val-1].max().max())])

    #3d plot
    fig2 = make_subplots(rows=1,cols=2, specs=[[{'type': 'surface'}, {'type': 'surface'}]],
                         subplot_titles=('Rail solution','Trolley Bus solution'),
                         horizontal_spacing=0.01,
                         vertical_spacing=0.1)
    fig2.add_trace(go.Surface(z=uxbridge,y=year,x=poppercent,name='Rail Solution', showscale=False), row=1,col=1)
    fig2.add_trace(go.Surface(z=uxbridgetr,y=year,x=poppercent,name='Trolley Bus Solution', showscale=False), row=1,col=2)

    
elif linkoption == 'Heathrow-Staines':
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = year, y = staines[percentage_val-1], 
                             mode='lines',
                             name='Rail solution'))
    
    fig.add_trace(go.Scatter(x = year, y = stainestr[percentage_val-1],
                             mode='lines',
                             name='Trolley Bus solution'))
    
    fig.update_layout(yaxis_range=[min(staines[percentage_val-1].min().min(),stainestr[percentage_val-1].min().min()),
                                   max(staines[percentage_val-1].max().max(),stainestr[percentage_val-1].max().max())])

    #3d plot
    fig2 = make_subplots(rows=1,cols=2, specs=[[{'type': 'surface'}, {'type': 'surface'}]],
                         subplot_titles=('Rail solution','Trolley Bus solution'),
                         horizontal_spacing=0.01,
                         vertical_spacing=0.1)
    fig2.add_trace(go.Surface(z=staines,y=year,x=poppercent,name='Rail Solution', showscale=False), row=1,col=1)
    fig2.add_trace(go.Surface(z=stainestr,y=year,x=poppercent,name='Trolley Bus Solution', showscale=False), row=1,col=2)

    
elif linkoption == 'Heathrow-Woking':
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = year, y = woking[percentage_val-1], 
                             mode='lines',
                             name='Rail solution'))
    
    fig.add_trace(go.Scatter(x = year, y = wokingtr[percentage_val-1],
                             mode='lines',
                             name='Trolley Bus solution'))
    
    fig.update_layout(yaxis_range=[min(woking[percentage_val-1].min().min(),wokingtr[percentage_val-1].min().min()),
                                   max(woking[percentage_val-1].max().max(),wokingtr[percentage_val-1].max().max())])
    
    #3d plot
    fig2 = make_subplots(rows=1,cols=2, specs=[[{'type': 'surface'}, {'type': 'surface'}]],
                         subplot_titles=('Rail solution','Trolley Bus solution'),
                         horizontal_spacing=0.01,
                         vertical_spacing=0.1)
    fig2.add_trace(go.Surface(z=woking,y=year,x=poppercent,name='Rail Solution', showscale=False), row=1,col=1)
    fig2.add_trace(go.Surface(z=wokingtr,y=year,x=poppercent,name='Trolley Bus Solution', showscale=False), row=1,col=2)


fig.add_hline(y=0,
              line_color = 'red',
              line_dash = 'dash')

fig.update_layout(xaxis_title='Year',
                  yaxis_title='Total Earnings [£ million]',
                  title = f"{linkoption} Mode comparison for {percentage_val}% share of total Heathrow passengers",
                  legend = dict(
                      title = 'Mode type:'
                  ))

fig2.update_layout(
    margin=dict(l=0, r=0, t=20, b=10),
    scene1 = dict(
                    xaxis_title='Heathrow passengers using link [%]',
                    yaxis_title='Years',
                    zaxis_title='Total Earnings [£ million]',),
    scene2 = dict(
                    xaxis_title='Heathrow passengers using link [%]',
                    yaxis_title='Years',
                    zaxis_title='Total Earnings [£ million]'))


fig2.layout.scene1.camera.eye=dict(x=0, y=15, z=2)
fig2.layout.scene2.camera.eye=dict(x=0, y=15, z=2)

fig2.layout.scene1.aspectratio=dict(x=4, y=4, z=6)
fig2.layout.scene2.aspectratio=dict(x=4, y=4, z=6)

plotter = st.plotly_chart(fig)
st.markdown(f"**{linkoption} Surface plots for both modes -** *feel free to rotate charts*")
plotter2 = st.plotly_chart(fig2,use_container_width=True)
