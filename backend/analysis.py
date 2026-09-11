import requests
import os
from dotenv import load_dotenv
from math import radians, sin, cos, sqrt, atan2

load_dotenv()


NASA_KEY = os.getenv("NASA_FIRMS_MAP_KEY")
print("NASA KEY LOADED:", NASA_KEY is not None)


def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c
if __name__ == "__main__":

    hotspot_lat = 13.0827
    hotspot_lon = 80.2707

    facility_lat = 13.1667
    facility_lon = 80.2583

    distance = calculate_distance(
        hotspot_lat,
        hotspot_lon,
        facility_lat,
        facility_lon
    )

    print("Thermal hotspot:", hotspot_lat, hotspot_lon)
    print("Industrial facility:", facility_lat, facility_lon)
    print("Distance:", round(distance, 2), "km")
import json


def find_nearest_facility(hotspot_lat, hotspot_lon):

    with open("industrial_facilities.json", "r") as file:
        facilities = json.load(file)

    nearest_facility = None
    shortest_distance = float("inf")

    for facility in facilities:

        distance = calculate_distance(
            hotspot_lat,
            hotspot_lon,
            facility["latitude"],
            facility["longitude"]
        )

        if distance < shortest_distance:
            shortest_distance = distance
            nearest_facility = facility

    return nearest_facility, shortest_distance
def get_firms_data():
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{NASA_KEY}/VIIRS_SNPP_NRT/68,6,98,38/1"

    response = requests.get(url)

    print("ANALYSIS NASA STATUS:", response.status_code)
    print("ANALYSIS NASA RESPONSE LENGTH:", len(response.text))

    if response.status_code != 200:
        print("FIRMS request failed:", response.text)
        return []

    import csv
    from io import StringIO

    csv_data = StringIO(response.text)
    reader = csv.DictReader(csv_data)

    data = list(reader)

    print("ANALYSIS FIRMS COUNT:", len(data))

    return data
def analyze_hotspot(hotspot):

    latitude = float(hotspot["latitude"])
    longitude = float(hotspot["longitude"])

    facility, distance = find_nearest_facility(
        latitude,
        longitude
    )
    result = {
    "latitude": latitude,
    "longitude": longitude,
    "frp": float(hotspot["frp"]),
    "confidence": hotspot["confidence"],
    "acq_time": hotspot["acq_time"],
    "nearest_facility": facility["name"],
    "facility_type": facility["type"],
    "distance_km": round(distance, 2)
    
}
    result["persistence_status"] = detect_persistence(result)
    return result
def classify_hotspot(result):

    distance = result["distance_km"]

    if distance <= 10:
        classification = "Possible Industrial Fire"
    else:
        classification = "Other Thermal Anomaly"

    result["classification"] = classification

    return result
def calculate_risk(result):

    distance = result["distance_km"]
    frp = result["frp"]

    if distance <= 10 and frp >= 20:
        risk = "HIGH"

    elif distance <= 25 or frp >= 10:
        risk = "MEDIUM"

    else:
        risk = "LOW"

    result["risk_level"] = risk

    return result
def detect_persistence(hotspot):
    frp = hotspot["frp"]

    if frp >= 15:
        return "Persistent Thermal Source"
    else:
        return "Single Thermal Anomaly"