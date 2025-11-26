# google_sheets_client.py
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import streamlit as st

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# TODO: put your actual Sheet ID here
SHEET_ID = "1LFcyNm5F31PUb6XfoATsrJ68NojFPhpncq7Yt3Rm9Hc"
SHEET_NAME = "data"  # or "data" if you renamed it

@st.cache_resource
def get_gsheet_client():
    creds = Credentials.from_service_account_file(
        "service_account.json",
        scopes=SCOPES,
    )
    client = gspread.authorize(creds)
    return client

@st.cache_data
def fetch_data(city, poi_type, grid_size, output_type):
    client = get_gsheet_client()
    sh = client.open_by_key(SHEET_ID)
    ws = sh.worksheet(SHEET_NAME)

    # Read all rows (header row becomes columns)
    records = ws.get_all_records()
    df = pd.DataFrame(records)

    if df.empty:
        return df

    # Filter based on dropdown selections
    mask = (
        (df["city"] == city) &
        (df["poi_type"] == poi_type) &
        (df["grid_size"] == grid_size) &
        (df["output_type"] == output_type)
    )
    return df[mask].reset_index(drop=True)
