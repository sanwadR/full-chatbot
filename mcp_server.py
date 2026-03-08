# mcp_server.py
import os
import sys
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Use __file__ so the subprocess always finds .env regardless of cwd
_HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_HERE, ".env"))

mcp = FastMCP("weather-server")

OWM_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "").strip()
OWM_BASE = "https://api.openweathermap.org"


def _log(msg: str):
    """Print to stderr so MCP's stdout transport is not corrupted."""
    print(f"[MCP] {msg}", file=sys.stderr, flush=True)


# ──────────────────────────────────────────────
# Internal helper
# ──────────────────────────────────────────────

def _geocode(city: str):
    """Return (lat, lon, resolved_name) or None if the city is not found."""
    url = f"{OWM_BASE}/geo/1.0/direct?q={city}&limit=1&appid={OWM_KEY}"
    data = requests.get(url, timeout=10).json()
    # API can return an error dict instead of a list on bad key / rate-limit
    if not isinstance(data, list) or len(data) == 0:
        return None
    r = data[0]
    return r["lat"], r["lon"], r.get("name", city)


# ──────────────────────────────────────────────
# Tool 1 – Geocode a city
# ──────────────────────────────────────────────

@mcp.tool()
def geocode_city(city: str) -> str:
    """Return the latitude, longitude, and country for a given city name."""
    _log(f"geocode_city called | city={city!r}")
    try:
        result = _geocode(city)
        if result is None:
            result_str = f"Could not find location: {city}"
        else:
            lat, lon, name = result
            result_str = f"{name}: latitude={lat}, longitude={lon}"
        _log(f"geocode_city returned | {result_str}")
        return result_str
    except Exception as e:
        err = f"Geocoding error: {e}"
        _log(f"geocode_city ERROR | {err}")
        return err


# ──────────────────────────────────────────────
# Tool 2 – Current weather by city name
# ──────────────────────────────────────────────

