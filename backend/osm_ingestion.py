import requests
from database import get_connection

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


# --------------------------------------------------
# OSM REGIONS
# Each region is downloaded separately so that
# Overpass does not receive one huge request.
# --------------------------------------------------

REGIONS = {
    "Chennai": (13.0, 80.0, 13.3, 80.4),

    "Bengaluru": (12.7, 77.4, 13.2, 77.9),

    "Hyderabad": (17.2, 78.1, 17.7, 78.7),

    "Mumbai": (18.8, 72.7, 19.4, 73.2),

    "Pune": (18.3, 73.6, 18.8, 74.1),

    "Ahmedabad": (22.8, 72.3, 23.3, 72.8),

    "Delhi_NCR": (28.3, 76.8, 29.0, 77.7),

    "Kolkata": (22.4, 87.9, 22.8, 88.6),

    "Visakhapatnam": (17.5, 82.8, 18.0, 83.5),

    "Coimbatore": (10.8, 76.7, 11.2, 77.2)
}


# --------------------------------------------------
# FETCH OSM DATA
# --------------------------------------------------

def fetch_osm_data(region_name, bbox):

    south, west, north, east = bbox

    query = f"""
    [out:json][timeout:60];

    nwr[industrial](
        {south},
        {west},
        {north},
        {east}
    );

    out center;
    """

    print()
    print("Fetching OSM data:", region_name)

    try:

        response = requests.post(
            OVERPASS_URL,
            data={"data": query},
            headers={
                "User-Agent": "ThermoSentinel/1.0"
            },
            timeout=90
        )

        print(
            "OSM response:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "OSM request failed for:",
                region_name
            )

            return []

        data = response.json()

        elements = data.get(
            "elements",
            []
        )

        print(
            "Features received:",
            len(elements)
        )

        return elements

    except Exception as error:

        print(
            "OSM error:",
            error
        )

        return []


# --------------------------------------------------
# GET COORDINATES
# --------------------------------------------------

def get_coordinates(element):

    if "lat" in element and "lon" in element:

        return (
            element["lat"],
            element["lon"]
        )

    center = element.get("center")

    if center:

        return (
            center["lat"],
            center["lon"]
        )

    return None, None


# --------------------------------------------------
# STORE OSM DATA
# --------------------------------------------------

def store_osm_data(elements):

    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0

    for element in elements:

        latitude, longitude = get_coordinates(
            element
        )

        if latitude is None or longitude is None:
            continue

        tags = element.get(
            "tags",
            {}
        )

        osm_id = element["id"]
        osm_type = element["type"]

        name = (
            tags.get("name")
            or tags.get("name:en")
        )

        industrial_type = tags.get(
            "industrial"
        )

        operator = tags.get(
            "operator"
        )

        website = tags.get(
            "website"
        )

        cursor.execute(
            """
            INSERT INTO osm_industrial_facilities
            (
                osm_id,
                osm_type,
                name,
                industrial_type,
                operator,
                website,
                latitude,
                longitude,
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
                ST_SetSRID(
                    ST_MakePoint(%s, %s),
                    4326
                )
            )

            ON CONFLICT
            (osm_id, osm_type)
            DO NOTHING
            """,

            (
                osm_id,
                osm_type,
                name,
                industrial_type,
                operator,
                website,
                latitude,
                longitude,
                longitude,
                latitude
            )
        )

        if cursor.rowcount == 1:

            inserted += 1

    conn.commit()

    cursor.close()
    conn.close()

    print(
        "New OSM facilities inserted:",
        inserted
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    total_regions = len(REGIONS)

    print(
        "ThermoSentinel OSM ingestion started"
    )

    print(
        "Regions:",
        total_regions
    )

    for region_name, bbox in REGIONS.items():

        elements = fetch_osm_data(
            region_name,
            bbox
        )

        if elements:

            store_osm_data(
                elements
            )

        else:

            print(
                "No data for:",
                region_name
            )

    print()
    print(
        "OSM ingestion completed."
    )