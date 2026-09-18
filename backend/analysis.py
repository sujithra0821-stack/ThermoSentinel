import requests
import os
import csv
from io import StringIO
from dotenv import load_dotenv

from database import get_connection

load_dotenv()

NASA_KEY = os.getenv("NASA_FIRMS_MAP_KEY")

print("NASA KEY LOADED:", NASA_KEY is not None)


# --------------------------------------------------
# NASA FIRMS DATA
# --------------------------------------------------

def get_firms_data():

    url = (
        f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
        f"{NASA_KEY}/VIIRS_SNPP_NRT/68,6,98,38/5"
    )

    response = requests.get(url)

    print("ANALYSIS NASA STATUS:", response.status_code)
    print("ANALYSIS NASA RESPONSE LENGTH:", len(response.text))

    if response.status_code != 200:
        print("FIRMS request failed:", response.text)
        return []

    csv_data = StringIO(response.text)
    reader = csv.DictReader(csv_data)

    data = list(reader)

    print("ANALYSIS FIRMS COUNT:", len(data))

    return data


# --------------------------------------------------
# FIND NEAREST INDUSTRIAL FACILITY
# USING POSTGRESQL + POSTGIS
# --------------------------------------------------

def find_nearest_facility(hotspot_lat, hotspot_lon):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            name,
            industrial_type,
            ST_Distance(
                geom::geography,
                ST_SetSRID(
                    ST_MakePoint(%s, %s),
                    4326
                )::geography
            ) / 1000 AS distance_km
        FROM osm_industrial_facilities
        WHERE geom IS NOT NULL
        ORDER BY
            geom::geography <->
            ST_SetSRID(
                ST_MakePoint(%s, %s),
                4326
            )
        LIMIT 1;
        """,
        (
            hotspot_lon,
            hotspot_lat,
            hotspot_lon,
            hotspot_lat
        )
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result is None:
        return None, None

    name, industrial_type, distance_km = result

    facility = {
        "name": name or "Unnamed OSM Facility",
        "type": industrial_type or "Industrial Facility"
    }

    return facility, round(distance_km, 2)


# --------------------------------------------------
# REAL TEMPORAL PERSISTENCE
# --------------------------------------------------

def detect_persistence(hotspot, cursor):

    latitude = hotspot["latitude"]
    longitude = hotspot["longitude"]
    acq_date = hotspot["acq_date"]

    cursor.execute(
        """
        SELECT COUNT(DISTINCT previous.acq_date)
        FROM firms_observations previous
        WHERE previous.acq_date < %s::date
          AND previous.acq_date >= %s::date - INTERVAL '7 days'
          AND ST_DWithin(
              previous.geom::geography,
              ST_SetSRID(
                  ST_MakePoint(%s, %s),
                  4326
              )::geography,
              1000
          );
        """,
        (
            acq_date,
            acq_date,
            longitude,
            latitude
        )
    )

    previous_days = cursor.fetchone()[0]

    if previous_days >= 2:
        return "Persistent Thermal Source"

    return "Single Thermal Anomaly"


# --------------------------------------------------
# CLASSIFICATION
# --------------------------------------------------

def classify_hotspot(result):

    distance = result["distance_km"]

    if distance is not None and distance <= 10:
        classification = "Possible Industrial Fire"
    else:
        classification = "Other Thermal Anomaly"

    result["classification"] = classification

    return result


# --------------------------------------------------
# RISK CALCULATION
# --------------------------------------------------

def calculate_risk(result):

    distance = result["distance_km"]
    frp = result["frp"]

    if distance is not None and distance <= 10 and frp >= 20:

        risk = "HIGH"

    elif (distance is not None and distance <= 25) or frp >= 10:

        risk = "MEDIUM"

    else:

        risk = "LOW"

    result["risk_level"] = risk

    return result


# --------------------------------------------------
# ANALYZE ALL NASA HOTSPOTS
# --------------------------------------------------

def analyze_all_hotspots(hotspots):

    conn = get_connection()
    cursor = conn.cursor()

    results = []

    for hotspot in hotspots:

        latitude = float(hotspot["latitude"])
        longitude = float(hotspot["longitude"])
        frp = float(hotspot["frp"])

        # Find nearest real OSM industrial facility

        cursor.execute(
            """
            SELECT
                name,
                industrial_type,
                ST_Distance(
                    geom::geography,
                    ST_SetSRID(
                        ST_MakePoint(%s, %s),
                        4326
                    )::geography
                ) / 1000 AS distance_km
            FROM osm_industrial_facilities
            WHERE geom IS NOT NULL
            ORDER BY
                geom::geography <->
                ST_SetSRID(
                    ST_MakePoint(%s, %s),
                    4326
                )
            LIMIT 1;
            """,
            (
                longitude,
                latitude,
                longitude,
                latitude
            )
        )

        facility_result = cursor.fetchone()

        if facility_result:

            name, industrial_type, distance_km = facility_result

            distance_km = round(distance_km, 2)

            if distance_km <= 25:

                nearest_facility = name or "Unnamed OSM Facility"

                facility_type = (
                    industrial_type
                    or "Industrial Facility"
                )

            else:

                nearest_facility = None
                facility_type = None

        else:

            nearest_facility = None
            facility_type = None
            distance_km = None

        # Build analysis result

        result = {

            "latitude": latitude,

            "longitude": longitude,

            "frp": frp,

            "confidence": hotspot["confidence"],

            "acq_date": hotspot["acq_date"],

            "acq_time": hotspot["acq_time"],

            "nearest_facility": nearest_facility,

            "facility_type": facility_type,

            "distance_km": distance_km
        }

        # Real temporal persistence

        result["persistence_status"] = detect_persistence(
            result,
            cursor
        )

        # Classification

        result = classify_hotspot(result)

        # Risk

        result = calculate_risk(result)

        results.append(result)

    cursor.close()
    conn.close()

    return results