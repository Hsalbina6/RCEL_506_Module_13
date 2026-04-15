import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from streamlit_lottie import st_lottie

# --- 1. DATA FETCHING ---
@st.cache_data(ttl=60) # Refresh data every minute
def get_ecobici_data():
    try:
        url = 'https://gbfs.mex.lyftbikes.com/gbfs/gbfs.json'
        website_data = requests.get(url).json()
        urls = website_data['data']['en']['feeds']
        info_url = next(u['url'] for u in urls if 'station_information' in u['url'])
        status_url = next(u['url'] for u in urls if 'station_status' in u['url'])
        
        df1 = pd.DataFrame(requests.get(info_url).json()['data']['stations'])[['station_id', 'lat', 'lon', 'capacity', 'name']]
        df2 = pd.DataFrame(requests.get(status_url).json()['data']['stations'])[['station_id', 'num_bikes_available', 'num_docks_available']]
        
        return pd.merge(df1, df2, on='station_id')
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

# --- 2. LOTTIE LOADER ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

lottie_bike = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_U8986t.json")

# --- ROW 1: HEADER ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Ecobici CDMX Tracker")
    st.caption("Developed by Hassan Albin Alshaikh")

with col2:
    if lottie_bike:
        st_lottie(lottie_bike, height=120, key="bike_anim")
    else:
        st.write("🚲")

st.divider()

# --- ROW 2: SIDEBAR & MAP ---
df = get_ecobici_data()

if not df.empty:
    # Sidebar Selection
    st.sidebar.header("Station Search")
    # Using the list as shown in your image
    station_list = sorted(df['station_id'].unique())
    selected_id = st.sidebar.selectbox("Select Station ID:", station_list)
    
    # Map Initialization
    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=13)
    
    # Logic for Dynamic Marker Colors
    for i, row in df.iterrows():
        bikes = row['num_bikes_available']
        
        # Color Logic
        if bikes > 5:
            marker_color = "green"
        elif bikes > 0:
            marker_color = "orange"
        else:
            marker_color = "red"
            
        folium.Marker(
            [row['lat'], row['lon']], 
            tooltip=f"ID: {row['station_id']} | Bikes: {bikes}",
            icon=folium.Icon(color=marker_color, icon="bicycle", prefix="fa")
        ).add_to(m)
        
    # Highlight the specific selected station with a Blue Star
    target = df[df['station_id'] == selected_id].iloc[0]
    folium.Marker(
        [target['lat'], target['lon']],
        popup=f"<b>Station {selected_id}</b><br>Name: {target['name']}<br>Bikes: {target['num_bikes_available']}<br>Docks: {target['num_docks_available']}",
        icon=folium.Icon(color="blue", icon="star", prefix="fa"),
        z_index_offset=1000 # Keep selected station on top
    ).add_to(m)

    st_folium(m, width=1000, height=500)
    
    # Quick Stats Row
    st.write("### Station Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Bikes Available", target['num_bikes_available'])
    c2.metric("Empty Docks", target['num_docks_available'])
    c3.metric("Total Capacity", target['capacity'])
