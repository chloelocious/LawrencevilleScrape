import pandas as pd
import re
from fuzzywuzzy import process, fuzz

# Function to clean and standardize addresses
def clean_address(address):
    if pd.isna(address):
        return "", ""
    address = address.lower().strip()  # Convert to lowercase and trim
    address = re.sub(r',\s*pittsburgh', '', address)  # Remove ", Pittsburgh"
    # Separate number and street
    match = re.match(r'(\d+)\s+(.*)', address)
    if match:
        number = match.group(1)
        street = match.group(2)
        # Standardize street type abbreviations
        street = re.sub(r'\b(street|st)\b', 'st', street)
        street = re.sub(r'\b(avenue|ave)\b', 'ave', street)
        street = re.sub(r'\b(boulevard|blvd)\b', 'blvd', street)
        street = re.sub(r'\b(road|rd)\b', 'rd', street)
        street = re.sub(r'\b(suite|ste)\b', 'ste', street)
        street = re.sub(r'\b(apartment|apt)\b', 'apt', street)
        street = re.sub(r'\s+', ' ', street)  # Remove extra spaces
        return number, street.strip()
    return "", address.strip()

# Load the datasets
lawrenceville_data = pd.read_csv('lawrenceville_data_clean.csv')
bounding_data = pd.read_csv('cleaned_addresses_with_flags.csv')

# Clean and split address components
lawrenceville_data[['Street_Number', 'Street_Name']] = lawrenceville_data['FULL_ADDRE'].apply(clean_address).apply(pd.Series)
bounding_data[['Street_Number', 'Street_Name']] = bounding_data['Address_bounding'].apply(clean_address).apply(pd.Series)

# Function for fuzzy matching with street names and exact matching on street numbers
def match_addresses(lawrenceville_df, bounding_df, threshold=80):
    matched_records = []

    for _, row in lawrenceville_df.iterrows():
        street_name = row['Street_Name']
        street_number = row['Street_Number']

        # Find the best match based on street name similarity
        matches = process.extract(street_name, bounding_df['Street_Name'], scorer=fuzz.partial_ratio, limit=5)
        
        # Check if there is a close match above the threshold and ensure exact match on street number
        best_match = None
        for match in matches:
            matched_row = bounding_df[(bounding_df['Street_Name'] == match[0]) & (bounding_df['Street_Number'] == street_number)]
            if match[1] >= threshold and not matched_row.empty:
                best_match = matched_row.iloc[0]
                break

        # Append match or empty if no valid match found
        if best_match is not None:
            matched_records.append({
                'Address': row['FULL_ADDRE'],
                'Business Name': best_match['Name_bounding'],
                'Street': best_match['Street_bounding'],
                'Rating': best_match['Rating_bounding'],
                'Latitude': best_match['Latitude_bounding'],
                'Longitude': best_match['Longitude_bounding'],
                'Flag': best_match['flag']
            })
        else:
            matched_records.append({
                'Address': row['FULL_ADDRE'],
                'Business Name': None,
                'Street': None,
                'Rating': None,
                'Latitude': None,
                'Longitude': None,
                'Flag': None
            })

    return pd.DataFrame(matched_records)

# Apply the matching function
merged_data = match_addresses(lawrenceville_data, bounding_data, threshold=80)

# Save the result to a new CSV file
merged_data.to_csv('merged_shape_business_data.csv', index=False)

print("Merged data saved to 'merged_shape_business_data.csv'")
