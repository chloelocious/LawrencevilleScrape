import requests
import csv
import time

# Your API Key
API_KEY = 'AIzaSyALb-2Rrmt34nrOuIGla2cv0i0zOlB7qfI'  # Replace with your actual API key

# Dictionary containing street names and their corresponding bounding boxes (SW corner, NE corner)
streets_bounding_boxes = {
    'liberty ave': [(40.4600, -79.9550), (40.4650, -79.9480)],  # Southwest and Northeast corners
    'penn ave': [(40.4650, -79.9650), (40.4700, -79.9550)],
    'butler st': [(40.4680, -79.9650), (40.4730, -79.9570)],
    '34th st': [(40.4675, -79.9690), (40.4690, -79.9660)],
    '35th st': [(40.4680, -79.9695), (40.4695, -79.9665)],
    '36th st': [(40.4685, -79.9700), (40.4700, -79.9670)],
    '37th st': [(40.4690, -79.9705), (40.4705, -79.9675)],
    '38th st': [(40.4695, -79.9710), (40.4710, -79.9680)],
    '39th st': [(40.4700, -79.9715), (40.4715, -79.9685)],
    '40th st': [(40.4705, -79.9720), (40.4720, -79.9690)],
    '41st st': [(40.4710, -79.9725), (40.4725, -79.9695)],
    '42nd st': [(40.4715, -79.9730), (40.4730, -79.9700)],
    '43rd st': [(40.4720, -79.9735), (40.4735, -79.9705)],
    '44th st': [(40.4725, -79.9740), (40.4740, -79.9710)],
    '45th st': [(40.4730, -79.9745), (40.4745, -79.9715)],
    '46th st': [(40.4735, -79.9750), (40.4750, -79.9720)],
    '47th st': [(40.4740, -79.9755), (40.4755, -79.9725)],
    '48th st': [(40.4745, -79.9760), (40.4760, -79.9730)],
    'plummer st': [(40.4750, -79.9765), (40.4765, -79.9735)],
    '49th st': [(40.4755, -79.9770), (40.4770, -79.9740)],
    '50th st': [(40.4760, -79.9775), (40.4775, -79.9745)],
    '51st st': [(40.4765, -79.9780), (40.4780, -79.9750)],
    'stanton ave': [(40.4770, -79.9785), (40.4785, -79.9755)],
    '52nd st': [(40.4775, -79.9790), (40.4790, -79.9760)],
    'mccandless ave': [(40.4780, -79.9795), (40.4795, -79.9765)],
    '53rd st': [(40.4785, -79.9800), (40.4800, -79.9770)],
    '54th st': [(40.4790, -79.9805), (40.4805, -79.9775)],
    '55th st': [(40.4795, -79.9810), (40.4810, -79.9780)],
    '56th st': [(40.4800, -79.9815), (40.4815, -79.9785)],
    'hatfield st': [(40.4805, -79.9820), (40.4820, -79.9790)],
    'fisk st': [(40.4810, -79.9825), (40.4825, -79.9795)],
    'smallman st': [(40.4815, -79.9830), (40.4830, -79.9800)],
    'main st': [(40.4820, -79.9835), (40.4835, -79.9805)],
    'charlotte': [(40.4825, -79.9840), (40.4840, -79.9810)],
}

# CSV file name
csv_file = 'lawrenceville_businesses_bounding_box.csv'

# Specify the headers for the CSV
headers = ['Street', 'Name', 'Address', 'Rating', 'Place ID', 'Latitude', 'Longitude']

# A set to track unique Place IDs
unique_place_ids = set()

# Function to search businesses using nearbysearch within a simulated bounding box (split into grids)
def search_businesses_nearby(api_key, lat, lng, radius):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f'{lat},{lng}',
        'radius': radius,  # 200 meters to ensure smaller grid search
        'key': api_key
    }

    all_results = []
    while True:
        response = requests.get(url, params=params)
        results = response.json().get('results', [])
        all_results.extend(results)
        
        # Print the number of results retrieved in this batch
        print(f"Retrieved {len(results)} results for location {lat}, {lng}.")
        
        # Check if there's a next_page_token for additional results
        next_page_token = response.json().get('next_page_token')
        if next_page_token:
            print("Next page token found, fetching more results...")
            params['pagetoken'] = next_page_token
            time.sleep(3)  # Delay to ensure the next page token is activated
        else:
            print("No more pages for this location.")
            break
    
    return all_results

# Function to divide the bounding box into smaller grids and search each grid
def search_bounding_box(api_key, sw_corner, ne_corner, radius=200):
    lat_step = 0.0015  # Adjust step size for grid spacing (latitude)
    lng_step = 0.0015  # Adjust step size for grid spacing (longitude)
    
    lat_start, lng_start = sw_corner
    lat_end, lng_end = ne_corner

    all_grid_results = []

    lat = lat_start
    while lat <= lat_end:
        lng = lng_start
        while lng <= lng_end:
            # Search the grid area
            grid_results = search_businesses_nearby(api_key, lat, lng, radius)
            all_grid_results.extend(grid_results)
            lng += lng_step  # Move to the next longitude step
        lat += lat_step  # Move to the next latitude step

    return all_grid_results

# Open the CSV file for writing
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Write the header row
    writer.writerow(headers)
    
    # Loop through each street and collect business data in bounding box
    for street, bounding_box in streets_bounding_boxes.items():
        print(f"Searching for businesses along {street}...")
        sw_corner, ne_corner = bounding_box
        
        # Search within the bounding box divided into smaller grids
        businesses = search_bounding_box(API_KEY, sw_corner, ne_corner)

        # Process the businesses and avoid duplicates
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

                # Write each unique business row to the CSV file
                writer.writerow([street, name, address, rating, place_id, latitude, longitude])

print(f"Data has been saved to {csv_file}, with no duplicates and all available pages.")