import requests

def geocode(city):
    """City name -> dict with name, country and coordinates (None if not found)."""
    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=8,
    )
    response.raise_for_status()
    data = response.json()
    # for instance: {"results": [{"name": "Riga", "country": "Latvia", "latitude": 56.95, "longitude": 24.1, ...}]}
    results = data.get("results")
    if not results:
        return None
    place = results[0]
    return {
        "name": place.get("name", city),
        "country": place.get("country", ""),
        "latitude": place["latitude"],
        "longitude": place["longitude"],
    }