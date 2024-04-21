import pandas_gbq
import pydata_google_auth
import pandas as pd

# Define your SQL query
pc_stmt = "SELECT player_code FROM sfgiants-viewer.scout_replica_scouting.tblPlayer_Pro WHERE player_code IN (139786) LIMIT 1"

# Authenticate with Google Cloud and get credentials
credentials = pydata_google_auth.get_user_credentials(
    [
        'https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/drive',
    ],
    auth_local_webserver=True,
)

# Read data from BigQuery into a Pandas DataFrame
df_codes = pd.read_gbq(pc_stmt, project_id="sfgiants-viewer", credentials=credentials)

# Now you can work with the DataFrame df_codes
print(df_codes.head())  # Example: Print the first few rows of the DataFrame