import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from streamlit_lottie import st_lottie

# --- 1. DATA FETCHING (Same as before) ---
@st.cache_data
def get_ecobici_data():
    try:
        url = 'https://gbfs.mex.lyftbikes.com/gbfs/gbfs.json'
        website_data = requests.get(url).json()
        urls = website_data['data']['en']['feeds']
        info_url = next(u['url'] for u in urls if 'station_information' in u['url'])
        status_url = next(u['url'] for u in urls if 'station_status' in u['url'])
        df1 = pd.DataFrame(requests.get(info_url).json()['data']['stations'])[['station_id', 'lat', 'lon', 'capacity']]
        df2 = pd.DataFrame(requests.get(status_url).json()['data']['stations'])[['station_id', 'num_bikes_available', 'num_docks_available']]
        return pd.merge(df1, df2, on='station_id')
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

# --- 2. ROBUST LOTTIE LOADER ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Try a different stable bike animation
lottie_bike = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_U8986t.json")

# --- ROW 1: HEADER ---
col1, col2 = st.columns([3, 1])

with col1:
    st.title("Ecobici CDMX Tracker")
    st.caption("Developed by [Your Name]")

with col2:
    # THE FIX: Only try to show if lottie_bike is NOT None
    if lottie_bike:
        st_lottie(lottie_bike, height=120, key="bike_anim")
    else:
        st.write("🚲") # Fallback to emoji if animation fails

st.divider()

# --- ROW 2: MAP ---
df = get_ecobici_data()

if not df.empty:
    selected_id = st.sidebar.selectbox("Select Station:", sorted(df['station_id'].unique()))
    
    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=13)
    
    # Add Red markers for all
    for i, row in df.iterrows():
        folium.Marker(
            [row['lat'], row['lon']], 
            tooltip=f"ID: {row['station_id']}",
            icon=folium.Icon(color="red", icon="bicycle", prefix="fa")
        ).add_to(m)
        
    # Highlight Blue
    target = df[df['station_id'] == selected_id].iloc[0]
    folium.Marker(
        [target['lat'], target['lon']],
        popup=f"Bikes Available: {target['num_bikes_available']}",
        icon=folium.Icon(color="blue", icon="star")
    ).add_to(m)

    st_folium(m, width=1000, height=500)
