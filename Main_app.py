import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from streamlit_lottie import st_lottie

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="Ecobici CDMX", page_icon="🚲", layout="wide")

# --- 2. DATA FETCHING (Cached) ---
@st.cache_data
def get_ecobici_data():
    url = 'https://gbfs.mex.lyftbikes.com/gbfs/gbfs.json'
    website_data = requests.get(url).json()
    urls = website_data['data']['en']['feeds']
    
    info_url = next(u['url'] for u in urls if 'station_information' in u['url'])
    status_url = next(u['url'] for u in urls if 'station_status' in u['url'])

    df1 = pd.DataFrame(requests.get(info_url).json()['data']['stations'])[['station_id', 'lat', 'lon', 'capacity']]
    df2 = pd.DataFrame(requests.get(status_url).json()['data']['stations'])[['station_id', 'num_bikes_available', 'num_docks_available']]
    
    return pd.merge(df1, df2, on='station_id')

# --- 3. LOTTIE ANIMATION LOADER ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Bike animation URL (A smooth cycling animation)
lottie_bike = load_lottieurl("https://lottie.host/80709087-94e9-4e0e-953e-5f336605986d/oP7YF3T0fA.json")

# --- ROW 1: HEADER & ANIMATION ---
col1, col2 = st.columns([2, 1])

with col1:
    st.title("Ecobici CDMX Tracker")
    st.caption("Developed with ❤️ by [Your Name]")
    
with col2:
    # This makes the bicycle "do something" (pedal!)
    st_lottie(lottie_bike, speed=1, reverse=False, loop=True, quality="low", height=150)

st.divider()

# --- ROW 2: INTERACTIVE MAP ---
df = get_ecobici_data()

# Sidebar for controls to keep the main view clean
st.sidebar.header("Controls")
all_ids = sorted(df['station_id'].unique().tolist())
selected_station = st.sidebar.selectbox("Highlight a Station:", all_ids)

def bike_share_system_plot(station_number):
    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=13)

    # Add all stations
    for n in range(len(df)):
        folium.Marker(
            location=[df['lat'].iloc[n], df['lon'].iloc[n]],
            tooltip=f"ID: {df['station_id'].iloc[n]}",
            icon=folium.Icon(color="red", icon="bicycle", prefix="fa"),
        ).add_to(m)

    # Highlight selection
    temp = df[df['station_id'] == station_number]
    if not temp.empty:
        folium.Marker(
            location=[temp['lat'].iloc[0], temp['lon'].iloc[0]],
            popup=f"Station {station_number}: {temp['num_bikes_available'].iloc[0]} bikes available",
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(m)

    st_folium(m, width=1000, height=500)

bike_share_system_plot(selected_station)
