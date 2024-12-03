"""
    Name: weather1.py
    Author: William A Loring
    Created: 12/10/2021
    Purpose: Get weather dictionary from OpenMeteo
"""
import requests
from datetime import datetime
from weather_utils import URL
from rich.console import Console
# Import Panel for title displays
from rich.panel import Panel
# Initialize rich.console
console = Console(highlight=False)


class OpenMeteo:
    def __init__(self):
        pass    
    def get_lat(self, lat):
        self.lat = lat

        # Build openmeteo request parameters
        # These are added on to the URL to make the complete request

        params = {
            "latitude": f"{self.lat}",
            "longitude": f"{self.lon}",
            "hourly": ["temperature_2m", "relativehumidity_2m", "wind_speed_10m"],
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "timezone": "America/Denver"
        }

        # Get the API JSON data as a Python requests object
        response = requests.get(
            URL,
            params=params
        )

        data = response.json()

        # Get current hour
        current_hour = datetime.now().hour

        # Print raw JSON data for demonstration
        # print(response.text)

        # Assuming the response contains an hourly list with 24 items, one for each hour of the day
        # And assuming the first item corresponds to the first hour of the current day in the specified timezone
        # This might need adjustment based on the actual structure and data of the response
        c_data = data['hourly']['temperature_2m'][current_hour], data['hourly'][
            'relativehumidity_2m'][current_hour], data['hourly'][
                'wind_speed_10m'][current_hour]

        # Print the current hour's temperature and relative humidity using Rich
        console.print("Current hour weather")
        console.print(f"     Temp: [bold cyan]{c_data[0]}°F[/bold cyan]")
        console.print(f" Humidity: [bold cyan]{c_data[1]}%[/bold cyan]")
        console.print(f"  Wind Sp: [bold cyan]{c_data[2]} mph[/bold cyan]")


def main():
    weather = OpenMeteo()
    # Hard code zip code location for testing
    # Get location input from user
    # Define hard coded location
    # Latitude and Longitude
    self.lat = 41.867600
    self.lon = -103.664170


if __name__ == "__main__":
    main()
