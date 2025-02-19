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
from requests import get
# pip install pillow
from PIL import ImageTk
# pip install tkinter-tooltip
from tktooltip import ToolTip
from base64 import b64decode
from time import sleep
from threading import Thread
from iss_icon import ICON_16
from iss_icon import ICON_32
from ctk_horizontal_spinbox import CTkHorizontalSpinbox
from openmeteo import get_weather

# https://wheretheiss.at/w/developer
URL = "https://api.wheretheiss.at/v1/satellites/25544?units=miles"

BIG_GAP = 40
SMALL_GAP = 10
TINY_GAP = 0


class ISSTracker:
    """Track and display the International Space Station's position on a map."""

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

# -------------------------INITIALIZE MARKER ------------------------------- #
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

# -------------------- UPDATE ISS POSITION THREAD -------------------------- #
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

# --------------------- UPDATE MARKER POSITION ----------------------------- #
    def update_marker_position(self) -> None:
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

# ------------------------- CHANGE MAP ------------------------------------- #
    def change_map(self, new_map: str) -> None:
        """Change the map tile server based on the selected option."""
        if new_map == "OpenStreetMap":
            self.map.set_tile_server(
                "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
            )

        elif new_map == "Google Normal":
            self.map.set_tile_server(
                "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
                max_zoom=22
            )

        elif new_map == "Google Satellite":
            self.map.set_tile_server(
                "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
                max_zoom=22
            )

        # Add OpenRailwayMap tile server
        if new_map == "OpenRailwayMap":
            self.map.set_overlay_tile_server(
                "http://a.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png"
            )

# ------------------------- CHANGE UPDATE INTERVAL ------------------------- #
    def change_update_interval(self, new_interval: str = None) -> None:
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

# ------------------------- GET WEATHER ------------------------------------ #
    def get_weather(self):
        weather_data = get_weather(self.lat, self.lng)

        self.lbl_description.configure(text=f"{weather_data['description']}")
        self.lbl_display_temp.configure(text=f"{weather_data['temp']}°F")
        self.lbl_display_humidity.configure(
            text=f"{weather_data['humidity']}%")
        self.lbl_display_wind.configure(
            text=f"{weather_data['wind_speed']} mph")
        self.lbl_display_pressure.configure(
            text=f"{weather_data['pressure']} inHg")
        self.lbl_display_cloud_cover.configure(
            text=f"{weather_data['cloud_cover']}%")
        self.lbl_display_day.configure(text=f"{weather_data['day']}")

# --------------------------- RUN ------------------------------------------ #
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

# --------------------------- CREATE WIDGETS ------------------------------- #
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

        # Replace interval entry and button with custom spinbox
        self.interval_spinbox = CTkHorizontalSpinbox(
            self.status_frame,
            min_value=5,     # Minimum 10 seconds
            max_value=300,    # Maximum 5 minutes
            initial_value=self.update_interval,
            command=self.change_update_interval
        )
        ToolTip(self.interval_spinbox, "Select update interval in seconds")

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
            values=["OpenStreetMap", "Google Normal",
                    "Google Satellite"],
            command=self.change_map
        )
        ToolTip(self.map_option_menu, "Select a map tile server")

        # self.map_overlay_menu = ctk.CTkOptionMenu(
        #     self.status_frame,
        #     values=["", "OpenRailwayMap"],
        #     command=self.change_map
        # )
        # ToolTip(self.map_option_menu, "Select an overlay map tile server")

        # Grid layout for status labels
        self.lbl_lat.grid(
            row=0, column=0, columnspan=2, padx=SMALL_GAP, pady=SMALL_GAP, sticky="ew"
        )
        self.lbl_lng.grid(
            row=1, column=0, columnspan=2, padx=SMALL_GAP, pady=10, sticky="ew"
        )

        self.interval_spinbox.grid(
            row=2, column=0, columnspan=2, padx=10, pady=(40, 10), sticky="ew"
        )
        self.lbl_interval.grid(
            row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew"
        )
        self.lbl_count.grid(
            row=4, column=0, columnspan=2, padx=10, pady=(10, 40), sticky="ew"
        )

        self.lbl_tile_server.grid(
            row=5, column=0, columnspan=2, padx=10, pady=(10), sticky="ew"
        )
        self.map_option_menu.grid(
            row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew"
        )
        # self.map_overlay_menu.grid(
        #     row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

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
