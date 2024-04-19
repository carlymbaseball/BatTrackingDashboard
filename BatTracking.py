import pandas as pd
import streamlit as st
import plotly.express as px
import pandas_gbq
import pydata_google_auth

# Constants
PLOT_WIDTH = 1150
PLOT_HEIGHT = 600

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
    filtered_df = df if player_name == 'All' else df[df['player'] == player_name]
    fig = px.scatter(filtered_df, hover_data=['player'], x='SBA', y='VSA', color=color_variable, color_continuous_scale='Oranges')
    fig.update_layout(
        title=title,
        xaxis=dict(title='SBA', autorange='reversed'),  # Reverse x-axis
        yaxis=dict(title='VSA', autorange='reversed'),  # Reverse y-axis
        width=PLOT_WIDTH,
        height=PLOT_HEIGHT,
    )
    fig.update_traces(
        hoverlabel=dict(
            font=dict(size=20)  # Adjust the font size of hover text
        )
    )
    st.plotly_chart(fig)

# Define function to update line plot
def update_line_plot(fig, df, player_name, y_axis_metric, title):
    filtered_df = df if player_name == 'All' else df[df['player'] == player_name]
    fig.data = []  # Clear existing data
    fig.add_trace(px.line(filtered_df, x='game_date', y=y_axis_metric).data[0])  # Update figure with new data
    fig.update_layout(
        title=title,
        xaxis=dict(title='game_date'),  # Reverse x-axis
        yaxis=dict(title=y_axis_metric),
        width=PLOT_WIDTH,
        height=PLOT_HEIGHT,
    )

# Define function to calculate rolling averages
def calculate_rolling_averages(df):
    metrics_to_roll = ['SwM_Perc', 'IZ_SwM_Perc', 'FB_SwM_Perc', 'BB_SwM_Perc']
    for metric in metrics_to_roll:
        df[f'{metric}_Rolling_Avg'] = df[metric].rolling(window=5).mean()
    return df

def main():
    st.set_page_config(layout="wide")

    # Load data
    sfg_hitters_data = load_data('he_sfg.csv')
    mlb_hitters_data = load_data('he_all.csv')
    additional_data = load_data('2024_rolling.csv')  # Update additional data source

    # Execute BigQuery query and display results
    st.subheader('')
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


    # Execute BigQuery query and display results
    st.sidebar.markdown('<h3 style="font-size:20px;">Player & Data Selection</h3>', unsafe_allow_html=True)

    #Line Separator1
    st.sidebar.markdown('---')
    selected_player_bigquery = st.sidebar.selectbox('Select Player (2024 Rolling):', ['All'] + df_bigquery['player'].unique().tolist())
    if selected_player_bigquery != 'All':
        df_bigquery = df_bigquery[df_bigquery['player'] == selected_player_bigquery]

    # Define available metrics for y-axis
    y_axis_metrics = ['SBA', 'VSA', 'BatSpeed', 'AttackAngle', 'ContactAngle', 'swings']  # Add or remove metrics as needed

    # Select metric for y-axis
    selected_y_axis_metric = st.sidebar.selectbox('Select Y-Axis (2024 Rolling):', y_axis_metrics)

    #Line Separator2
    st.sidebar.markdown('---')

    # Select player for SFG Hitters 2023
    selected_player_sfg = st.sidebar.selectbox('Select Player (SFG Hitters 2023):', ['All'] + sfg_hitters_data['player'].unique().tolist())

    # Select player for MLB Hitters 2023
    selected_player_all = st.sidebar.selectbox('Select Player (MLB Hitters 2023):', ['All'] + mlb_hitters_data['player'].unique().tolist())

    st.title('Bat Tracking Dashboard')
    st.markdown("You can find the HawkEye metric dictionary [here.](https://docs.google.com/presentation/d/1nWijqEPe8m4tjqsn3TrAG1O1N2u6Kumz5icSxosU6_0/edit#slide=id.g227cd5eb79c_0_77) If you have any questions or ideas on how to make this dashboard better, reach out to Carly cmitchell@sfgiants.com")

    # Plot line graph for BigQuery Results
    st.subheader('2024 Rolling Bat Metrics')
    fig = px.line()
    update_line_plot(fig, df_bigquery, selected_player_bigquery, selected_y_axis_metric, f'{selected_y_axis_metric} Trend Over Time for {selected_player_bigquery}')
    st.plotly_chart(fig)

    # Display the full query results/table
    st.subheader('Rolling Data Table')
    st.dataframe(df_bigquery)

    # Add a button to refresh the data and plot
    if st.button('Refresh Data'):
        df_bigquery = execute_bigquery_query(query)
        selected_player_bigquery = st.sidebar.selectbox('Select Player (2024 Rolling):', ['All'] + df_bigquery['player'].unique().tolist())
        if selected_player_bigquery != 'All':
            df_bigquery = df_bigquery[df_bigquery['player'] == selected_player_bigquery]
        update_line_plot(fig, df_bigquery, selected_player_bigquery, selected_y_axis_metric, f'{selected_y_axis_metric} Trend Over Time for {selected_player_bigquery}')

        # Add a button to clear cache
    if st.button('Clear Cache'):
        st.caching.clear_cache()

    st.subheader('San Francisco Giants Hitters 2023')
    update_scatter_plot(sfg_hitters_data, selected_player_sfg, 'SwM_Perc', '')

    st.subheader('Major League Baseball Hitters 2023')
    update_scatter_plot(mlb_hitters_data, selected_player_all, 'SwM_Perc', '')



if __name__ == "__main__":
    main()