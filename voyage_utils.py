# voyage_utils.py
import math
import pandas as pd
from datetime import datetime, timedelta

def haversine_nm(lat1, lon1, lat2, lon2):
    """Distance in nautical miles"""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    km = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return km / 1.852

def interpolate(start, end, steps=60):
    return [
        (
            start[0] + (end[0] - start[0]) * i / (steps - 1),
            start[1] + (end[1] - start[1]) * i / (steps - 1),
        )
        for i in range(steps)
    ]

def generate_voyage(route, speed_knots):
    rows = []
    t = datetime.utcnow()
    for a, b in zip(route[:-1], route[1:]):
        for lat, lon in interpolate(a, b):
            rows.append([
                t.isoformat() + "Z",
                "OSV_SIM",
                "Transit",
                round(lat, 5),
                round(lon, 5),
                speed_knots,
                "Underway"
            ])
            t += timedelta(minutes=1)
    df = pd.DataFrame(rows, columns=["timestamp","vessel","phase","latitude","longitude","speed_knots","nav_status"])
    
    total_nm = sum(haversine_nm(*a,*b) for a,b in zip(route[:-1], route[1:]))
    eta = datetime.utcnow() + timedelta(hours=total_nm/speed_knots)
    
    return df, total_nm, eta
