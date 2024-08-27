import streamlit as st
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(layout="wide")  # Set the layout to wide

st.sidebar.success("Select page above.")
st.title('Link-to-Link Quantitative Assessment :train:')

st.markdown(""" This page of the dashboard aims to assess
            a select number of links to work out the year
            when the implementations of the different 
            transportation modes break even. Scroll down to view the qualitative assessment as well. :chart:""")

st.markdown("""*The different links include:*
            - Heathrow **>** Reading
            - Heathrow **>** Uxbridge
            - Heathrow **>** Staines
            - Heathrow **>** Woking""")

st.markdown("""Toggle between link options using the **dropdown menu** in the **sidebar**.""")

year = np.arange(2025, 2101)
poppercent = np.arange(1, 101)
multipliers = np.arange(50, 201, 5)

linkoption = st.selectbox('*Select link for comparison:*',
                          options=['Heathrow-Reading',
                                   'Heathrow-Woking',
                                   'Heathrow-Uxbridge',
                                   'Heathrow-Staines'])

percentage_val = st.select_slider("*Select percentage [%] of total Heathrow passenger demand on link:*",
                                  value=20,
                                  options=poppercent)

multval = st.select_slider("*Select cost multiplier [%]:*",
                           value=100,
                           options=multipliers)

val1 = str(int(multval / 100))[0]

# Data import
data_files = {
    'reading': 'readingtrain.xlsx',
    'woking': 'wokingtrain.xlsx',
    'uxbridge': 'uxbridgetrain.xlsx',
    'staines': 'stainestrain.xlsx',
    'readingtr': 'readingtrolley.xlsx',
    'wokingtr': 'wokingtrolley.xlsx',
    'uxbridgetr': 'uxbridgetrolley.xlsx',
    'stainestr': 'stainestrolley.xlsx'
}

if multval == 200 or multval == 100:
    data = {key: pd.read_excel(f'data/{filename}', sheet_name=val1, header=None)
            for key, filename in data_files.items()}
else:
    data = {key: pd.read_excel(f'data/{filename}', sheet_name=str(multval / 100), header=None)
            for key, filename in data_files.items()}

fig = go.Figure()
fig.add_trace(go.Scatter(x=year, y=data['reading'][percentage_val - 1],
                         mode='lines',
                         name='Rail solution',
                         marker=dict(color='purple')))

fig.add_trace(go.Scatter(x=year, y=data['readingtr'][percentage_val - 1],
                         mode='lines',
                         name='Trolley Bus solution',
                         marker=dict(color='darkorange')))

fig.update_layout(yaxis_range=[min(data['reading'][percentage_val - 1].min().min(), data['readingtr'][percentage_val - 1].min().min()),
                               max(data['reading'][percentage_val - 1].max().max(), data['readingtr'][percentage_val - 1].max().max())])

fig2 = make_subplots(rows=1, cols=2, specs=[[{'type': 'surface'}, {'type': 'surface'}]],
                     subplot_titles=('Rail solution', 'Trolley Bus solution'),
                     horizontal_spacing=0.01,
                     vertical_spacing=0.1)
fig2.add_trace(go.Surface(z=data['reading'], y=year, x=poppercent, name='Rail Solution', showscale=False, colorscale='inferno'), row=1, col=1)
fig2.add_trace(go.Surface(z=data['readingtr'], y=year, x=poppercent, name='Trolley Bus Solution', showscale=False, colorscale='inferno'), row=1, col=2)

if linkoption == 'Heathrow-Reading':
    data = {
        'rail': data['reading'],
        'trolley': data['readingtr']
    }
elif linkoption == 'Heathrow-Uxbridge':
    data = {
        'rail': data['uxbridge'],
        'trolley': data['uxbridgetr']
    }
elif linkoption == 'Heathrow-Staines':
    data = {
        'rail': data['staines'],
        'trolley': data['stainestr']
    }
elif linkoption == 'Heathrow-Woking':
    data = {
        'rail': data['woking'],
        'trolley': data['wokingtr']
    }

fig = go.Figure()
fig.add_trace(go.Scatter(x=year, y=data['rail'][percentage_val - 1],
                         mode='lines',
                         name='Rail solution',
                         marker=dict(color='purple')))

fig.add_trace(go.Scatter(x=year, y=data['trolley'][percentage_val - 1],
                         mode='lines',
                         name='Trolley Bus solution',
                         marker=dict(color='darkorange')))

fig.update_layout(yaxis_range=[min(data['rail'][percentage_val - 1].min().min(), data['trolley'][percentage_val - 1].min().min()),
                               max(data['rail'][percentage_val - 1].max().max(), data['trolley'][percentage_val - 1].max().max())])

