import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.sidebar.success("Select page above.")
st.sidebar.image('\images\logo.jpg', use_column_width='always')
st.title('Link-to-Link Quantitative Assessment :train:')

st.markdown(""" This page of the dashboard aims to assess
            a select number of links to work out the year
            when the implementations of the different 
            transportation modes break even. :chart:""")

st.markdown("""
            *The different links include:*
            - Heathrow **>** Iver
            - Heathrow **>** Uxbridge
            - Heathrow **>** Staines
            - Heathrow **>** Woking
            """)

# data import
iver = pd.read_excel('train.xlsx',sheet_name='Iver',header=None)
woking = pd.read_excel('train.xlsx',sheet_name='Woking',header=None)
uxbridge = pd.read_excel('train.xlsx',sheet_name='Uxbridge',header=None)
staines = pd.read_excel('train.xlsx',sheet_name='Staines',header=None)

# arrays needed for plotting
year = np.arange(2025,2051)
poppercent = np.arange(1,101)


linkoption = st.sidebar.selectbox('*Select Link for comparison:*',
                                    options=['Heathrow-Iver',
                                            'Heathrow-Uxbridge',
                                            'Heathrow-Staines',
                                            'Heathrow-Woking'])

percentage_val = st.select_slider("*Select percentage [%] of Heathrow passengers expected to use link:*",
                                  value = 50,
                                  options = poppercent)

if linkoption == 'Heathrow-Iver':

    fig = px.line(x = year, 
                y = iver[percentage_val-1],
                title = f"{linkoption}")
    fig.update_layout(yaxis_range=[iver.min().min(),iver.max().max()])

    #3d plot
    fig2 = go.Figure(data=[go.Surface(z=iver,y=year,x=poppercent)])
    fig2.update_layout(title=f"{linkoption} total surface plot", autosize=False,
                  yaxis_range=[0,100])
    
elif linkoption == 'Heathrow-Uxbridge':
    fig = px.line(x = year, 
                y = uxbridge[percentage_val-1],
                title = f"{linkoption}")
    fig.update_layout(yaxis_range=[uxbridge.min().min(),uxbridge.max().max()])

    #3d plot
    fig2 = go.Figure(data=[go.Surface(z=uxbridge,y=year,x=poppercent)])
    fig2.update_layout(title=f"{linkoption} total surface plot", autosize=False,
                  margin=dict(l=65, r=50, b=65, t=90))
    
elif linkoption == 'Heathrow-Staines':
    fig = px.line(x = year, 
                y = staines[percentage_val-1],
                title = f"{linkoption}")
    fig.update_layout(yaxis_range=[staines.min().min(),staines.max().max()])

    #3d plot
    fig2 = go.Figure(data=[go.Surface(z=staines,y=year,x=poppercent)])
    fig2.update_layout(title=f"{linkoption} total surface plot", autosize=False,
                  margin=dict(l=65, r=50, b=65, t=90))
    
elif linkoption == 'Heathrow-Woking':
    fig = px.line(x = year, 
                y = woking[percentage_val-1],
                title = f"{linkoption}")
    fig.update_layout(yaxis_range=[woking.min().min(),woking.max().max()])

    #3d plot
    fig2 = go.Figure(data=[go.Surface(z=woking,y=year,x=poppercent)])
    fig2.update_layout(title=f"{linkoption} total surface plot", autosize=False,
                  margin=dict(l=65, r=50, b=65, t=90))

fig.add_hline(y=0,
              line_color = 'red',
              line_dash = 'dash')

fig.update_layout(
                    xaxis_title='Year',
                    yaxis_title='Earnings [£ million]')

fig2.update_layout(
    margin=dict(l=10, r=10, t=20, b=20),
    scene = dict(
                    xaxis_title='Percentage of Heathrow passengers using link [%]',
                    yaxis_title='Years',
                    zaxis_title='Earnings [£ million]'))


plotter = st.plotly_chart(fig)
plotter2 = st.plotly_chart(fig2)
