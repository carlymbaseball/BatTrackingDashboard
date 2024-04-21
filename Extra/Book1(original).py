import pandas as pd
import streamlit as st
import plotly.express as px
import pandas_gbq
import pydata_google_auth

# Load data
@st.cache_data
def load_data(filename):
    return pd.read_csv(filename)

# Authenticate with Google Cloud and get credentials
def authenticate_google_cloud():
    credentials = pydata_google_auth.get_user_credentials(
        [
            'https://www.googleapis.com/auth/cloud-platform',
            'https://www.googleapis.com/auth/drive',
        ],
        auth_local_webserver=True,
    )
    return credentials

# Define function to execute BigQuery query
def execute_bigquery_query(query):
    credentials = authenticate_google_cloud()
    df = pd.read_gbq(query, project_id="sfgiants-viewer", credentials=credentials)
    return df

# Define function to update scatter plot
def update_scatter_plot(df, player_name, color_variable, title):
    if player_name == 'All':
        filtered_df = df
    else:
        filtered_df = df[df['player'] == player_name]
    fig = px.scatter(filtered_df, hover_data=['player'], x='SBA', y='VSA', color=color_variable, color_continuous_scale='Oranges')
    fig.update_layout(
        title=title,
        xaxis=dict(title='SBA', autorange='reversed'),  # Reverse x-axis
        yaxis=dict(title='VSA', autorange='reversed'),  # Reverse y-axis
        width=1150,  # Set width of the plot
        height=600,  # Set height of the plot
    )
    st.plotly_chart(fig)

# Define function to update line plot
def update_line_plot(df, player_name, y_axis_metric, title):
    if player_name == 'All':
        filtered_df = df
    else:
        filtered_df = df[df['player'] == player_name]
    fig = px.line(filtered_df, x='game_date', y=y_axis_metric)
    fig.update_layout(
        title=title,
        xaxis=dict(title='game_date', autorange='reversed'),  # Reverse x-axis
        yaxis=dict(title=y_axis_metric),
        width=1150,  # Set width of the plot
        height=600,  # Set height of the plot
    )
    st.plotly_chart(fig)

# Define function to update line plot for rolling averages
def update_rolling_average_plot(df, player_name, rolling_metric, title):
    if player_name == 'All':
        filtered_df = df
    else:
        filtered_df = df[df['player'] == player_name]
    fig = px.line(filtered_df, x='game_date', y=rolling_metric)
    fig.update_layout(
        title=title,
        xaxis=dict(title='game_date', autorange='reversed'),  # Reverse x-axis
        yaxis=dict(title=rolling_metric),
        width=1150,  # Set width of the plot
        height=600,  # Set height of the plot
    )
    st.plotly_chart(fig)

# Define function to calculate rolling averages
def calculate_rolling_averages(df):
    df['SwM_Rolling_Avg'] = df['SwM_Perc'].rolling(window=5).mean()
    df['IZ_SwM_Rolling_Avg'] = df['IZ_SwM_Perc'].rolling(window=5).mean()
    df['FB_SwM_Rolling_Avg'] = df['FB_SwM_Perc'].rolling(window=5).mean()
    df['BB_SwM_Rolling_Avg'] = df['BB_SwM_Perc'].rolling(window=5).mean()
    return df

