# app.py
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import math

st.set_page_config(page_title="OSV Route Planner", layout="wide")
st.title("🚢 Offshore Supply Vessel Route Simulator")

# -------------------------------
# Session State Initialization
# -------------------------------
if "waypoints" not in st.session_state:
    st.session_state.waypoints = []

if "voyage_df" not in st.session_state:
    st.session_state.voyage_df = None

if "map_clicked" not in st.session_state:
    st.session_state.map_clicked = None

if "voyage_metrics" not in st.session_state:
    st.session_state.voyage_metrics = None

# -------------------------------
# Helper Functions
# -------------------------------
def haversine_nm(lat1, lon1, lat2, lon2):
    """Calculate distance in nautical miles"""
    R = 6371  # km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    km = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return km / 1.852  # convert km to NM

def interpolate(start, end, steps=60):
    """Interpolate points between start and end"""
    return [
        (
            start[0] + (end[0]-start[0])*i/(steps-1),
            start[1] + (end[1]-start[1])*i/(steps-1)
        )
        for i in range(steps)
    ]

def create_map(start, end, waypoints):
    """Create folium map with ports and waypoints"""
    m = folium.Map(location=start, zoom_start=7)
    # Start and End
    folium.Marker(start, tooltip="Start Port", icon=folium.Icon(color="blue", icon="anchor", prefix="fa")).add_to(m)
    folium.Marker(end, tooltip="End Port", icon=folium.Icon(color="purple", icon="anchor", prefix="fa")).add_to(m)
    # Waypoints
    for i, wp in enumerate(waypoints, 1):
        folium.Marker(wp, tooltip=f"Waypoint {i}", icon=folium.Icon(color="cadetblue", icon="flag", prefix="fa")).add_to(m)
    return m

# -------------------------------
# Sidebar Inputs
# -------------------------------
st.sidebar.header("📍 Ports")
start_lat = st.sidebar.number_input("Start Port Latitude", value=18.938507)
start_lon = st.sidebar.number_input("Start Port Longitude", value=72.851778)
end_lat = st.sidebar.number_input("End Port Latitude", value=19.41667)
end_lon = st.sidebar.number_input("End Port Longitude", value=71.33333)

st.sidebar.header("🧭 Vessel")
speed_knots = st.sidebar.number_input("Average Speed (knots, optional)", min_value=0.1, value=10.0)

st.sidebar.header("⚓ Waypoints")

# Manual input
with st.sidebar.expander("Add Waypoint Manually"):
    wp_lat = st.number_input("Waypoint Latitude", value=0.0, step=0.0001)
    wp_lon = st.number_input("Waypoint Longitude", value=0.0, step=0.0001)
    if st.button("➕ Add Waypoint"):
        st.session_state.waypoints.append((wp_lat, wp_lon))
        st.experimental_rerun()

# Display existing waypoints with remove button
if st.session_state.waypoints:
    st.sidebar.subheader("Current Waypoints")
    for i, wp in enumerate(st.session_state.waypoints):
        col1, col2 = st.sidebar.columns([4,1])
        col1.write(f"{i+1}. {wp[0]:.5f}, {wp[1]:.5f}")
        if col2.button("❌", key=f"remove_wp_{i}"):
            st.session_state.waypoints.pop(i)
            st.experimental_rerun()

# -------------------------------
# Map to add waypoints via click
# -------------------------------
st.subheader("🗺 Click on map to add waypoint")
waypoint_map = create_map((start_lat, start_lon), (end_lat, end_lon), st.session_state.waypoints)
click_data = st_folium(waypoint_map, width=1100, height=550, key="waypoint_map_unique")

# Add clicked waypoint to session state
if click_data and click_data.get("last_clicked"):
    click = click_data["last_clicked"]
    lat_lng = (click["lat"], click["lng"])
    if st.session_state.map_clicked != lat_lng:
        st.session_state.map_clicked = lat_lng
        st.session_state.waypoints.append(lat_lng)
        st.experimental_rerun()

# -------------------------------
# Generate Voyage
# -------------------------------
if st.sidebar.button("🚀 Generate Voyage"):
    route = [(start_lat, start_lon)] + st.session_state.waypoints + [(end_lat, end_lon)]
    total_nm = sum(haversine_nm(*a,*b) for a,b in zip(route[:-1], route[1:]))
    speed = speed_knots if speed_knots>0 else 10
    eta = datetime.utcnow() + timedelta(hours=total_nm/speed)

    # Build voyage DataFrame
    rows = []
    t = datetime.utcnow()
    for a,b in zip(route[:-1], route[1:]):
        for lat, lon in interpolate(a,b):
            rows.append([t.isoformat()+"Z","OSV_SIM","Transit",round(lat,5),round(lon,5),speed,"Underway"])
            t += timedelta(minutes=1)

    st.session_state.voyage_df = pd.DataFrame(
        rows, columns=["timestamp","vessel","phase","latitude","longitude","speed_knots","nav_status"]
    )
    st.session_state.voyage_metrics = {"distance":total_nm,"speed":speed,"eta":eta}

# -------------------------------
# Display Voyage Data & Map
# -------------------------------
if st.session_state.voyage_df is not None:
    df = st.session_state.voyage_df
    metrics = st.session_state.voyage_metrics

    col1,col2,col3 = st.columns(3)
    col1.metric("Total Distance (NM)", f"{metrics['distance']:.1f}")
    col2.metric("Avg Speed (kn)", f"{metrics['speed']}")
    col3.metric("ETA (UTC)", metrics["eta"].strftime("%Y-%m-%d %H:%M"))

    voyage_map = create_map((start_lat, start_lon), (end_lat, end_lon), st.session_state.waypoints)
    folium.PolyLine(list(zip(df.latitude, df.longitude)), color="blue", weight=3).add_to(voyage_map)

    st_folium(voyage_map, width=1100, height=600, key="voyage_map_display")

    st.download_button(
        "⬇ Download Voyage CSV",
        df.to_csv(index=False).encode("utf-8"),
        "custom_voyage.csv",
        "text/csv"
    )