fig2 = make_subplots(rows=1, cols=2, specs=[[{'type': 'surface'}, {'type': 'surface'}]],
                     subplot_titles=('Rail solution', 'Trolley Bus solution'),
                     horizontal_spacing=0.01,
                     vertical_spacing=0.1)
fig2.add_trace(go.Surface(z=data['rail'], y=year, x=poppercent, name='Rail Solution', showscale=False, colorscale='inferno'), row=1, col=1)
fig2.add_trace(go.Surface(z=data['trolley'], y=year, x=poppercent, name='Trolley Bus Solution', showscale=False, colorscale='inferno'), row=1, col=2)

fig.add_hline(y=0,
              line_color='red',
              line_dash='dash')

fig.update_layout(xaxis_title='Year',
                  yaxis_title='Total Earnings [£ million]',
                  title=f"{linkoption} Mode comparison for {percentage_val}% share of total Heathrow passengers",
                  legend=dict(
                      title='Mode type:'
                  ))

fig2.update_layout(
    margin=dict(l=0, r=0, t=20, b=10),
    scene1=dict(
        xaxis_title='Heathrow passengers using link [%]',
        yaxis_title='Years',
        zaxis_title='Total Earnings [£ million]'),
    scene2=dict(
        xaxis_title='Heathrow passengers using link [%]',
        yaxis_title='Years',
        zaxis_title='Total Earnings [£ million]'))

fig2.layout.scene1.camera.eye = dict(x=0, y=15, z=2)
fig2.layout.scene2.camera.eye = dict(x=0, y=15, z=2)

fig2.layout.scene1.aspectratio = dict(x=4, y=4, z=6)
fig2.layout.scene2.aspectratio = dict(x=4, y=4, z=6)

plotter = st.plotly_chart(fig, use_container_width=True)  # Use container width for responsive design
st.markdown(f"**{linkoption} Surface plots for both modes -** *feel free to rotate charts*")
plotter2 = st.plotly_chart(fig2, use_container_width=True)

# qualitative
st.title('Qualitative Assessment :briefcase:')

scores = {
    'reading': {
        'rail': 3.8,
        'trolley': 3.3
    },
    'woking': {
        'rail': 3.78,
        'trolley': 3.7
    },
    'staines': {
        'rail': 3.2,
        'trolley': 3.78
    },
    'uxbridge': {
        'rail': 3.37,
        'trolley': 3.29
    }
}

factors = {
    'accessibility': {
        'rail': 3.58,
        'trolley': 3.165
    },
    'comfort': {
        'rail': 3.4975,
        'trolley': 2.83
    },
    'safety': {
        'rail': 3.33,
        'trolley': 3.47
    },
    'deliverability': {
        'rail': 3.5,
        'trolley': 2.9
    }
}

barplot = go.Figure(data=[
    go.Bar(name='Rail solution',
           y=['Reading', 'Uxbridge', 'Staines', 'Woking'],
           x=[scores['reading']['rail'], scores['uxbridge']['rail'], scores['staines']['rail'], scores['woking']['rail']],
           orientation='h',
           marker=dict(color='purple')),
    go.Bar(name='Trolley Bus solution',
           y=['Reading', 'Uxbridge', 'Staines', 'Woking'],
           x=[scores['reading']['trolley'], scores['uxbridge']['trolley'], scores['staines']['trolley'], scores['woking']['trolley']],
           orientation='h',
           marker=dict(color='darkorange'))
])

barplot.update_layout(title='Average Qualitative Assessment Scores per Link')

st.plotly_chart(barplot, use_container_width=True)

barplot2 = go.Figure(data=[
    go.Bar(name='Rail solution',
           y=['Accessibility', 'Comfort', 'Safety', 'Deliverability'],
           x=[factors['accessibility']['rail'], factors['comfort']['rail'], factors['safety']['rail'], factors['deliverability']['rail']],
           orientation='h',
           marker=dict(color='purple')),
    go.Bar(name='Trolley Bus solution',
           y=['Accessibility', 'Comfort', 'Safety', 'Deliverability'],
           x=[factors['accessibility']['trolley'], factors['comfort']['trolley'], factors['safety']['trolley'], factors['deliverability']['trolley']],
           orientation='h',
           marker=dict(color='darkorange'))
])

barplot2.update_layout(title='Average Qualitative Assessment Scores per Social and Feasibility Factor')

st.plotly_chart(barplot2, use_container_width=True)
