"""
Filename: iss_location.py

Purpose: Track the International Space Station
References:
This program is written in Python 3.10 using Atom.io
    and Microsoft VS Code.
This program is modified from "joke_api.py"
    written by William Loring, WNCC.
https://nordicapis.com/11-space-apis-because-space-is-neat/
https://wheretheiss.at/w/developer
"""
import requests
import os

# Set this flag to False to only display the location.
# Otherwise it will display all the raw data from the API
# which can get messy. This is used for developement
# and testing.
TEST_FLAG = True
# This is the fully qualified web address for the API which
# tracks the current location of the ISS. This is where we
# will get our raw data from. Our ISS is a satellite with a
# NORAD reference number of 25544.
URL = "https://api.wheretheiss.at/v1/satellites/25544"

# The main() function is where the program will begin
# when it is called, or run.


def main():
    # This will create a loop so the user can ask for
    # more than one location.
    while True:
        # Call the location function. This means we will
        # go to another part of the program
        # to execute more code...
        get_iss_location()
        # ...then return to this point when it is done.
        # Once we return to this point, we will ask if
        # the user would like another location.
        print("\nWould you like another location?")
        # Recieve the answer and store it as the user choice.
        choice = input("[y] or [n] : ")
        # If the user presses 'n', exit the program.
        if choice == "n":
            break
        # Otherwise, clear the screen to begin again.
        os.system("cls" if os.name == "nt" else "clear")


def get_iss_location():
    # We are going to use the request's package '.get()'
    # function that we imported at the beginning to
    # assign the data we recieve to the location.
    location = requests.get(URL)
    # There is a status code returned when we request
    # from the server. We are looking for the code 200
    # which means we made a good connection.
    if (location.status_code == 200):
        # The data we recieve will be in JSON format. This
        # will convert the raw data into a Python dictionary
        # which will store the data in Key: Value pairs that
        # Python can then interpret.
        location_data = location.json()
        # This is our TEST_FLAG mentioned in line 24.
        # Right now we are showing all the data. If we
        # change this to False, we will only see the location
        # and the following code will not be executed. It
        # is True at this time, so execute the following code
        # through line 96.
        if (TEST_FLAG == True):
            # First, display the status code we recieved.
            print(f"\nStatus code: {location.status_code} \n")
            # Next, display the raw data from the request
            # we made of the API.
            print("Raw data from the API: ")
            print(location.text)
            # Next, display the Python dictionary that was
            # created on line 78. This will make the data
            # available to Python in a Python format.
            print("\nRaw data in a Python dictionary: ")
            print(location_data)

        # Now print the data from the dictionary created
        # from the raw API data that was in JSON format.
        print()  # This line just prints a blank line.
        # This line prints us the name of the target.
        print(f'Name: {location_data.get("name")}')
        
        # This line prints the current latitude of the ISS.
        print(f'Latitude: {location_data.get("latitude")}')
        # This line gives us the current longitude.
        print(f'Longitude: {location_data.get("longitude")}')
        
        # This line gives us it's altitude.
        print(
            f'Altitude: {location_data.get("altitude")} kilometers above sea level')
        # And this line gives us it's velocity. It is pretty fast!
        print(f'Velocity: {location_data.get("velocity")} kilometers per hour')
        # All of the previous code is taking place in a
        # conditional environment called an 'if' statement.
        # If the status code we recieved was NOT 200,
        # then the following code would be executed.
    else:
        print("Could not reach the server at this time.")


# Now that we have completed the code for the main()
# function and the get_iss_location() function,
# we need to call the main() function to actually
# run the program. The following code does this.
if __name__ == "__main__":
    main()
