import requests
import folium

def get_air_quality_data(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid=45e8ea657c8ce688e2a924ab4cb2457c"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch air quality data for lat={lat}, lon={lon}. Error: {response.text}")
        return None

def create_map_with_air_quality_data():
    cities = [
        {"name": "Paris", "latitude": 48.8566, "longitude": 2.3522},
        {"name": "Islamabad", "latitude": 33.6844, "longitude": 73.0479},
        {"name": "Tehran", "latitude": 35.6892, "longitude": 51.3890},
        {"name": "Berlin", "latitude": 52.5200, "longitude": 13.4050},
        {"name": "Riyadh", "latitude": 24.7136, "longitude": 46.6753},
        {"name": "Beijing", "latitude": 39.9042, "longitude": 116.4074},
        {"name": "Washington", "latitude": 38.8951, "longitude": -77.0364},
        {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
        {"name": "Copenhagen", "latitude": 55.6761, "longitude": 12.5683},
        {"name": "Amsterdam", "latitude": 52.3676, "longitude": 4.9041},
        {"name": "Madrid", "latitude": 40.4168, "longitude": -3.7038},
        {"name": "London", "latitude": 51.5074, "longitude": -0.1278},
        {"name": "Brasilia", "latitude": -15.8267, "longitude": -47.9218},
        {"name": "Ottawa", "latitude": 45.4215, "longitude": -75.6972},
        {"name": "Brasilia", "latitude": -15.8267, "longitude": -47.9218},  # Brazil
        {"name": "Ottawa", "latitude": 45.4215, "longitude": -75.6972},  # Canada
        {"name": "Mexico City", "latitude": 19.4326, "longitude": -99.1332},  # Mexico
        {"name": "Buenos Aires", "latitude": -34.6037, "longitude": -58.3816},  # Argentina
        {"name": "Bogota", "latitude": 4.7110, "longitude": -74.0721},  # Colombia
        {"name": "Bern", "latitude": 46.9480, "longitude": 7.4474},  # Switzerland
        {"name": "Vienna", "latitude": 48.2082, "longitude": 16.3738},  # Austria
        {"name": "Canberra", "latitude": -35.2820, "longitude": 149.1286},  # Australia
        {"name": "Stockholm", "latitude": 59.3293, "longitude": 18.0686},  # Sweden
        {"name": "Brussels", "latitude": 50.8503, "longitude": 4.3517},  # Belgium
        {"name": "Kiev", "latitude": 50.4501, "longitude": 30.5234},  # Ukraine
        {"name": "Moscow", "latitude": 55.7558, "longitude": 37.6176},  # Russia
        {"name": "Tokyo", "latitude": 35.6895, "longitude": 139.6917},  # Japan
        {"name": "Bangkok", "latitude": 13.7563, "longitude": 100.5018},  # Thailand
        {"name": "New Delhi", "latitude": 28.6139, "longitude": 77.2090},  # India
        {"name": "Hong Kong", "latitude": 22.3193, "longitude": 114.1694},  # Hong Kong
        {"name": "Seoul", "latitude": 37.5665, "longitude": 126.9780},  # South Korea
        {"name": "Pyongyang", "latitude": 39.0392, "longitude": 125.7625},  # North Korea
        {"name": "Baghdad", "latitude": 33.3152, "longitude": 44.3661},  # Iraq
        {"name": "Damascus", "latitude": 33.5138, "longitude": 36.2765},  # Syria
        {"name": "Kuwait City", "latitude": 29.3759, "longitude": 47.9774},  # Kuwait
        {"name": "Manama", "latitude": 26.2285, "longitude": 50.5860},  # Bahrain
        {"name": "Amman", "latitude": 31.9522, "longitude": 35.2332},  # Jordan
        {"name": "Abu Dhabi", "latitude": 24.4539, "longitude": 54.3773},  # United Arab Emirates
        {"name": "Kabul", "latitude": 34.5553, "longitude": 69.2075},  # Afghanistan
        {"name": "Baku", "latitude": 40.4093, "longitude": 49.8671},  # Azerbaijan
        {"name": "Ankara", "latitude": 39.9334, "longitude": 32.8597},  # Turkey
        {"name": "Abuja", "latitude": 9.0765, "longitude": 7.3986},  # Nigeria
        {"name": "Cairo", "latitude": 30.0444, "longitude": 31.2357},  # Egypt
        {"name": "Rabat", "latitude": 34.0209, "longitude": -6.8415},  # Morocco
        {"name": "Algiers", "latitude": 36.7372, "longitude": 3.0870},  # Algeria
        {"name": "Pretoria", "latitude": -25.7463, "longitude": 28.1876},  # South Africa
        {"name": "Kinshasa", "latitude": -4.4419, "longitude": 15.2663},  # Congo
        {"name": "Helsinki", "latitude": 60.1695, "longitude": 24.9354},  # Finland
        {"name": "Dublin", "latitude": 53.3498, "longitude": -6.2603},  # Ireland
        {"name": "Oslo", "latitude": 59.9139, "longitude": 10.7522},  # Norway
        {"name": "Rome", "latitude": 41.9028, "longitude": 12.4964},  # Italy
        {"name": "Warsaw", "latitude": 52.2297, "longitude": 21.0122},  # Poland
        {"name": "Zagreb", "latitude": 45.8150, "longitude": 15.9819},  # Croatia
        {"name": "Niamey", "latitude": 13.5127, "longitude": 2.1126},  # Niger
        {"name": "Tripoli", "latitude": 32.8872, "longitude": 13.1913},  # Libya
        {"name": "Kampala", "latitude": 0.3476, "longitude": 32.5825},  # Uganda
        {"name": "Bamako", "latitude": 12.6392, "longitude": -8.0029},  # Mali
        {"name": "Khartoum", "latitude": 15.5007, "longitude": 32.5599},  # Sudan
        {"name": "Sucre", "latitude": -19.0196, "longitude": -65.2619},  # Bolivia
        # Add capitals here
        # Format: {"name": "City", "latitude": latitude_value, "longitude": longitude_value}
    ]

    m = folium.Map(location=[20, 0], zoom_start=2)


    for city in cities:
        data = get_air_quality_data(city['latitude'], city['longitude'], "YOUR_OPENWEATHERMAP_API_KEY")
        if data and 'list' in data and len(data['list']) > 0:
            pollutants = data['list'][0]['components']
            popup_text = f"City: {city['name']}<br>PM2.5: {pollutants.get('pm2_5')}<br>PM10: {pollutants.get('pm10')}<br>NO2: {pollutants.get('no2')}"
            folium.Marker([city['latitude'], city['longitude']], popup=folium.Popup(popup_text, max_width=1000)).add_to(m)
        else:
            folium.Marker([city['latitude'], city['longitude']], popup=f"No data available for {city['name']}").add_to(m)

    m.save("air_quality_map_cities.html")
    print("Map created. Please open 'air_quality_map_cities.html' in your web browser to view.")

if __name__ == "__main__":
    create_map_with_air_quality_data()
