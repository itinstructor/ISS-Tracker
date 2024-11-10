"""
    Name: geocode_geopy.py
    Author: William A Loring
    Created: 07/10/2021
    Purpose: Geocode using Nominatim from geopy
    pip install geopy
"""

from geopy.geocoders import Nominatim


def main():
    # For testing
    latitude, longitude, address = geocode()
    # For testing purposes
    print(address)
    print((latitude, longitude))
    address = reverse_geocode(latitude, longitude)
    print(f"Reverse GeoCode from Lat and Long")
    print(address)


def geocode():
    try:
        # Create geolocator object with Nominatim geocode service
        # Nominatim is a free geolocater that uses openstreetmaps.org
        geolocator = Nominatim(user_agent="location_practice")

        # Get location input from user
        city = input("Enter city: ")
        state = input("Enter state: ")
        country = input("Enter country: ")

        # Create location dictionary for request
        location = {
            "city": city,
            "state": state,
            "country": country
        }

        # Get location from geocode
        geo_location = geolocator.geocode(location)

        # Return geocode location information to calling program
        return (geo_location.latitude, geo_location.longitude, geo_location.address)
    except:
        print("An error occured while geocoding.")


def reverse_geocode(lat, lon):
    try:
        # Create geolocator object
        geolocator = Nominatim(user_agent="location_practice")
        # Create location tuple
        location = (lat, lon)
        # Get address with resolution of town
        address = geolocator.reverse(location, zoom=10)

        return address
    except:
        print("An error occured while reverse geocoding.")


# If a standalone program, call the main function
# Else, use as a module
if __name__ == '__main__':
    main()
