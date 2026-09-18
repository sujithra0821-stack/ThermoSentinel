from database import get_connection


def get_cluster_persistence(cluster):
    """
    Calculates real historical persistence using FIRMS observations
    stored in PostgreSQL/PostGIS.

    It checks the 7 days before the cluster's latest observation
    and looks for thermal observations within 1 km of the cluster center.
    """

    center_latitude = cluster["center_latitude"]
    center_longitude = cluster["center_longitude"]

    latest_date = max(
        hotspot["acq_date"]
        for hotspot in cluster["observations"]
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(DISTINCT acq_date)
        FROM firms_observations
        WHERE acq_date < %s::date
          AND acq_date >= %s::date - INTERVAL '7 days'
          AND ST_DWithin(
              geom::geography,
              ST_SetSRID(
                  ST_MakePoint(%s, %s),
                  4326
              )::geography,
              1000
          );
        """,
        (
            latest_date,
            latest_date,
            center_longitude,
            center_latitude
        )
    )

    previous_days = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    # Include the current detection day
    return previous_days + 1


def calculate_cluster_intelligence(cluster):
    """
    Calculates intelligence for a thermal cluster.

    This does NOT confirm a fire.

    It evaluates:
    - thermal intensity
    - number of observations
    - industrial proximity
    - historical persistence
    """

    maximum_frp = float(cluster["maximum_frp"])
    observation_count = cluster["observation_count"]

    # Calculate real historical persistence
    persistence_days = get_cluster_persistence(cluster)

    # ---------------------------------------------------------
    # FIND NEAREST INDUSTRIAL FACILITY
    # ---------------------------------------------------------

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
            cluster["center_longitude"],
            cluster["center_latitude"],
            cluster["center_longitude"],
            cluster["center_latitude"]
        )
    )

    facility = cursor.fetchone()

    cursor.close()
    conn.close()

    # ---------------------------------------------------------
    # INDUSTRIAL LINK
    # ---------------------------------------------------------

    if facility:

        facility_name, facility_type, distance_km = facility

        distance_km = round(distance_km, 2)

        # Consider industrial correlation only within 25 km
        industrial_link = distance_km <= 25

        nearest_facility = (
            facility_name
            if facility_name
            else "Unnamed OSM Facility"
        )

        facility_type = (
            facility_type
            if facility_type
            else "Industrial Facility"
        )

    else:

        distance_km = None
        industrial_link = False
        nearest_facility = None
        facility_type = None

    # ---------------------------------------------------------
    # INTELLIGENCE SCORE
    # ---------------------------------------------------------

    score = 0

    # Thermal intensity
    if maximum_frp >= 20:
        score += 40

    elif maximum_frp >= 10:
        score += 25

    elif maximum_frp >= 5:
        score += 15

    else:
        score += 5

    # Number of observations
    if observation_count >= 20:
        score += 30

    elif observation_count >= 10:
        score += 20

    elif observation_count >= 5:
        score += 10

    else:
        score += 5

    # Industrial proximity
    if industrial_link:
        score += 30

    # Historical persistence
    if persistence_days >= 3:
        score += 20

    elif persistence_days >= 2:
        score += 10

    # ---------------------------------------------------------
    # RISK LEVEL
    # ---------------------------------------------------------

    # Normalize score to 100
    score = min(score, 100)

    # Risk level
    if score >= 70:
        risk_level = "HIGH"

    elif score >= 40:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    # ---------------------------------------------------------
    # FINAL INTELLIGENCE RESULT
    # ---------------------------------------------------------

    return {
        "intelligence_score": score,
        "risk_level": risk_level,
        "industrial_link": industrial_link,
        "nearest_facility": nearest_facility,
        "facility_type": facility_type,
        "distance_km": distance_km,
        "persistence_days": persistence_days
    }