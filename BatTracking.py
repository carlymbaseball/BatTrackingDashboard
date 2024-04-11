import pandas as pd
import streamlit as st
import plotly.express as px

# Load data
@st.cache_data
def load_data(filename):
    return pd.read_csv(filename)

# Define function to update plot
def update_plot(df, color_variable, title):
    fig = px.scatter(df, hover_data=['player'], x='VSA', y='SBA', color=color_variable, color_continuous_scale='Oranges')
    fig.update_layout(
        title=title,
        xaxis=dict(title='VSA'),
        yaxis=dict(title='SBA')
    )
    st.plotly_chart(fig)

def main():
    st.title('SFG Hitters vs MLB Hitters')

    # Load data
    he_sfg = load_data('he_sfg.csv')
    he_all = load_data('he_all.csv')

    # Define color options
    color_options = ['SwM', 'BB_SwM', 'FB_SwM', 'IZ_SwM']

    # Select color variable
    color_variable = st.selectbox('Colored By:', color_options)

    # Update plot for SFG Hitters
    st.subheader('SFG Hitters')
    update_plot(he_sfg, color_variable, 'SFG Hitters')

    # Update plot for MLB Hitters
    st.subheader('MLB Hitters')
    update_plot(he_all, color_variable, 'MLB Hitters')

if __name__ == "__main__":
    main()
