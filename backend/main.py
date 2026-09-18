from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
import csv
import json
from io import StringIO

from analysis import (
    get_firms_data as analysis_get_firms_data,
    analyze_all_hotspots
)

from clustering import generate_clusters

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NASA_KEY = os.getenv("NASA_FIRMS_MAP_KEY")


@app.get("/")
def home():
    return {
        "message": "ThermoSentinel Backend is running",
        "nasa_key_loaded": NASA_KEY is not None
    }


@app.get("/firms")
def get_firms():
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{NASA_KEY}/VIIRS_SNPP_NRT/68,6,98,38/5"

    response = requests.get(url)

    csv_data = StringIO(response.text)
    reader = csv.DictReader(csv_data)
    data = list(reader)

    print("NASA STATUS:", response.status_code)
    print("NASA HOTSPOTS:", len(data))

    return {
        "status": response.status_code,
        "count": len(data),
        "data": data
    }


@app.get("/facilities")
def get_facilities():

    from database import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            osm_id,
            osm_type,
            name,
            industrial_type,
            operator,
            website,
            latitude,
            longitude
        FROM osm_industrial_facilities
        ORDER BY name;
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    facilities = []

    for row in rows:

        osm_id, osm_type, name, industrial_type, operator, website, latitude, longitude = row

        facilities.append({
            "osm_id": osm_id,
            "osm_type": osm_type,
            "name": name,
            "type": industrial_type,
            "operator": operator,
            "website": website,
            "latitude": latitude,
            "longitude": longitude
        })

    return {
        "count": len(facilities),
        "facilities": facilities
    }
@app.get("/analyzed-hotspots")
def get_analyzed_hotspots():

    nasa_result = get_firms()

    hotspots = nasa_result["data"]

    results = analyze_all_hotspots(hotspots)

    return {
        "count": len(results),
        "hotspots": results
    }
@app.get("/clusters")
def get_clusters():

    nasa_result = analysis_get_firms_data()

    hotspots = nasa_result

    clusters = generate_clusters(hotspots)

    return {
        "count": len(clusters),
        "clusters": clusters
    }
@app.get("/incidents")
def get_incidents():

    hotspots = analysis_get_firms_data()

    clusters = generate_clusters(hotspots)

    incidents = []

    from cluster_intelligence import calculate_cluster_intelligence

    for cluster in clusters:

        intelligence = calculate_cluster_intelligence(cluster)

        incident = {
            "incident_id": cluster["cluster_id"],
            "observation_count": cluster["observation_count"],
            "center_latitude": cluster["center_latitude"],
            "center_longitude": cluster["center_longitude"],
            "maximum_frp": cluster["maximum_frp"],
            "average_frp": cluster["average_frp"],
            "start_date": cluster["start_date"],
            "end_date": cluster["end_date"],

            "intelligence_score": intelligence["intelligence_score"],
            "risk_level": intelligence["risk_level"],
            "industrial_link": intelligence["industrial_link"],
            "nearest_facility": intelligence["nearest_facility"],
            "facility_type": intelligence["facility_type"],
            "distance_km": intelligence["distance_km"],
            "persistence_days": intelligence["persistence_days"]
        }

        incidents.append(incident)

    return {
        "count": len(incidents),
        "incidents": incidents
    }