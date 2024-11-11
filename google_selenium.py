from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from webdriver_manager.chrome import ChromeDriverManager

# Load the data
data = pd.read_csv('lawrenceville_data_cleaned_updated.csv')

# Check if the 'Business Name' and 'Rating' columns exist; if not, create them
if 'Business Name' not in data.columns:
    data['Business Name'] = None  # Initialize with None or empty values
if 'Rating' not in data.columns:
    data['Rating'] = None  # Initialize with None or empty values

# Dictionary to store business info as we find it
business_cache = {}

# Set up the Chrome driver using ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Function to search Google and retrieve business name and rating
def fetch_business_name_and_rating(address):
    # If the business info is already in the cache, return it
    if address in business_cache:
        print(f"Using cached info for: {address}")
        return business_cache[address]
    
    # Perform a Google search if the business info is not cached
    driver.get("https://www.google.com")
    try:
        # Find the Google search bar and enter the search query
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(address)
        search_box.send_keys(Keys.RETURN)
        print(f"Searching for: {address}")
        
        # Wait until the "Most popular places at this address" element appears
        popular_places_header = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Most popular places at this address')]"))
        )

        # Click the first popular place link
        popular_place_link = driver.find_element(By.XPATH, "//a[@class='GsTn7d']")
        popular_place_link.click()
        
        # Attempt to locate business name and rating
        try:
            # First try to locate business name using the main title element
            business_name_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-attrid='title']"))
            )
            business_name = business_name_element.text
        except:
            # Alternative method if primary title element is missing
            business_name_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h2[@class='qrShPb']"))
            )
            business_name = business_name_element.text
        
        # Attempt to locate rating
        try:
            rating_element = driver.find_element(By.XPATH, "//span[@class='Aq14fc']")
            rating = rating_element.text
        except:
            rating = None
            print(f"Rating not found for {address}")
        
        print(f"Found business name: {business_name} with rating: {rating}")
        
        # Store the result in the cache
        business_cache[address] = (business_name, rating)
        return business_name, rating

    except Exception as e:
        print(f"No popular business info found for {address}: {e}")
        business_cache[address] = (None, None)  # Cache the failure to prevent re-searching
        return None, None

# Loop through each address, retrieve business info if 'Business Name' or 'Rating' is missing
for idx, row in data.iterrows():
    # Skip if both 'Business Name' and 'Rating' are already filled
    if pd.notna(row['Business Name']) and pd.notna(row['Rating']):
        continue

    # Fetch and fill in the business name and rating if not present
    address = row['Address']
    business_name, rating = fetch_business_name_and_rating(address)
    if business_name:
        data.at[idx, 'Business Name'] = business_name
    if rating:
        data.at[idx, 'Rating'] = rating
    
    # Add a short delay to prevent Google from blocking requests
    time.sleep(2)

# Save the updated data to a new CSV
data.to_csv('lawrenceville_data_with_business_info.csv', index=False)

# Close the browser session
driver.quit()

print("Business information fetched and saved to 'lawrenceville_data_with_business_info.csv'")
