# google_sheets_client.py
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import streamlit as st
import streamlit as st
from streamlit_gsheets import GSheetsConnection

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# TODO: put your actual Sheet ID here
SHEET_ID = "1NSxmfeRUD-bkjIC8Bl_4JJMZaJExRJ2x_DX1NDOvqgc" # "1LFcyNm5F31PUb6XfoATsrJ68NojFPhpncq7Yt3Rm9Hc"
SHEET_NAME = ["delhi_1km", "delhi_1km_2"] # "grid_exp_gdf"  # or "data" if you renamed it

# @st.cache_resource
# def get_gsheet_client():
#     creds = Credentials.from_service_account_file(
#         "service_account.json",
#         scopes=SCOPES,
#     )
#     client = gspread.authorize(creds)
#     return client

@st.cache_data
def fetch_data(city, poi_type, grid_size, output_type):
    # client = get_gsheet_client()
    # sh = client.open_by_key(SHEET_ID)
    # ws = sh.worksheet(SHEET_NAME)

    # # Read all rows (header row becomes columns)
    # records = ws.get_all_records()
    # df = pd.DataFrame(records)

    
    # Create a connection object.
    conn = st.connection("gsheets", type=GSheetsConnection)

    worksheet = ""
    if city == "Delhi" & grid_size == "1 km":
        worksheet = SHEET_NAME[0]
    else:
        worksheet = SHEET_NAME[1]
    
    df = conn.read(
        worksheet=worksheet,
        ttl="10m",
        usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        nrows=3,
    )
    if df.empty:
        return df

    # Filter based on dropdown selections
    mask = (
        (df["output_type"] == output_type)
    )
    return df[mask].reset_index(drop=True)

