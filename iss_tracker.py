
"""
    Name: iis_tkintermapview.py
    Author: William A Loring
    Created: 11/09/2024
    Description: Track the International Space Station (ISS) using Tkinter and MapView
"""

# https://github.com/TomSchimansky/TkinterMapView
# pip install tkintermapview
import tkintermapview as tkmap
from base64 import b64decode
from time import sleep
import customtkinter as ctk
from PIL import ImageTk
import requests
import threading
from iis_icon import ICON_16
from iis_icon import ICON_32

# https://wheretheiss.at/w/developer
URL = "https://api.wheretheiss.at/v1/satellites/25544?units=miles"


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
                marker_color_outside="darkblue"
            )

# ------------------------- GET ISS POSITION ---------------------------- #
    def get_iss_position(self):
        """Fetch the current ISS position from API."""
        # Get the current ISS position from the API
        response = requests.get(URL)

        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse the JSON response to a Python dictionary
        position = response.json()

        # Extract the latitude and longitude from the response
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
                self.lbl_lon.configure(
                    text=f" Longitude: {self.longitude:.4f} "
                )

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
        """Change the map tile server based on the selected option."""
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

        # Create the thread to update the ISS position
        self.update_thread = threading.Thread(
            target=self.update_iss_position_thread,
            daemon=True
        )
        
        # Start the thread
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