@mcp.tool()
def get_weather_by_city(city: str) -> str:
    """Get the current weather conditions for a city by name."""
    _log(f"get_weather_by_city called | city={city!r}")
    url = f"{OWM_BASE}/data/2.5/weather?q={city}&appid={OWM_KEY}&units=metric"
    try:
        data = requests.get(url, timeout=10).json()
        if str(data.get("cod")) != "200":
            err = f"Error: {data.get('message', 'Unknown error')}"
            _log(f"get_weather_by_city ERROR | {err}")
            return err

        name = data["name"]
        country = data["sys"]["country"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"].capitalize()
        wind = data["wind"]["speed"]
        visibility = data.get("visibility", None)
        vis_str = f"{visibility / 1000:.1f} km" if visibility else "N/A"

        result = (
            f"Current weather in {name}, {country}:\n"
            f"  Condition  : {desc}\n"
            f"  Temperature: {temp}°C (feels like {feels_like}°C)\n"
            f"  Humidity   : {humidity}%\n"
            f"  Wind Speed : {wind} m/s\n"
            f"  Visibility : {vis_str}"
        )
        _log(f"get_weather_by_city returned | {name}, {country} — {temp}°C, {desc}")
        return result
    except Exception as e:
        err = f"Weather error: {e}"
        _log(f"get_weather_by_city ERROR | {err}")
        return err


# ──────────────────────────────────────────────
# Tool 3 – Current weather by coordinates
# ──────────────────────────────────────────────

@mcp.tool()
def get_weather_by_coordinates(lat: float, lon: float) -> str:
    """Get the current weather conditions for a location by latitude and longitude."""
    _log(f"get_weather_by_coordinates called | lat={lat}, lon={lon}")
    url = f"{OWM_BASE}/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_KEY}&units=metric"
    try:
        data = requests.get(url, timeout=10).json()
        if str(data.get("cod")) != "200":
            err = f"Error: {data.get('message', 'Unknown error')}"
            _log(f"get_weather_by_coordinates ERROR | {err}")
            return err

        name = data["name"]
        country = data["sys"]["country"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"].capitalize()
        wind = data["wind"]["speed"]

        result = (
            f"Current weather at ({lat}, {lon}) — {name}, {country}:\n"
            f"  Condition  : {desc}\n"
            f"  Temperature: {temp}°C (feels like {feels_like}°C)\n"
            f"  Humidity   : {humidity}%\n"
            f"  Wind Speed : {wind} m/s"
        )
        _log(f"get_weather_by_coordinates returned | {name}, {country} — {temp}°C, {desc}")
        return result
    except Exception as e:
        err = f"Weather error: {e}"
        _log(f"get_weather_by_coordinates ERROR | {err}")
        return err


# ──────────────────────────────────────────────
# Tool 4 – Hourly forecast (up to 48 h)
# ──────────────────────────────────────────────

@mcp.tool()
def get_hourly_forecast(city: str, hours: int = 24) -> str:
    """Get an hourly weather forecast for a city (up to 48 hours ahead)."""
    _log(f"get_hourly_forecast called | city={city!r}, hours={hours}")
    try:
        result = _geocode(city)
        if result is None:
            err = f"Could not find location: {city}"
            _log(f"get_hourly_forecast ERROR | {err}")
            return err
        lat, lon, name = result
    except Exception as e:
        err = f"Geocoding error: {e}"
        _log(f"get_hourly_forecast ERROR | {err}")
        return err
    hours = max(1, min(hours, 48))

    url = (
        f"{OWM_BASE}/data/3.0/onecall?"
        f"lat={lat}&lon={lon}&exclude=minutely,daily,alerts"
        f"&appid={OWM_KEY}&units=metric"
    )
    try:
        data = requests.get(url, timeout=10).json()
        if "hourly" not in data:
            err = f"Error: {data.get('message', 'Could not retrieve hourly forecast')}"
            _log(f"get_hourly_forecast ERROR | {err}")
            return err

        lines = [f"Hourly forecast for {name} (next {hours} hours):"]
        for h in data["hourly"][:hours]:
            dt = datetime.fromtimestamp(h["dt"], tz=timezone.utc).strftime("%Y-%m-%d %H:00 UTC")
            temp = h["temp"]
            desc = h["weather"][0]["description"].capitalize()
            pop = int(h.get("pop", 0) * 100)
            lines.append(f"  {dt}  {temp:>5.1f}°C  {desc}  (Rain {pop}%)")

        result = "\n".join(lines)
        _log(f"get_hourly_forecast returned | {name}, {hours} slots")
        return result
    except Exception as e:
        err = f"Forecast error: {e}"
        _log(f"get_hourly_forecast ERROR | {err}")
        return err


# ──────────────────────────────────────────────
# Tool 5 – Daily forecast (up to 8 days)
# ──────────────────────────────────────────────

@mcp.tool()
def get_daily_forecast(city: str, days: int = 7) -> str:
    """Get a daily weather forecast for a city (up to 8 days ahead)."""
    _log(f"get_daily_forecast called | city={city!r}, days={days}")
    try:
        result = _geocode(city)
        if result is None:
            err = f"Could not find location: {city}"
            _log(f"get_daily_forecast ERROR | {err}")
            return err
        lat, lon, name = result
    except Exception as e:
        err = f"Geocoding error: {e}"
        _log(f"get_daily_forecast ERROR | {err}")
        return err
    days = max(1, min(days, 8))

    url = (
        f"{OWM_BASE}/data/3.0/onecall?"
        f"lat={lat}&lon={lon}&exclude=minutely,hourly,alerts"
        f"&appid={OWM_KEY}&units=metric"
    )
    try:
        data = requests.get(url, timeout=10).json()
        if "daily" not in data:
            err = f"Error: {data.get('message', 'Could not retrieve daily forecast')}"
            _log(f"get_daily_forecast ERROR | {err}")
            return err

        lines = [f"Daily forecast for {name} (next {days} days):"]
        for d in data["daily"][:days]:
            dt = datetime.fromtimestamp(d["dt"], tz=timezone.utc).strftime("%Y-%m-%d")
            temp_day = d["temp"]["day"]
            temp_min = d["temp"]["min"]
            temp_max = d["temp"]["max"]
            desc = d["weather"][0]["description"].capitalize()
            humidity = d["humidity"]
            pop = int(d.get("pop", 0) * 100)
            lines.append(
                f"  {dt}  {desc}  "
                f"Day {temp_day:.1f}°C  Min {temp_min:.1f}°C / Max {temp_max:.1f}°C  "
                f"Humidity {humidity}%  Rain {pop}%"
            )

        result = "\n".join(lines)
        _log(f"get_daily_forecast returned | {name}, {days} days")
        return result
    except Exception as e:
        err = f"Forecast error: {e}"
        _log(f"get_daily_forecast ERROR | {err}")
        return err


# ──────────────────────────────────────────────
# Tool 6 – Air pollution / AQI
# ──────────────────────────────────────────────

@mcp.tool()
def get_air_pollution(city: str) -> str:
    """Get air quality index (AQI) and key pollutant concentrations for a city."""
    _log(f"get_air_pollution called | city={city!r}")
    try:
        result = _geocode(city)
        if result is None:
            err = f"Could not find location: {city}"
            _log(f"get_air_pollution ERROR | {err}")
            return err
        lat, lon, name = result
    except Exception as e:
        err = f"Geocoding error: {e}"
        _log(f"get_air_pollution ERROR | {err}")
        return err

    url = f"{OWM_BASE}/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OWM_KEY}"
    try:
        data = requests.get(url, timeout=10).json()
        if "list" not in data or not data["list"]:
            err = f"Could not retrieve air pollution data for {city}"
            _log(f"get_air_pollution ERROR | {err}")
            return err

        item = data["list"][0]
        aqi = item["main"]["aqi"]
        aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        c = item["components"]

        result = (
            f"Air quality in {name}:\n"
            f"  AQI  : {aqi} — {aqi_labels.get(aqi, 'Unknown')}\n"
            f"  CO   : {c.get('co', 'N/A')} μg/m³\n"
            f"  NO₂  : {c.get('no2', 'N/A')} μg/m³\n"
            f"  O₃   : {c.get('o3', 'N/A')} μg/m³\n"
            f"  PM2.5: {c.get('pm2_5', 'N/A')} μg/m³\n"
            f"  PM10 : {c.get('pm10', 'N/A')} μg/m³\n"
            f"  SO₂  : {c.get('so2', 'N/A')} μg/m³\n"
            f"  NH₃  : {c.get('nh3', 'N/A')} μg/m³"
        )
        _log(f"get_air_pollution returned | {name}, AQI={aqi} ({aqi_labels.get(aqi, 'Unknown')})")
        return result
    except Exception as e:
        err = f"Air pollution error: {e}"
        _log(f"get_air_pollution ERROR | {err}")
        return err


if __name__ == "__main__":
    mcp.run()  # runs over stdio by default