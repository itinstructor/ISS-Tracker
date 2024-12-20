"""
    Name: iis_tracker.py
    Author: William A Loring
    Created: 11/09/2024
    Description: Track the International Space Station (ISS) using Tkinter
    and TkinterMapView
    Claude.ai used as a code helper
"""
# https://github.com/TomSchimansky/CustomTkinter
# pip install customtkinter
import customtkinter as ctk
# https://github.com/TomSchimansky/TkinterMapView
# pip install tkintermapview
import tkintermapview as tkmap
# pip install requests
import requests
from requests import get
# pip install pillow
from PIL import ImageTk
# pip install tkinter-tooltip
from tktooltip import ToolTip
from base64 import b64decode
from time import sleep
from datetime import datetime
from threading import Thread
from wmo_codes import get_wmo_weather_description
from iss_icon import ICON_16
from iss_icon import ICON_32
from ctk_horizontal_spinbox import CTkHorizontalSpinbox

# https://wheretheiss.at/w/developer
URL = "https://api.wheretheiss.at/v1/satellites/25544?units=miles"

BIG_GAP = 40
SMALL_GAP = 10
TINY_GAP = 0


class ISSTracker:
    """Class to track and display the International Space Station's position on a map."""

    def __init__(
        self,
            window_width=1024 * 2,
            window_height=768 * 2,
            update_interval=10
    ):
        """Initialize the ISS tracker application.

        Args:
            window_width (int): Width of the map window in pixels
            window_height (int): Height of the map window in pixels
            update_interval (int): How often to update the ISS position in seconds
        """
        self.width = window_width
        self.height = window_height

        # Set the appearance mode and default color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("ISS Tracker")
        self.root.geometry("+50+50")

        # Set the window and taskbar icon
        small_icon = ImageTk.PhotoImage(data=b64decode(ICON_16))
        large_icon = ImageTk.PhotoImage(data=b64decode(ICON_32))
        self.root.wm_iconbitmap()
        self.root.iconphoto(False, large_icon, small_icon)

        # The WM_DELETE_WINDOW protocol is used to handle what happens
        # when the user clicks the close button of a window.
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        # Initialize the ISS position and update interval
        self.update_interval = update_interval
        self.running = False
        self.update_thread = None
        self.count = 0

        # LIst to track previous positions for drawing lines
        self.previous_positions = []

        self.marker = None
        self.get_iss_position()

        # Create the main application widgets
        self.create_widgets()

        # Initialize marker with current ISS position
        self.initialize_marker()

# -------------------------INITIALIZE MARKER ----------------------------- #
    def initialize_marker(self):
        """Create the initial ISS marker with the current ISS position."""
        try:
            # Create marker with red color
            self.marker = self.map.set_marker(
                self.lat,                  # X coordinage
                self.lng,                 # Y coordinate
                text="ISS",                     # Text to display on marker
                marker_color_circle="red",      # Circle color
                marker_color_outside="darkblue"  # Outside color
            )
            # Add initial position to previous positions
            self.previous_positions.append((self.lat, self.lng))

        except Exception as e:
            print(f"Error initializing marker: {e}")
            # Fall back to 0,0 if we can't get initial position
            self.marker = self.map.set_marker(
                0,
                0,
                text="ISS",
                marker_color_circle="red",
                marker_color_outside="darkblue"
            )
            self.previous_positions.append((0, 0))

# ------------------------- GET ISS POSITION ---------------------------- #
    def get_iss_position(self):
        """Fetch the current ISS position from API."""
        # Get the current ISS position from the API
        response = get(URL)

        # Check for HTTP errors
        response.raise_for_status()

        # Parse the JSON response to a Python dictionary
        position = response.json()

        # Extract the latitude and longitude from the response
        self.lat = float(position.get("latitude"))
        self.lng = float(position.get("longitude"))

