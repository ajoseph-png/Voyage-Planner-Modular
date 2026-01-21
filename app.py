# app.py
import streamlit as st
from voyage_utils import generate_voyage
from map_utils import create_waypoint_map, create_voyage_map

# Sidebar inputs
start = (st.sidebar.number_input("Start Lat", 18.938507),
         st.sidebar.number_input("Start Lon", 72.851778))
end = (st.sidebar.number_input("End Lat", 18.938507),
       st.sidebar.number_input("End Lon", 72.851778))
speed = st.sidebar.number_input("Average Speed (kn)", 10.0)
waypoints = st.session_state.get("waypoints", [])

# Map to select waypoints
map_placeholder = st.empty()
m = create_waypoint_map(start, end, waypoints)
click_data = st_folium(m, width=1100, height=550, key="waypoint_map")

# Add clicked waypoint
if click_data and click_data.get("last_clicked"):
    click = click_data["last_clicked"]
    if "waypoints" not in st.session_state:
        st.session_state.waypoints = []
    st.session_state.waypoints.append((click["lat"], click["lng"]))
    st.experimental_rerun()

# Generate voyage
if st.sidebar.button("🚀 Generate Voyage"):
    route = [start] + st.session_state.waypoints + [end]
    df, total_nm, eta = generate_voyage(route, speed)
    st.session_state.voyage_df = df
    st.session_state.metrics = {"distance": total_nm, "speed": speed, "eta": eta}

# Output
if "voyage_df" in st.session_state:
    df = st.session_state.voyage_df
    metrics = st.session_state.metrics
    st.metric("Distance (NM)", f"{metrics['distance']:.1f}")
    st.metric("ETA", metrics["eta"].strftime("%Y-%m-%d %H:%M"))
    
    voyage_map = create_voyage_map(route, start, end, st.session_state.waypoints)
    st_folium(voyage_map, width=1100, height=600)
    
    st.download_button("⬇ Download CSV", df.to_csv(index=False).encode("utf-8"), "voyage.csv", "text/csv")
