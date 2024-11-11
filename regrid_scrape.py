import requests
import csv
import time

# Your API Key
API_KEY = 'AIzaSyALb-2Rrmt34nrOuIGla2cv0i0zOlB7qfI'  # Replace with your API key

# Dictionary containing street names and their corresponding center coordinates (latitude, longitude)
streets_coordinates = {
    'liberty ave': (40.4625, -79.9514),
    'penn ave': (40.4669, -79.9602),
    'butler st': (40.4702, -79.9610),
    '34th st': (40.4679, -79.9675),
    '35th st': (40.4684, -79.9680),
    '36th st': (40.4689, -79.9686),
    '37th st': (40.4695, -79.9692),
    '38th st': (40.4700, -79.9698),
    '39th st': (40.4705, -79.9703),
    '40th st': (40.4710, -79.9709),
    '41st st': (40.4715, -79.9715),
    '42nd st': (40.4720, -79.9720),
    '43rd st': (40.4725, -79.9726),
    '44th st': (40.4730, -79.9731),
    '45th st': (40.4735, -79.9736),
    '46th st': (40.4740, -79.9742),
    '47th st': (40.4745, -79.9747),
    '48th st': (40.4750, -79.9753),
    'Plummer st': (40.4755, -79.9758),
    '49th st': (40.4760, -79.9763),
    '50th st': (40.4765, -79.9768),
    '51st st': (40.4770, -79.9773),
    'Stanton ave': (40.4775, -79.9778),
    '52nd st': (40.4780, -79.9783),
    'McCandless ave': (40.4785, -79.9788),
    '53rd st': (40.4790, -79.9793),
    '54th st': (40.4795, -79.9798),
    '55th st': (40.4800, -79.9803),
    '56th st': (40.4805, -79.9808),
    'Hatfield st': (40.4810, -79.9813),
    'Fisk st': (40.4815, -79.9818),
    'Smallman st': (40.4820, -79.9823),
    'Main st': (40.4825, -79.9828),
    'Charlotte': (40.4830, -79.9833)
}


# Set a smaller radius for more detailed searches
RADIUS = 500  # 500 meters for smaller, more precise searches

# CSV file name
csv_file = 'lawrenceville_businesses.csv'

# Specify the headers for the CSV
headers = ['Street', 'Name', 'Address', 'Rating', 'Place ID', 'Latitude', 'Longitude']

# A set to track unique Place IDs
unique_place_ids = set()

# Function to search businesses along a specific street and handle pagination
def search_businesses(api_key, location, radius):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f'{location[0]},{location[1]}',  # Latitude, Longitude
        'radius': radius,
        'key': api_key
    }
    
    all_results = []
    while True:
        response = requests.get(url, params=params)
        results = response.json().get('results', [])
        all_results.extend(results)
        
        # Print the number of results retrieved in this batch
        print(f"Retrieved {len(results)} results")
        
        # Check if there's a next_page_token for additional results
        next_page_token = response.json().get('next_page_token')
        if next_page_token:
            print("Next page token found, fetching more results...")
            params['pagetoken'] = next_page_token
            # Delay to ensure the next page token is activated
            time.sleep(3)  # Increasing sleep time to ensure the token is ready
        else:
            print("No more pages.")
            break
    
    return all_results

# Open the CSV file for writing
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Write the header row
    writer.writerow(headers)
    
    # Loop through each street and collect business data
    for street, coordinates in streets_coordinates.items():
        print(f"Searching for businesses along {street}...")
        
        # Perform multiple smaller searches along the same street by shifting the center points
        for offset in range(-2, 3):  # Offset to cover adjacent areas along the street
            offset_lat = coordinates[0] + (offset * 0.0015)  # Adjust latitude slightly
            offset_lng = coordinates[1] + (offset * 0.0015)  # Adjust longitude slightly
            businesses = search_businesses(API_KEY, (offset_lat, offset_lng), RADIUS)
            
            for business in businesses:
                place_id = business.get('place_id', 'N/A')
                
                # Check if this place ID has already been written (to avoid duplicates)
                if place_id not in unique_place_ids:
                    unique_place_ids.add(place_id)  # Add the place ID to the set

                    name = business.get('name', 'N/A')
                    address = business.get('vicinity', 'N/A')
                    rating = business.get('rating', 'N/A')
                    latitude = business['geometry']['location'].get('lat', 'N/A')
                    longitude = business['geometry']['location'].get('lng', 'N/A')

                    # Write each unique business row
                    writer.writerow([street, name, address, rating, place_id, latitude, longitude])

print(f"Data has been saved to {csv_file}, with no duplicates and all available pages.")