def main():
    st.set_page_config(layout="wide")

    # Load data
    he_sfg = load_data('he_sfg.csv')
    he_all = load_data('he_all.csv')
    additional_data = load_data('2024_rolling.csv')  # Update additional data source

    # Get unique player names
    player_names_sfg = ['All'] + he_sfg['player'].unique().tolist()
    player_names_all = ['All'] + he_all['player'].unique().tolist()

    # Define color options with custom labels
    color_options = {'SwM': 'Swing & Miss', 'BB_SwM': 'Breaking Ball Swing & Miss', 'FB_SwM': 'Fastball Swing & Miss', 'IZ_SwM': 'In-Zone Swing & Miss'}
    color_variable = st.sidebar.selectbox('Colored By - Scatter Plots:', list(color_options.keys()), format_func=lambda x: color_options[x])

    # Select player for SFG Hitters 2023
    selected_player_sfg = st.sidebar.selectbox('Select Player (SFG Hitters 2023):', player_names_sfg)

    # Select player for MLB Hitters 2023
    selected_player_all = st.sidebar.selectbox('Select Player (MLB Hitters 2023):', player_names_all)

    # Select player for BigQuery Results
    selected_player_bigquery = st.sidebar.selectbox('Select Player (2024 Rolling):', player_names_sfg)

    # Define available metrics for y-axis
    y_axis_metrics = ['SBA', 'VSA', 'BatSpeed', 'AttackAngle', 'ContactAngle', 'swings']  # Add or remove metrics as needed

    # Select metric for y-axis
    selected_y_axis_metric = st.sidebar.selectbox('Select Y-Axis (2024 Rolling):', y_axis_metrics)

    st.title('Bat Angles and Hitting Performance')
    st.markdown("You can find the HawkEye metric dictionary [here.](https://docs.google.com/presentation/d/1nWijqEPe8m4tjqsn3TrAG1O1N2u6Kumz5icSxosU6_0/edit#slide=id.g227cd5eb79c_0_65) If you have any questions or ideas on how to make this dashboard better, reach out to Carly cmitchell@sfgiants.com")

    st.subheader('San Francisco Giants Hitters 2023')
    update_scatter_plot(he_sfg, selected_player_sfg, color_variable, 'swing bottom angle X vertical swing angle')

    st.subheader('Major League Baseball Hitters 2023')
    update_scatter_plot(he_all, selected_player_all, color_variable, 'swing bottom angle X vertical swing angle')

    # Execute BigQuery query and display results
    st.subheader('BigQuery Results:')
    query = """
    SELECT 
        ge.game_date, 
        current_org, 
        current_team, 
        CONCAT(last_name, ', ', first_name) as player,
        COUNT(*) as swings,
        ROUND(AVG(vertical_swing_angle), 2) as VSA,
        ROUND(AVG(swing_bottom_angle), 2) as SBA,
        ROUND(AVG(bat_speed), 2) as BatSpeed,
        ROUND(AVG(attack_angle), 2) as AttackAngle,
        ROUND(AVG(contact_angle), 2) as ContactAngle,
        ROUND(SAFE_DIVIDE(COUNTIF(is_swing_and_miss), COUNTIF(is_swing)) * 100, 2) as SwM_Perc, 
        ROUND(SAFE_DIVIDE(COUNTIF(strike_probability > 0.5 and is_swing_and_miss), COUNTIF(strike_probability > 0.5 and is_swing)) * 100, 2) as IZ_SwM_Perc,
        ROUND(SAFE_DIVIDE(COUNTIF(is_swing_and_miss and ge.pitch_type in ('four_seam','sinker')), COUNTIF(is_swing and ge.pitch_type in ('four_seam','sinker'))) * 100, 2) as FB_SwM_Perc,
        ROUND(SAFE_DIVIDE(COUNTIF(is_swing_and_miss and ge.pitch_type in ('curveball','slider')), COUNTIF(is_swing and ge.pitch_type in ('curveball','slider'))) * 100, 2) as BB_SwM_Perc,
    FROM 
        sfgiants-viewer.game_event.pro ge 
    INNER JOIN 
        sfgiants-analyst.swing_tracking.hawkeye st on st.pitch_uid = ge.trackman_pitch_uid 
    LEFT JOIN 
        prod-warehouse-sfgiants-onprem.scout_replica_scouting.tblPlayer_Pro map on ge.hitter_sfg_id = map.player_code 
    WHERE 
        year = 2024 
        AND vertical_swing_angle IS NOT NULL 
        AND position_code != 'P' 
        AND current_org = 'San Francisco Giants' 
    GROUP BY 
        ge.game_date, player, current_org, current_team 
    ORDER BY 
        ge.game_date DESC, player, current_org, current_team
    """

    df_bigquery = execute_bigquery_query(query)

    # Filter SQL query results based on selected player
    if selected_player_bigquery != 'All':
        df_bigquery = df_bigquery[df_bigquery['player'] == selected_player_bigquery]

    # Plot line graph for BigQuery Results
    st.subheader('Line Graph for BigQuery Results:')
    fig_bigquery = px.line(df_bigquery, x='game_date', y=selected_y_axis_metric)
    fig_bigquery.update_layout(
        title=f'{selected_y_axis_metric} Trend Over Time for {selected_player_bigquery}',
        xaxis=dict(title='game_date'),
        yaxis=dict(title=selected_y_axis_metric),
        width=1150,  # Set width of the plot
        height=600,  # Set height of the plot
    )
    st.plotly_chart(fig_bigquery)

    # Display the original table or update it
    # Display the original table or update it
    table = st.empty()
    if st.button('Toggle Raw Query Table'):
        if table.empty:
            # Display the table if it's not already displayed
            table.write(df_bigquery_sorted)
        else:
            # Remove the table if it's already displayed
            table.empty()

    # Add a button to clear cache
    if st.button('Clear Cache'):
        st.caching.clear_cache()

if __name__ == "__main__":
    main()