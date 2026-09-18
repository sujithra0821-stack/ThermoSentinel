import requests
import csv
import os
from io import StringIO
from dotenv import load_dotenv

from database import get_connection

load_dotenv()

NASA_KEY = os.getenv("NASA_FIRMS_MAP_KEY")

NASA_URL = (
    f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
    f"{NASA_KEY}/VIIRS_SNPP_NRT/68,6,98,38/5"
)


def fetch_firms_data():
    print("Fetching NASA FIRMS data...")

    response = requests.get(NASA_URL, timeout=60)

    print("NASA response:", response.status_code)

    if response.status_code != 200:
        print("NASA FIRMS request failed")
        print(response.text)
        return []

    reader = csv.DictReader(StringIO(response.text))
    data = list(reader)

    print("NASA observations received:", len(data))

    return data


def store_firms_data(data):
    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0

    for row in data:
        latitude = float(row["latitude"])
        longitude = float(row["longitude"])

        cursor.execute(
            """
            INSERT INTO firms_observations
            (
                latitude,
                longitude,
                acq_date,
                acq_time,
                satellite,
                instrument,
                confidence,
                frp,
                geom
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            )
            ON CONFLICT DO NOTHING
            """,
            (
                latitude,
                longitude,
                row["acq_date"],
                row["acq_time"],
                row["satellite"],
                row["instrument"],
                row["confidence"],
                float(row["frp"]),
                longitude,
                latitude
            )
        )

        if cursor.rowcount == 1:
            inserted += 1

    conn.commit()

    cursor.close()
    conn.close()

    print("Records inserted into PostgreSQL:", inserted)


if __name__ == "__main__":
    data = fetch_firms_data()

    if data:
        store_firms_data(data)
    else:
        print("No FIRMS data to store.")