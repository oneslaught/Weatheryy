import requests
from datetime import datetime

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 8  # seconds to wait for the API
LANGUAGE = "en"  # language of city and country names

# WMO weather code (description, icon)
WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Drizzle", "🌦️"),
    55: ("Heavy drizzle", "🌦️"),
    56: ("Freezing drizzle", "🌧️"),
    57: ("Heavy freezing drizzle", "🌧️"),
    61: ("Light rain", "🌧️"),
    63: ("Rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Freezing rain", "🌧️"),
    67: ("Heavy freezing rain", "🌧️"),
    71: ("Light snow", "🌨️"),
    73: ("Snow", "🌨️"),
    75: ("Heavy snow", "🌨️"),
    77: ("Snow grains", "🌨️"),
    80: ("Light showers", "🌦️"),
    81: ("Showers", "🌦️"),
    82: ("Heavy showers", "🌦️"),
    85: ("Snow showers", "🌨️"),
    86: ("Heavy snow showers", "🌨️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}

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
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "forecast_days": 7,
        "timezone": "auto",
    }
    response = requests.get(FORECAST_URL, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()

def describe(code):
    return WEATHER_CODES.get(code, ("No data", "❔"))

def build_result(place, raw):
    cur = raw["current"]
    now = datetime.fromisoformat(cur["time"])
    description, icon = describe(cur["weather_code"])
    current = {
        "temperature": round(cur["temperature_2m"]),
        "humidity": round(cur["relative_humidity_2m"]),
        "cloud_cover": round(cur["cloud_cover"]),
        "description": description,
        "icon": icon,
        "weekday": now.strftime("%A"),
    }
    
    daily = raw["daily"]
    days = []
    for i, date in enumerate(daily["time"]):
        description, icon = describe(daily["weather_code"][i])
        d = datetime.fromisoformat(date)
        if i == 0:
            weekday = "Today"
        else:
            weekday =d.strftime("%A")
        days.append({
            "weekday": weekday,
            "date": f"{d.strftime('%B')} {d.day}",
            "description": description,
            "icon": icon,
            "max": round(daily["temperature_2m_max"][i]),
            "min": round(daily["temperature_2m_min"][i]),
            "rain" : daily["precipitation_probability_max"][i] or 0,
        })
        
    return {
        "error": None,
        "city": {"name": place["name"], "country": place["country"]},
        "current": current,
        "daily": days,
    }

def get_weather(city):
    place = geocode(city)
    if place is None:
        return {"error": "city_not_found", "city": None, "current": None, "daily": None}
    raw = fetch_forecast(place["latitude"], place["longitude"])
    return build_result(place, raw)