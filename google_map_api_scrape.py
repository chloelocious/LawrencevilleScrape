import requests
import csv
import pandas as pd
import time

# Your API Key
API_KEY = 'AIzaSyALb-2Rrmt34nrOuIGla2cv0i0zOlB7qfI'  # Replace with your actual API key

# # Dictionary containing street names and their corresponding center coordinates (latitude, longitude)
# streets_coordinates = {
#     'Liberty Ave': (40.4625, -79.9514),
#     'Penn Ave': (40.4669, -79.9602),
#     'Butler St': (40.4702, -79.9610),
#     '34th St': (40.4679, -79.9675),
#     '35th St': (40.4684, -79.9680),
#     '36th St': (40.4689, -79.9686),
#     '37th St': (40.4695, -79.9692),
#     '38th St': (40.4700, -79.9698),
#     '39th St': (40.4705, -79.9703),
#     '40th St': (40.4710, -79.9709),
#     '41st St': (40.4715, -79.9715),
#     '42nd St': (40.4720, -79.9720),
#     '43rd St': (40.4725, -79.9726),
#     '44th St': (40.4730, -79.9731),
#     '45th St': (40.4735, -79.9736),
#     '46th St': (40.4740, -79.9742),
#     '47th St': (40.4745, -79.9747),
#     '48th St': (40.4750, -79.9753),
#     'Plummer St': (40.4755, -79.9758),
#     '49th St': (40.4760, -79.9763),
#     '50th St': (40.4765, -79.9768),
#     '51st St': (40.4770, -79.9773),
#     'Stanton Ave': (40.4775, -79.9778),
#     '52nd St': (40.4780, -79.9783),
#     'McCandless Ave': (40.4785, -79.9788),
#     '53rd St': (40.4790, -79.9793),
#     '54th St': (40.4795, -79.9798),
#     '55th St': (40.4800, -79.9803),
#     '56th St': (40.4805, -79.9808),
#     'Hatfield St': (40.4810, -79.9813),
#     'Fisk St': (40.4815, -79.9818),
#     'Smallman St': (40.4820, -79.9823),
#     'Main St': (40.4825, -79.9828),
#     'Charlotte': (40.4830, -79.9833)
# }

# # Set a smaller radius for more detailed searches
# RADIUS = 300  # Reduce radius to 300 meters to avoid hitting the 60-result limit

# # CSV file name
# csv_file = 'lawrenceville_businesses_broad.csv'

# # Specify the headers for the CSV
# headers = ['Street', 'Name', 'Address', 'Rating', 'Place ID', 'Latitude', 'Longitude']

# # A set to track unique Place IDs
# unique_place_ids = set()

# # Function to search businesses along a specific street and handle pagination
# def search_businesses(api_key, location, radius):
#     url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
#     params = {
#         'location': f'{location[0]},{location[1]}',  # Latitude, Longitude
#         'radius': radius,
#         'key': api_key
#     }
    
#     all_results = []
#     while True:
#         response = requests.get(url, params=params)
#         results = response.json().get('results', [])
#         all_results.extend(results)
        
#         # Print the number of results retrieved in this batch
#         print(f"Retrieved {len(results)} results")
        
#         # Check if there's a next_page_token for additional results
#         next_page_token = response.json().get('next_page_token')
#         if next_page_token:
#             print("Next page token found, fetching more results...")
#             params['pagetoken'] = next_page_token
#             # Delay to ensure the next page token is activated
#             time.sleep(3)  # Ensuring enough delay for the next page token
#         else:
#             print("No more pages.")
#             break
    
#     return all_results

# # Open the CSV file for writing
# with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
#     writer = csv.writer(file)
    
#     # Write the header row
#     writer.writerow(headers)
    
#     # Loop through each street and collect business data
#     for street, coordinates in streets_coordinates.items():
#         print(f"Searching for businesses along {street}...")
        
#         # Perform multiple smaller searches along the same street by shifting the center points
#         for offset in range(-3, 4):  # Offset to cover adjacent areas along the street, increase range
#             offset_lat = coordinates[0] + (offset * 0.001)  # Adjust latitude slightly
#             offset_lng = coordinates[1] + (offset * 0.001)  # Adjust longitude slightly
#             businesses = search_businesses(API_KEY, (offset_lat, offset_lng), RADIUS)
            
#             for business in businesses:
#                 place_id = business.get('place_id', 'N/A')
                
#                 # Check if this place ID has already been written (to avoid duplicates)
#                 if place_id not in unique_place_ids:
#                     unique_place_ids.add(place_id)  # Add the place ID to the set

#                     name = business.get('name', 'N/A')
#                     address = business.get('vicinity', 'N/A')
#                     rating = business.get('rating', 'N/A')
#                     latitude = business['geometry']['location'].get('lat', 'N/A')
#                     longitude = business['geometry']['location'].get('lng', 'N/A')

#                     # Write each unique business row
#                     writer.writerow([street, name, address, rating, place_id, latitude, longitude])

# print(f"Data has been saved to {csv_file}, with no duplicates and all available pages.")


# Load your CSV data
data = pd.read_csv('filtered_merged_shape_business_data.csv')

# Function to get business data from Google Places API
def get_business_data(address):
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        'input': address,
        'inputtype': 'textquery',
        'fields': 'name,formatted_address,geometry/location,rating',
        'key': API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        result = response.json().get('candidates')
        if result:
            business = result[0]
            return {
                'Business Name': business.get('name', ''),
                'Street': business.get('formatted_address', ''),
                'Rating': business.get('rating', ''),
                'Latitude': business.get('geometry', {}).get('location', {}).get('lat', ''),
                'Longitude': business.get('geometry', {}).get('location', {}).get('lng', ''),
                'Flag': 'broad_filled'
            }
    return None

# Loop through each row, fill missing business data if 'Business Name' is empty
for idx, row in data.iterrows():
    if pd.isna(row['Business Name']):
        business_data = get_business_data(row['Address'])
        if business_data:
            for key, value in business_data.items():
                data.at[idx, key] = value
        time.sleep(1)  # to avoid hitting API rate limits

# Save the updated CSV
data.to_csv('lawrenceville_data_updated.csv', index=False)

print("Updated data saved to 'lawrenceville_data_updated.csv'")
