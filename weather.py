import requests
from datetime import datetime

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 8  # seconds to wait for the API
LANGUAGE = "en"  # language of city and country names


def geocode(city):
    """City name -> dict with name, country and coordinates (None if not found)."""
    response = requests.get(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": LANGUAGE, "format": "json"},
        timeout=TIMEOUT,
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
    
def fetch_forecast(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join([
            "temperature_2m", "relative_humidity_2m",
            "cloud_cover", "weather_code", "is_day",
        ]),
    }
    response = requests.get(FORECAST_URL, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()

def build_result(place, raw):
    cur = raw["current"]
    now = datetime.fromisoformat(cur["time"])
    current = {
        "temperature": round(cur["temperature_2m"]),
        "humidity": round(cur["relative_humidity_2m"]),
        "cloud_cover": round(cur["cloud_cover"]),
        "weekday": now.strftime("%A"),
    }
    return {
        "error": None,
        "city": {"name": place["name"], "country": place["country"]},
        "current": current,
    }

def get_weather(city):
    place = geocode(city)
    if place is None:
        return {"error": "city_not_found", "city": None, "current": None}
    raw = fetch_forecast(place["latitude"], place["longitude"])
    return build_result(place, raw)