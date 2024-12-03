def get_wmo_weather_description(code):
    """
    Returns the description for a given WMO Weather interpretation code.

    Args:
        code (int): WMO Weather interpretation code

    Returns:
        str: Description of the weather code, or None if no matching code is found
    """
    wmo_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Drizzle: Light intensity",
        53: "Drizzle: Moderate intensity",
        55: "Drizzle: Dense intensity",
        56: "Freezing Drizzle: Light intensity",
        57: "Freezing Drizzle: Dense intensity",
        61: "Rain: Slight intensity",
        63: "Rain: Moderate intensity",
        65: "Rain: Heavy intensity",
        66: "Freezing Rain: Light intensity",
        67: "Freezing Rain: Heavy intensity",
        71: "Snow fall: Slight intensity",
        73: "Snow fall: Moderate intensity",
        75: "Snow fall: Heavy intensity",
        77: "Snow grains",
        80: "Rain showers: Slight intensity",
        81: "Rain showers: Moderate intensity",
        82: "Rain showers: Violent intensity",
        85: "Snow showers: Slight intensity",
        86: "Snow showers: Heavy intensity",
        95: "Thunderstorm: Slight or moderate",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }

    return wmo_codes.get(code, None)

# Example usage


def main():
    # Test some codes
    test_codes = [0, 2, 55, 67, 95, 99, 100]

    for code in test_codes:
        description = get_wmo_weather_description(code)
        if description:
            print(f"Code {code}: {description}")
        else:
            print(f"Code {code}: No description found")


if __name__ == "__main__":
    main()
