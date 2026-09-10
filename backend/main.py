from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
import csv
import json
from io import StringIO

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
def get_firms_data():

    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{NASA_KEY}/VIIRS_SNPP_NRT/68,6,98,38/1"

    response = requests.get(url)

    csv_data = StringIO(response.text)

    reader = csv.DictReader(csv_data)

    data = list(reader)

    return {
        "status": response.status_code,
        "count": len(data),
        "data": data
    }
@app.get("/facilities")
def get_facilities():

    with open("industrial_facilities.json", "r") as file:
        facilities = json.load(file)

    return {
        "count": len(facilities),
        "facilities": facilities
    }
@app.get("/facilities")
def get_facilities():

    with open("industrial_facilities.json", "r") as file:
        facilities = json.load(file)

    return {
        "count": len(facilities),
        "facilities": facilities
    }
from analysis import get_firms_data, analyze_hotspot, classify_hotspot, calculate_risk


@app.get("/analyzed-hotspots")
def get_analyzed_hotspots():

    hotspots = get_firms_data()

    results = []

    for hotspot in hotspots:
        result = analyze_hotspot(hotspot)
        result = classify_hotspot(result)
        result = calculate_risk(result)
        results.append(result)

    return {
        "count": len(results),
        "hotspots": results
    }