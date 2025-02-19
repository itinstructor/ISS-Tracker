import requests
from datetime import datetime
from wmo_codes import get_wmo_weather_description


def get_weather(lat, lng):
    params = {
        "latitude": f"{lat}",
        "longitude": f"{lng}",
        "hourly": [
            "temperature_2m",
            "relativehumidity_2m",
            "wind_speed_10m",
            "surface_pressure",
            "cloud_cover",
            "is_day"
        ],
        "minutely_15": ["weather_code"],
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "pressure_unit": "hPa",
        "timezone": "America/Denver"
    }

    # URL to access current Open-Meteo weather for a location
    URL = "https://api.open-meteo.com/v1/forecast?"
    # Get the API JSON data as a Python requests object
    response = requests.get(
        URL,
        params=params
    )

    data = response.json()

    # Get current hour
    current_hour = datetime.now().hour

    # Assuming the response contains an hourly list with 24 items,
    # one for each hour of the day, And assuming the first item
    # corresponds to the first hour of the current day in the specified timezone
    # This might need adjustment based on the actual structure and data of the response
    wmo_code = data['minutely_15']['weather_code'][current_hour]
    description = get_wmo_weather_description(wmo_code)

    temp = data['hourly']['temperature_2m'][current_hour]
    humidity = data['hourly']['relativehumidity_2m'][current_hour]
    wind_speed = data['hourly']['wind_speed_10m'][current_hour]
    pressure = data['hourly']['surface_pressure'][current_hour]
    pressure = round(pressure * 0.029529983071445, 2)
    cloud_cover = data['hourly']['cloud_cover'][current_hour]
    day = data['hourly']['is_day'][current_hour]
    if day == 1:
        day = "Daytime"
    else:
        day = "Nighttime"

    # Return the weather data as a dictionary
    return {
        "description": description,
        "temp": temp,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "pressure": pressure,
        "cloud_cover": cloud_cover,
        "day": day
    }
