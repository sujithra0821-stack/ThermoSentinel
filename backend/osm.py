import requests

url = "https://overpass-api.de/api/interpreter"

query = """
[out:json];
node["industrial"](20,68,38,98);
out;
"""

response = requests.post(url, data=query)

print("Status:", response.status_code)

if response.status_code == 200:
    data = response.json()
    elements = data["elements"]

    print("Industrial facilities found:", len(elements))

    for item in elements[:10]:
        print(
            item.get("lat"),
            item.get("lon"),
            item.get("tags", {}).get("name", "Unknown")
        )
else:
    print("OSM request failed")
    print(response.text[:500])