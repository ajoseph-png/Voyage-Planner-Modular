# map_utils.py
import folium

def create_waypoint_map(start, end, waypoints=[]):
    m = folium.Map(location=start, zoom_start=7)
    folium.Marker(start, tooltip="Start Port", icon=folium.Icon(color="blue", icon="anchor", prefix="fa")).add_to(m)
    folium.Marker(end, tooltip="End Port", icon=folium.Icon(color="purple", icon="anchor", prefix="fa")).add_to(m)
    for i, wp in enumerate(waypoints, 1):
        folium.Marker(wp, tooltip=f"Waypoint {i}", icon=folium.Icon(color="cadetblue", icon="flag", prefix="fa")).add_to(m)
    return m

def create_voyage_map(route, start, end, waypoints=[]):
    m = folium.Map(location=start, zoom_start=7)
    folium.PolyLine(route, color="blue", weight=3).add_to(m)
    folium.Marker(start, tooltip="Start Port", icon=folium.Icon(color="blue", icon="anchor", prefix="fa")).add_to(m)
    folium.Marker(end, tooltip="End Port", icon=folium.Icon(color="purple", icon="anchor", prefix="fa")).add_to(m)
    for i, wp in enumerate(waypoints, 1):
        folium.Marker(wp, tooltip=f"Waypoint {i}", icon=folium.Icon(color="cadetblue", icon="flag", prefix="fa")).add_to(m)
    return m
