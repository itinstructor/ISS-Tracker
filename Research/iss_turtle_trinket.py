#!/bin/python3
# -*- coding: utf-8 -*-
"""
ISS Tracking Program (OOP Version)
---------------------------------
This program tracks the International Space Station (ISS) and displays:
- Current ISS location on a world map
- Number of people currently in space
- Names of astronauts grouped by their spacecraft
- Updates every 10 seconds

Classes:
    - ISSTracker: Main class handling the ISS tracking functionality
    - DisplayManager: Handles the turtle graphics and display elements
    - DataFetcher: Manages API calls and data retrieval
"""

import json
import urllib.request
import turtle
import time
from typing import Tuple, Dict, Any
START_Y = 85 # Starting position of text on the screen

class DataFetcher:
    """Handles all API calls and data retrieval operations"""

    # API endpoint URLs
    ISS_URL = 'http://api.open-notify.org/iss-now.json'
    ASTROS_URL = 'http://api.open-notify.org/astros.json'

    @staticmethod
    def get_iss_position() -> Tuple[float, float]:
        """
        Fetches current ISS position from the API
        Returns:
            tuple: (latitude, longitude) as float values
        """
        try:
            response = urllib.request.urlopen(DataFetcher.ISS_URL)
            iss_now = json.loads(response.read())
            location = iss_now['iss_position']
            return float(location['latitude']), float(location['longitude'])
        except Exception as e:
            print(f"Error fetching ISS position: {e}")
            return 0.0, 0.0

    @staticmethod
    def get_astronauts() -> Dict[str, Any]:
        """
        Fetches current astronaut data from the API
        Returns:
            dict: Containing number of astronauts and their details
        """
        try:
            response = urllib.request.urlopen(DataFetcher.ASTROS_URL)
            return json.loads(response.read())
        except Exception as e:
            print(f"Error fetching astronaut data: {e}")
            return {"number": 0, "people": []}


class DisplayManager:
    """Handles all turtle graphics and display elements"""

    def __init__(self):
        """Initialize the display components"""
        # Create and configure the main screen
        self.screen = turtle.Screen()
        self.screen.setup(720, 360)
        self.screen.setworldcoordinates(-180, -90, 180, 90)
        self.screen.bgpic('./img/map1.gif')
        self.screen.register_shape('./img/iss1.gif')

        # Create and configure the ISS turtle
        self.iss = turtle.Turtle()
        self.iss.shape('./img/iss1.gif')
        self.iss.setheading(90)
        self.iss.penup()

        # Create and configure the text turtle
        self.text = turtle.Turtle()
        self.text.penup()
        self.text.hideturtle()
        self.text.color('yellow')

    def update_iss_position(self, lon: float, lat: float) -> None:
        """Updates the ISS marker position on the map"""
        self.iss.goto(lon, lat)

    def write_astronaut_info(self, astros: Dict[str, Any]) -> None:
        """
        Writes astronaut information on the screen
        Args:
            astros: Dictionary containing astronaut data
        """
        # Clear previous text
        self.text.clear()

        # Start position for text (upper portion of screen)
        current_y = START_Y  # Adjusted starting position as requested

        # Write total count of people in space
        self.text.goto(-175, current_y)
        self.text.write(f'People in space: {astros["number"]}',
                        font=('Arial', 10, 'bold'))
        current_y -= 12

        # Group astronauts by spacecraft
        spacecraft_crews = {}
        for person in astros['people']:
            craft = person['craft']
            if craft not in spacecraft_crews:
                spacecraft_crews[craft] = []
            spacecraft_crews[craft].append(person['name'])

        # Write grouped information with compact spacing
        for craft, names in spacecraft_crews.items():
            # Write spacecraft name
            self.text.goto(-175, current_y)
            self.text.write(f'{craft}:', font=('Arial', 9, 'bold'))
            current_y -= 12

            # Write astronaut names under their spacecraft
            for name in names:
                self.text.goto(-165, current_y)
                self.text.write(f'• {name}', font=('Arial', 8, 'normal'))
                current_y -= 12


class ISSTracker:
    """Main class that coordinates tracking and display updates"""

    def __init__(self):
        """Initialize the tracker with its components"""
        self.display = DisplayManager()
        self.data_fetcher = DataFetcher()
        self.update_interval = 10  # seconds between updates

    def update_display(self) -> bool:
        """
        Updates all display elements with current data
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Get and update ISS position
            lat, lon = self.data_fetcher.get_iss_position()
            self.display.update_iss_position(lon, lat)
            print(f'Latitude: {lat}\nLongitude: {lon}')

            # Get and update astronaut information
            astros = self.data_fetcher.get_astronauts()
            self.display.write_astronaut_info(astros)

            # Print astronaut details to console
            print(f'People in Space: {astros["number"]}')
            for p in astros['people']:
                print(f'{p["name"]} in {p["craft"]}')

            return True

        except Exception as e:
            print(f"Error in update_display: {e}")
            return False

    def run(self) -> None:
        """Main loop that keeps the tracker running"""
        while True:
            try:
                self.update_display()
                self.display.screen.update()
                time.sleep(self.update_interval)

            except turtle.Terminator:
                print("Display window was closed")
                break

            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(self.update_interval)


def main():
    """Entry point of the program"""
    tracker = ISSTracker()
    tracker.run()


if __name__ == "__main__":
    main()
