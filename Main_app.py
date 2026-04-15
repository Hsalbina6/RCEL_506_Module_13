import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from streamlit_lottie import st_lottie

# --- 1. DATA FETCHING ---
@st.cache_data(ttl=60)
def get_ecobici_data():
    try:
        url = 'https://gbfs.mex.lyftbikes.com/gbfs/gbfs.json'
        website_data = requests.get(url).json()
        urls = website_data['data']['en']['feeds']
        info_url = next(u['url'] for u in urls if 'station_information' in u['url'])
        status_url = next(u['url'] for u in urls if 'station_status' in u['url'])
        
        df1 = pd.DataFrame(requests.get(info_url).json()['data']['stations'])[['station_id', 'lat', 'lon', 'capacity', 'name']]
        df2 = pd.DataFrame(requests.get(status_url).json()['data']['stations'])[['station_id', 'num_bikes_available', 'num_docks_available']]
        
        df1['station_id'] = df1['station_id'].astype(int)
        df2['station_id'] = df2['station_id'].astype(int)
        
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

# --- ROW 2: SIDEBAR & CONFIG ---
df = get_ecobici_data()

if not df.empty:
    st.sidebar.header("Map Settings")
    
    # 1. Day/Night Toggle
    map_style = st.sidebar.radio("Map Mode:", ["Day (Standard)", "Night (Dark Mode)"])
    tile_provider = "OpenStreetMap" if map_style == "Day (Standard)" else "CartoDB dark_matter"

    # 2. Station Search
    st.sidebar.divider()
    st.sidebar.header("Station Search")
    df = df.sort_values('station_id')
    df['display_name'] = df['station_id'].astype(str) + " - " + df['name']
    selected_display = st.sidebar.selectbox("Select Station:", df['display_name'])
    selected_id = int(selected_display.split(" - ")[0])
    
    # --- MAP INITIALIZATION ---
    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=13, tiles=tile_provider)
    
    for i, row in df.iterrows():
        bikes = row['num_bikes_available']
        color = "green" if bikes > 5 else "orange" if bikes > 0 else "red"
            
        folium.Marker(
            [row['lat'], row['lon']], 
            tooltip=f"ID: {row['station_id']} | {row['name']}",
            icon=folium.Icon(color=color, icon="bicycle", prefix="fa")
        ).add_to(m)
        
    target = df[df['station_id'] == selected_id].iloc[0]
    folium.Marker(
        [target['lat'], target['lon']],
        popup=f"ID {selected_id}: {target['num_bikes_available']} bikes",
        icon=folium.Icon(color="blue", icon="star", prefix="fa"),
        z_index_offset=1000 
    ).add_to(m)

    st_folium(m, width=1000, height=500)
    
    # --- STATISTICS ---
    st.write(f"### Current Status: {target['name']}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Bikes Available", target['num_bikes_available'])
    c2.metric("Empty Docks", target['num_docks_available'])
    c3.metric("Total Capacity", target['capacity'])

    st.divider()

    # --- LEADERBOARDS ---
    st.write("### 🏆 CDMX Network Leaderboards")
    lead1, lead2 = st.columns(2)

    with lead1:
        st.subheader("🔥 Top 5 Fullest Stations")
        top_5 = df.nlargest(5, 'num_bikes_available')[['station_id', 'name', 'num_bikes_available']]
        st.dataframe(top_5, hide_index=True, use_container_width=True)

    with lead2:
        st.subheader("👻 Top 5 'Ghost' Stations")
        ghost_5 = df.nsmallest(5, 'num_bikes_available')[['station_id', 'name', 'num_bikes_available']]
        st.dataframe(ghost_5, hide_index=True, use_container_width=True)
