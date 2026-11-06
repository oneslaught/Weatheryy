import requests
from datetime import datetime, timedelta, timezone

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 8  # seconds to wait for the API
LANGUAGE = "en"  # language of city and country names
HOURS_SHOWN = 24  # length of the hourly forecast

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

def _round(value):
    return None if value is None else round(value)

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
            "cloud_cover", "weather_code", "is_day", "apparent_temperature", "surface_pressure", "wind_speed_10m", "uv_index", "visibility", "dewpoint_2m", 
        ]),
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset,sunrise,sunset",
        "hourly": "temperature_2m,precipitation_probability,weather_code,is_day",
        "forecast_days": 7,
        "timezone": "auto",
    }
    response = requests.get(FORECAST_URL, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()

def describe(code, is_day=True):
    description, icon = WEATHER_CODES.get(code, ("No data", "❔"))
    if not is_day and code in (0, 1):
        icon = "🌙"
    return description, icon

def build_result(place, raw):
    cur = raw["current"]
    now = datetime.fromisoformat(cur["time"])
    description, icon = describe(cur["weather_code"])
    local_now = datetime.now(timezone.utc) + timedelta(seconds=raw["utc_offset_seconds"])
    current = {
        "temperature": _round(cur["temperature_2m"]),
        "humidity": _round(cur["relative_humidity_2m"]),
        "cloud_cover": _round(cur["cloud_cover"]),
        "description": description,
        "icon": icon,
        "weekday": now.strftime("%A"),
        "real_feel": _round(cur["apparent_temperature"]),
        "pressure": _round(cur["surface_pressure"]),
        "wind_speed": _round(cur["wind_speed_10m"]),
        "uv_index": _round(cur["uv_index"]),
        "visibility": _round(cur["visibility"]/1000),
        "dew_point": _round(cur["dewpoint_2m"]),
        "local_time": local_now.strftime("%H:%M"),
        "local_date": f"{local_now.strftime('%B')} {local_now.day}",
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
            "max": _round(daily["temperature_2m_max"][i]),
            "min": _round(daily["temperature_2m_min"][i]),
            "rain" : daily["precipitation_probability_max"][i] or 0,
        })
        
    current["precipitation_probability"] = days[0]["rain"]
    current["sunrise"] = daily["sunrise"][0][11:16]
    current["sunset"] = daily["sunset"][0][11:16]
    h = raw["hourly"]
    current_hour = cur["time"][:13]  # e.g. "2026-10-28T01"
    start = next((i for i, t in enumerate(h["time"]) if t[:13] >= current_hour), 0)
    hourly = []
    for i in range(start, min(start + HOURS_SHOWN, len(h["time"]))):
        hour_description, hour_icon = describe(h["weather_code"][i], bool(h["is_day"][i]))
        hourly.append({
            "time": h["time"][i][11:16],  # "2026-10-28T01:00" =>> "01:00"
            "temperature": _round(h["temperature_2m"][i]),
            "precipitation_probability": _round(h["precipitation_probability"][i]),
            "description": hour_description,
            "icon": hour_icon,
        })
        
    return {
        "error": None,
        "city": {"name": place["name"], "country": place["country"]},
        "current": current,
        "daily": days,
        "hourly": hourly,
    }

def _error(code):
    return {
        "error": code,
        "city": None,
        "current": None,
        "hourly": [],
    }

def get_weather(city):
    try:
        place = geocode(city)
        if place is None:
            return _error("city_not_found")
        raw = fetch_forecast(place["latitude"], place["longitude"])
        return build_result(place, raw)
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as e:
        print("WEATHER ERROR:", repr(e))
        return _error("service_unavailable")