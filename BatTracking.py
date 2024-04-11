#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import plotly.express as px
from ipywidgets import interact, Dropdown 

he_sfg = pd.read_csv('he_sfg.csv')  # Adjust the file path as per your data

color_options = ['SwM', 'BB_SwM', 'FB_SwM', 'IZ_SwM']

def update_plot(color_variable):
    fig = px.scatter(he_sfg, hover_data=['player'], x='VSA', y='SBA', color=color_variable, color_continuous_scale='Oranges')
    fig.update_layout(
        title='SFG Hitters',
        xaxis=dict(title='VSA'),
        yaxis=dict(title='SBA')
    )
    fig.show()

dropdown = Dropdown(
    options=color_options,
    description='Colored By:'
)

interact(update_plot, color_variable=dropdown)


# In[2]:


import pandas as pd
import plotly.express as px
from ipywidgets import interact, Dropdown 

he_all = pd.read_csv('he_all.csv')  # Adjust the file path as per your data

color_options = ['SwM', 'BB_SwM', 'FB_SwM', 'IZ_SwM']

def update_plot(color_variable):
    fig = px.scatter(he_all, hover_data=['player'], x='VSA', y='SBA', color=color_variable, color_continuous_scale='Oranges')
    fig.update_layout(
        title='MLB Hitters',
        xaxis=dict(title='VSA'),
        yaxis=dict(title='SBA')
    )
    fig.show()

dropdown = Dropdown(
    options=color_options,
    description='Colored By:'
)

interact(update_plot, color_variable=dropdown)


# In[ ]:




