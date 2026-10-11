"""Get the current weather for a city.

Usage:
    python weather.py <city name>

Example:
    python weather.py London
    python weather.py "New York"

Uses the free Open-Meteo API (no API key required).
"""

import json
import sys
import urllib.parse
import urllib.request

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}


def fetch_json(url, params):
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(full_url, timeout=10) as response:
        return json.load(response)


def get_city_location(city):
    data = fetch_json(GEOCODE_URL, {"name": city, "count": 1, "language": "en"})
    results = data.get("results")
    if not results:
        return None
    return results[0]


def get_weather(city):
    location = get_city_location(city)
    if location is None:
        raise ValueError(f"City '{city}' not found.")

    data = fetch_json(WEATHER_URL, {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                   "weather_code,wind_speed_10m",
        "timezone": "auto",
    })
    current = data["current"]

    return {
        "city": location["name"],
        "region": location.get("admin1", ""),
        "country": location.get("country", ""),
        "temperature": current["temperature_2m"],
        "feels_like": current["apparent_temperature"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "condition": WEATHER_CODES.get(current["weather_code"], "Unknown"),
        "time": current["time"],
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python weather.py <city name>")
        sys.exit(1)

    city = " ".join(sys.argv[1:])
    try:
        w = get_weather(city)
    except ValueError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching weather: {e}")
        sys.exit(1)

    place = ", ".join(p for p in (w["city"], w["region"], w["country"]) if p)
    print(f"Weather in {place} (local time {w['time']})")
    print(f"  Condition   : {w['condition']}")
    print(f"  Temperature : {w['temperature']} °C (feels like {w['feels_like']} °C)")
    print(f"  Humidity    : {w['humidity']} %")
    print(f"  Wind speed  : {w['wind_speed']} km/h")


if __name__ == "__main__":
    main()
