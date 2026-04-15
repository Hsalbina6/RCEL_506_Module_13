import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# Standard assumption for data structure based on your function
# df = pd.read_csv('your_ecobici_data.csv') 

# Row 1: Title and Caption
st.title("Ecobici CDMX Station Tracker")
st.caption("Developed by Hassan Albin Alshaikh")

st.divider()

# Row 2: Map Visualization
def bike_share_system_plot(df, station_number):
    # Initialize map
    m = folium.Map(
        location=[df['lat'].mean(), df['lon'].mean()], 
        zoom_start=12
    )

    # Plot all stations
    for n in range(len(df)):
        folium.Marker(
            location=[df['lat'].iloc[n], df['lon'].iloc[n]],
            tooltip=str(df['station_id'].iloc[n]),
            icon=folium.Icon(color="red"),
        ).add_to(m)

    # Filter selected station
    temp = df[df['station_id'] == station_number]

    try:
        folium.Marker(
            location=[temp['lat'].iloc[0], temp['lon'].iloc[0]],
            tooltip=str(temp['station_id'].iloc[0]),
            icon=folium.Icon(color="blue", icon="cloud"),
        ).add_to(m)
    except IndexError:
        st.error('Station not found')

    # Display map in Streamlit
    st_folium(m, width=800, height=400)

# Implementation (Placeholder data used for demonstration)
if 'df' in locals() or 'df' in globals():
    selected_id = st.number_input("Enter Station ID", value=1, step=1)
    bike_share_system_plot(df, selected_id)
else:
    st.warning("Please ensure your DataFrame 'df' is loaded to view the map.")