# -------------------- UPDATE ISS POSITION THREAD ------------------------ #
    def update_iss_position_thread(self):
        """Update the ISS marker position on the map."""
        while self.running:
            try:
                self.get_iss_position()
                # Update the position count
                self.count += 1
                self.lbl_count.configure(text=f" Count: {self.count} ")
                self.lbl_lat.configure(text=f" Latitude: {self.lat:.4f} ")
                self.lbl_lng.configure(
                    text=f" Longitude: {self.lng:.4f} "
                )

                # Get the current weather
                self.get_weather()

                # Schedule GUI update on the main thread
                # This will keep the GUI responsive while updating the marker
                self.root.after(0, self.update_marker_position)

                # Sleep the thread for the update interval before the next update
                sleep(self.update_interval)

            except Exception as e:
                print(f"Error updating ISS position: {e}")

# --------------------- UPDATE MARKER POSITION --------------------------- #
    def update_marker_position(self):
        """Update the marker and map position in the GUI thread."""
        if self.marker:
            # Draw line from previous position
            if self.previous_positions:
                last_pos = self.previous_positions[-1]
                # Add a line to show the path
                self.map.set_path(
                    [last_pos,               # Previous position
                     (self.lat, self.lng)    # Current position
                     ],
                    color="blue",            # Line color
                    width=3                  # Line width
                )

            # Update marker and map position
            self.marker.set_position(self.lat, self.lng)
            self.map.set_position(self.lat, self.lng)

            # Add new position to tracking list
            self.previous_positions.append((self.lat, self.lng))

        else:
            self.marker = self.map.set_marker(
                self.lat,
                self.lng,
                text="ISS",
                marker_color_circle="red",
                marker_color_outside="red"
            )
            self.previous_positions.append((self.lat, self.lng))

# ------------------------- CHANGE MAP ----------------------------------- #
    def change_map(self, new_map: str):
        """Change the map tile server based on the selected option."""
        if new_map == "OpenStreetMap":
            self.map.set_tile_server(
                "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
            )

        elif new_map == "Google normal":
            self.map.set_tile_server(
                "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
                max_zoom=22
            )

        elif new_map == "Google satellite":
            self.map.set_tile_server(
                "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
                max_zoom=22
            )

# ------------------------- CHANGE UPDATE INTERVAL ----------------------- #
    def change_update_interval(self, new_interval: str = None):
        """
        Change the update interval for ISS position tracking.

        Change the update interval.

        :param value: The new interval value
        If no value passed, get from spinbox
        """
        try:
            if new_interval is None:
                new_interval = self.interval_spinbox.get()

            interval = int(new_interval)
            if interval > 0:
                self.update_interval = interval
                self.lbl_interval.configure(
                    text=f" Update Interval: {interval} seconds "
                )
            else:
                raise ValueError("Interval must be a positive integer")
        except ValueError:
            print("Invalid update interval. Please enter a positive number.")
        except Exception as e:
            print(f"Error changing update interval: {e}")

