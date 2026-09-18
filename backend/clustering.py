import math
from datetime import datetime


def haversine_distance(lat1, lon1, lat2, lon2):

    R = 6371.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def date_difference(date1, date2):

    d1 = datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.strptime(date2, "%Y-%m-%d")

    return abs((d1 - d2).days)


def are_related(hotspot1, hotspot2):

    distance = haversine_distance(
        float(hotspot1["latitude"]),
        float(hotspot1["longitude"]),
        float(hotspot2["latitude"]),
        float(hotspot2["longitude"])
    )

    days = date_difference(
        hotspot1["acq_date"],
        hotspot2["acq_date"]
    )

    # Same thermal event if:
    # within 2 km AND within 1 day

    return distance <= 2 and days <= 1


def cluster_hotspots(hotspots):

    clusters = []

    for hotspot in hotspots:

        latitude = float(hotspot["latitude"])
        longitude = float(hotspot["longitude"])
        date = hotspot["acq_date"]

        assigned = False

        for cluster in clusters:

            # Cluster center
            center_latitude = cluster["center_latitude"]
            center_longitude = cluster["center_longitude"]

            # Check distance from cluster center
            distance = haversine_distance(
                latitude,
                longitude,
                center_latitude,
                center_longitude
            )

            # Check whether observation is from the same day
            same_day = date in cluster["dates"]

            if distance <= 2 and same_day:

                cluster["observations"].append(hotspot)
                cluster["dates"].add(date)

                # Recalculate cluster center
                total = len(cluster["observations"])

                cluster["center_latitude"] = sum(
                    float(h["latitude"])
                    for h in cluster["observations"]
                ) / total

                cluster["center_longitude"] = sum(
                    float(h["longitude"])
                    for h in cluster["observations"]
                ) / total

                assigned = True
                break

        if not assigned:

            clusters.append({
                "observations": [hotspot],
                "dates": {date},
                "center_latitude": latitude,
                "center_longitude": longitude
            })

    return [
        cluster["observations"]
        for cluster in clusters
    ]


def summarize_cluster(cluster, cluster_number):

    latitudes = [
        float(hotspot["latitude"])
        for hotspot in cluster
    ]

    longitudes = [
        float(hotspot["longitude"])
        for hotspot in cluster
    ]

    frps = [
        float(hotspot["frp"])
        for hotspot in cluster
    ]

    dates = [
        hotspot["acq_date"]
        for hotspot in cluster
    ]

    center_latitude = sum(latitudes) / len(latitudes)
    center_longitude = sum(longitudes) / len(longitudes)

    return {
        "cluster_id": f"TS-CL-{cluster_number:04d}",
        "observation_count": len(cluster),
        "center_latitude": round(center_latitude, 6),
        "center_longitude": round(center_longitude, 6),
        "maximum_frp": round(max(frps), 2),
        "average_frp": round(sum(frps) / len(frps), 2),
        "start_date": min(dates),
        "end_date": max(dates),
        "observations": cluster
    }

def generate_clusters(hotspots):

    raw_clusters = cluster_hotspots(hotspots)

    summaries = []

    for index, cluster in enumerate(raw_clusters, start=1):

        summary = summarize_cluster(
            cluster,
            index
        )

        summaries.append(summary)

    return summaries