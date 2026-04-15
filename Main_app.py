import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

# --- DATA FETCHING (Using your logic) ---
@st.cache_data
def get_ecobici_data():
    url = 'https://gbfs.mex.lyftbikes.com/gbfs/gbfs.json'
    website_data = requests.get(url).json()
    urls = website_data['data']['en']['feeds']
    
    # Identifying specific feeds to ensure robustness
    info_url = next(u['url'] for u in urls if 'station_information' in u['url'])
    status_url = next(u['url'] for u in urls if 'station_status' in u['url'])

    # Station Information (lat, lon, capacity)
    data1 = requests.get(info_url).json()
    df1 = pd.DataFrame(data1['data']['stations'])
    df1 = df1[['station_id', 'lat', 'lon', 'capacity']]

    # Station Status (bikes/docks availability)
    data2 = requests.get(status_url).json()
    df2 = pd.DataFrame(data2['data']['stations'])
    df2 = df2[['station_id', 'num_bikes_available', 'num_bikes_disabled', 'num_docks_available', 'num_docks_disabled']]

    # Merge dataframes
    df = pd.merge(df1, df2, on='station_id')
    return df

# Load the data
df = get_ecobici_data()

# --- ROW 1: Header ---
st.title("Ecobici CDMX Dashboard")
st.caption("Developed by [Your Name]") # Replace with your actual name

st.divider()

# --- ROW 2: Map & Interactive Selection ---
def bike_share_system_plot(station_number):
    # Initialize map centered on the average coordinates
    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=13)

    # Plot all stations in Red
    for n in range(len(df)):
        folium.Marker(
            location=[df['lat'].iloc[n], df['lon'].iloc[n]],
            tooltip=f"ID: {df['station_id'].iloc[n]} | Bikes: {df['num_bikes_available'].iloc[n]}",
            icon=folium.Icon(color="red"),
        ).add_to(m)

    # Highlight selected station in Blue
    temp = df[df['station_id'] == station_number]

    try:
        folium.Marker(
            location=[temp['lat'].iloc[0], temp['lon'].iloc[0]],
            tooltip=f"SELECTED: {temp['station_id'].iloc[0]}",
            icon=folium.Icon(color="blue", icon="cloud"),
        ).add_to(m)
    except IndexError:
        st.sidebar.error('Station not found')

    # Render map in Streamlit
    st_folium(m, width=800, height=400)

# Station selection widget
all_ids = sorted(df['station_id'].unique().tolist())
selected_station = st.selectbox("Select a Station to highlight:", all_ids)

# Call the plot function
bike_share_system_plot(selected_station)