# ------------------------- GET WEATHER ---------------------------------- #
    def get_weather(self):
        params = {
            "latitude": f"{self.lat}",
            "longitude": f"{self.lng}",
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

        # Print raw JSON data for demonstration
        # print(response.text)

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

        #  console.print(f"     Temp: [bold cyan]{c_data[0]}°F[/bold cyan]")
        # console.print(f" Humidity: [bold cyan]{c_data[1]}%[/bold cyan]")
        # console.print(f"  Wind Sp: [bold cyan]{c_data[2]} mph[/bold cyan]")
        self.lbl_description.configure(text=f"{description}")
        self.lbl_display_temp.configure(text=f"{temp}°F")
        self.lbl_display_humidity.configure(text=f"{humidity}%")
        self.lbl_display_wind.configure(text=f"{wind_speed} mph")
        self.lbl_display_pressure.configure(text=f"{pressure} inHg")
        self.lbl_display_cloud_cover.configure(text=f"{cloud_cover}%")
        self.lbl_display_day.configure(text=f"{day}")

# ------------------------- RUN ------------------------------------------ #
    def run(self):
        """Start the ISS tracker application."""
        self.running = True

        # Create the thread to update the ISS position
        self.update_thread = Thread(
            target=self.update_iss_position_thread,
            daemon=True     # This stops the thread on program exit
        )

        # Start the thread
        self.update_thread.start()

        # Start the main event loop of the program
        self.root.mainloop()

# ------------------------- CREATE WIDGETS ------------------------------- #
    def create_widgets(self):
        """Create the main application widgets."""
        # Create main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Create map frame
        self.map_frame = ctk.CTkFrame(self.main_frame)
        self.map_frame.grid(row=0, column=0, padx=10, pady=10)

        # Create map widget
        self.map = tkmap.TkinterMapView(
            self.map_frame,
            width=self.width,
            height=self.height,
            corner_radius=2
        )
        self.map.set_position(self.lat, self.lng)
        self.map.set_zoom(5)
        self.map.pack(expand=True, fill="both")

        # Create status frame with modern styling
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.grid(
            row=0, column=1, padx=10,
            pady=(10), sticky="nsew"
        )

        # Create labels with CustomTkinter styling
        self.lbl_lat = ctk.CTkLabel(
            self.status_frame,
            text=f"Latitude: {self.lat:.4f}",
            corner_radius=6,
            fg_color=("gray85", "gray25")
        )
        self.lbl_lng = ctk.CTkLabel(
            self.status_frame,
            text=f"Longitude: {self.lng:.4f}",
            corner_radius=6,
            fg_color=("gray85", "gray25")
        )
        self.lbl_count = ctk.CTkLabel(
            self.status_frame,
            text="Count: 0",
            corner_radius=6,
            fg_color=("gray85", "gray25")
        )
        self.lbl_interval = ctk.CTkLabel(
            self.status_frame,
            text=f"Update Interval: {self.update_interval} seconds",
            corner_radius=6,
            fg_color=("gray85", "gray25")
        )
        self.lbl_tile_server = ctk.CTkLabel(
            self.status_frame,
            text="Tile Server",
            corner_radius=6,
            fg_color=("gray85", "gray25")
        )

        # Create option menus
        self.map_option_menu = ctk.CTkOptionMenu(
            self.status_frame,
            values=["OpenStreetMap", "Google Normal", "Google Satellite"],
            command=self.change_map
        )
        ToolTip(self.map_option_menu, "Select a map tile server")

        # Replace interval entry and button with custom spinbox
        self.interval_spinbox = CTkHorizontalSpinbox(
            self.status_frame,
            min_value=5,     # Minimum 10 seconds
            max_value=300,    # Maximum 5 minutes
            initial_value=self.update_interval,
            command=self.change_update_interval
        )
        self.interval_spinbox.grid(
            row=6, column=0, columnspan=2, padx=10, pady=(40, 10), sticky="ew"
        )
        ToolTip(self.interval_spinbox, "Select update interval in seconds")

        # Grid layout for status labels
        self.lbl_lat.grid(
            row=0, column=0, columnspan=2, padx=SMALL_GAP, pady=SMALL_GAP, sticky="ew"
        )
        self.lbl_lng.grid(
            row=1, column=0, columnspan=2, padx=SMALL_GAP, pady=10, sticky="ew"
        )

        self.lbl_count.grid(
            row=2, column=0, columnspan=2, padx=10, pady=(40, 10), sticky="ew"
        )
        self.lbl_interval.grid(
            row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew"
        )

        self.lbl_tile_server.grid(
            row=4, column=0, columnspan=2, padx=10, pady=(40, 10), sticky="ew"
        )
        self.map_option_menu.grid(
            row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew"
        )

    # ---------------------- WEATHER LABELS ------------------------------ #
        self.lbl_description = ctk.CTkLabel(
            self.status_frame, anchor="center", wraplength=300
        )
        self.lbl_description.grid(
            row=8, column=0, padx=10, columnspan=2,
            pady=(BIG_GAP, TINY_GAP), sticky="ew"
        )

        self.lbl_temp = ctk.CTkLabel(
            self.status_frame,
            text="Temperature:", anchor="e"
        )
        self.lbl_temp.grid(
            row=9, column=0, padx=10, pady=(TINY_GAP), sticky="e"
        )

        self.lbl_display_temp = ctk.CTkLabel(
            self.status_frame, anchor="w"
        )
        self.lbl_display_temp.grid(
            row=9, column=1, padx=10, pady=(TINY_GAP), sticky="w"
        )

        self.lbl_humidity = ctk.CTkLabel(
            self.status_frame,
            text="Humidity:", anchor="e"
        )
        self.lbl_humidity.grid(
            row=10, column=0, padx=10,
            pady=(TINY_GAP), sticky="e")

        self.lbl_display_humidity = ctk.CTkLabel(
            self.status_frame, anchor="w"
        )
        self.lbl_display_humidity.grid(
            row=10, column=1, padx=10,
            pady=(TINY_GAP), sticky="w"
        )

        self.lbl_wind = ctk.CTkLabel(
            self.status_frame,
            text="Wind Speed:", anchor="e"
        )
        self.lbl_wind.grid(
            row=11, column=0, padx=10,
            pady=(TINY_GAP), sticky="e")

        self.lbl_display_wind = ctk.CTkLabel(
            self.status_frame, anchor="w"
        )
        self.lbl_display_wind.grid(
            row=11, column=1, padx=10,
            pady=(TINY_GAP), sticky="w")

        self.lbl_pressure = ctk.CTkLabel(
            self.status_frame,
            text="Pressure:", anchor="e"
        )

        self.lbl_pressure.grid(
            row=12, column=0, padx=10,
            pady=(TINY_GAP), sticky="e")

        self.lbl_display_pressure = ctk.CTkLabel(
            self.status_frame, anchor="w"
        )
        self.lbl_display_pressure.grid(
            row=12, column=1, padx=10,
            pady=(TINY_GAP), sticky="w")

        self.lbl_cloud_cover = ctk.CTkLabel(
            self.status_frame,
            text="Cloud Cover:", anchor="e"
        )
        self.lbl_cloud_cover.grid(
            row=13, column=0, padx=10,
            pady=(TINY_GAP), sticky="e")

        self.lbl_display_cloud_cover = ctk.CTkLabel(
            self.status_frame, anchor="w"
        )

        self.lbl_display_cloud_cover.grid(
            row=13, column=1, padx=10,
            pady=(TINY_GAP), sticky="w"
        )

        self.lbl_day = ctk.CTkLabel(
            self.status_frame,
            text="Day/Night:", anchor="e"
        )
        self.lbl_day.grid(
            row=14, column=0, padx=10,
            pady=(TINY_GAP, SMALL_GAP), sticky="e")

        self.lbl_display_day = ctk.CTkLabel(
            self.status_frame,
            anchor="w"
        )
        self.lbl_display_day.grid(
            row=14, column=1, padx=10, pady=(TINY_GAP, SMALL_GAP), sticky="w")

    # ---------------------- QUIT BUTTON --------------------------------- #
        self.btn_quit = ctk.CTkButton(
            self.status_frame,
            text="Quit",
            command=self.quit
        )
        ToolTip(self.btn_quit, "Press the Escape key to quit")
        self.btn_quit.grid(
            row=15, column=0, padx=10,
            pady=(BIG_GAP, SMALL_GAP), sticky="ew", columnspan=2
        )

        for child in self.status_frame.winfo_children():
            child.grid_configure(ipadx=1, ipady=1)

        # Bind the Escape key to the quit method
        self.root.bind("<Escape>", self.quit)

# ------------------------- QUIT ----------------------------------------- #
    def quit(self, *arts):
        """Stop the ISS tracker application."""
        self.running = False
        # Closes the main application window by destroying the root window
        self.root.destroy()


def main():
    """Create and run the ISS tracker application."""
    tracker = ISSTracker()
    tracker.run()


if __name__ == "__main__":
    main()
