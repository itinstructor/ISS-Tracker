
"""
    Name: iis_tkintermapview.py
    Author: William A Loring
    Created: 11/09/2024
    Description: Track the International Space Station (ISS) using Tkinter and MapView
"""

# https://github.com/TomSchimansky/TkinterMapView
# pip install tkintermapview
from time import sleep
import tkintermapview as tkmap
import customtkinter as ctk
import requests
import threading
# https://wheretheiss.at/w/developer
URL = "https://api.wheretheiss.at/v1/satellites/25544?units=miles"
# http://open-notify.org/Open-Notify-API/ISS-Location-Now/
# URL_OPEN_NOTIFY = "http://api.open-notify.org/iss-now.json"


class ISSTracker:
    """A class to track and display the International Space Station's position on a map."""

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
            update_interval (int): How often to update the ISS position in milliseconds
        """
        self.width = window_width
        self.height = window_height

        self.update_interval = update_interval
        self.running = False
        self.update_thread = None
        self.count = 0

        # Set the appearance mode and default color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("ISS Tracker")

        # The WM_DELETE_WINDOW protocol is used to handle what happens
        # when the user clicks the close button of a window.
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

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
                self.latitude,
                self.longitude,
                text="ISS",
                marker_color_circle="red",
                marker_color_outside="darkblue"
            )

        except Exception as e:
            print(f"Error initializing marker: {e}")
            # Fall back to 0,0 if we can't get initial position
            self.marker = self.map.set_marker(
                0,
                0,
                text="ISS",
                marker_color_circle="red",
                marker_color_outside="black"
            )

# ------------------------- GET ISS POSITION ---------------------------- #
    def get_iss_position(self):
        """Fetch the current ISS position from the Open Notify API.

        Returns:
            dict: JSON response containing ISS position data
        """
        response = requests.get(URL)
        response.raise_for_status()
        position = response.json()

        # Extract coordinates
        # self.latitude = float(position.get("iss_position").get("latitude"))
        # self.longitude = float(position.get("iss_position").get("longitude"))

        self.latitude = float(position.get("latitude"))
        self.longitude = float(position.get("longitude"))

# -------------------- UPDATE ISS POSITION THREAD ------------------------ #
    def update_iss_position_thread(self):
        """Update the ISS marker position on the map."""
        while self.running:
            try:
                self.get_iss_position()

                self.count += 1
                self.lbl_count.configure(text=f" Count: {self.count} ")
                self.lbl_lat.configure(text=f" Latitude: {self.latitude:.4f} ")
                self.lbl_lon.configure(text=f" Longitude: {
                                       self.longitude:.4f} ")

                # Schedule GUI update on the main thread
                self.root.after(0, self.update_marker_position)

                sleep(self.update_interval)

            except Exception as e:
                print(f"Error updating ISS position: {e}")

# --------------------- UPDATE MARKER POSITION --------------------------- #
    def update_marker_position(self):
        """Update the marker position in the GUI thread."""
        if self.marker:
            self.marker.set_position(self.latitude, self.longitude)
            self.map.set_position(self.latitude, self.longitude)
        else:
            self.marker = self.map.set_marker(
                self.latitude,
                self.longitude,
                text="ISS",
                marker_color_circle="red",
                marker_color_outside="red"
            )

# ------------------------- CHANGE MAP ----------------------------------- #
    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map.set_tile_server(
                "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map.set_tile_server(
                "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
                max_zoom=22)
        elif new_map == "Google satellite":
            self.map.set_tile_server(
                "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
                max_zoom=22)

# ------------------------- RUN ------------------------------------------ #
    def run(self):
        """Start the ISS tracker application."""
        self.running = True

        # Start the update thread
        self.update_thread = threading.Thread(
            target=self.update_iss_position_thread,
            daemon=True
        )
        self.update_thread.start()

        # Start the main event loop
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
        self.map.set_position(self.latitude, self.longitude)
        self.map.set_zoom(5)
        self.map.pack(expand=True, fill="both")

        # Create status frame with modern styling
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.grid(row=0, column=1, padx=10,
                               pady=(10), sticky="nsew")

        # Create labels with CustomTkinter styling
        self.lbl_lat = ctk.CTkLabel(
            self.status_frame,
            text=f"Latitude: {self.latitude:.4f}",
            corner_radius=6,
            fg_color=("gray85", "gray25")
        )
        self.lbl_lon = ctk.CTkLabel(
            self.status_frame,
            text=f"Longitude: {self.longitude:.4f}",
            corner_radius=6,
            fg_color=("gray85", "gray25")
        )
        self.lbl_count = ctk.CTkLabel(
            self.status_frame,
            text="Count: 0",
            corner_radius=6,
            fg_color=("gray85", "gray25")
        )
        self.lbl_tile_server = ctk.CTkLabel(
            self.status_frame,
            text="Tile Server",
            corner_radius=6,
            fg_color=("gray85", "gray25")
        )

        self.map_option_menu = ctk.CTkOptionMenu(
            self.status_frame,
            values=["OpenStreetMap", "Google normal", "Google satellite"],
            command=self.change_map
        )

        # Grid layout for status labels
        self.lbl_lat.grid(
            row=0, column=0, padx=10, pady=10, sticky="ew"
        )
        self.lbl_lon.grid(
            row=1, column=0, padx=10, pady=10, sticky="ew"
        )
        self.lbl_count.grid(
            row=2, column=0, padx=10, pady=10, sticky="ew"
        )

        self.lbl_tile_server.grid(
            row=3, column=0, padx=10, pady=(40, 10), sticky="ew"
        )
        self.map_option_menu.grid(
            row=4, column=0, padx=10, pady=10, sticky="ew"
        )

        for child in self.status_frame.winfo_children():
            child.grid_configure(ipadx=1, ipady=1)

        # Bind the Escape key to the quit method
        self.root.bind("<Escape>", self.quit)

# ------------------------- QUIT ----------------------------------------- #
    def quit(self, *arts):
        """Stop the ISS tracker application."""
        self.running = False
        self.root.destroy()


def main():
    """Create and run the ISS tracker application."""
    tracker = ISSTracker()
    tracker.run()


if __name__ == "__main__":
    main()
