# mcp_server.py
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-server")

@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_response = requests.get(geo_url).json()

        if "results" not in geo_response:
            return f"Could not find location: {city}"

        lat = geo_response["results"][0]["latitude"]
        lon = geo_response["results"][0]["longitude"]

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
        )
        weather_response = requests.get(weather_url).json()
        temp = weather_response["current_weather"]["temperature"]
        wind = weather_response["current_weather"]["windspeed"]

        return f"The current temperature in {city} is {temp}°C with wind speed {wind} km/h."
    except Exception as e:
        return f"Weather error: {str(e)}"


if __name__ == "__main__":
    mcp.run()  # runs over stdio by default