import pandas as pd

# Load your CSV into a DataFrame (replace 'your_file.csv' with the actual file path)
df = pd.read_csv('merged_businesses_full.csv')

# Function to merge rows with same addresses and flag them
def consolidate_addresses(row):
    # Initialize a flag to track if any broad values are used
    row['flag'] = 'bounding_only'  # Default flag is that only bounding data exists

    for column in ['Street', 'Name', 'Address', 'Rating', 'Latitude', 'Longitude']:
        # If the bounding part is missing, but broad is present, fill it and flag the row
        if pd.isnull(row[f'{column}_bounding']) and not pd.isnull(row[f'{column}_broad']):
            row[f'{column}_bounding'] = row[f'{column}_broad']
            row['flag'] = 'broad_filled'  # Indicate that broad data was used
        # If both bounding and broad exist, flag it as merged
        elif not pd.isnull(row[f'{column}_bounding']) and not pd.isnull(row[f'{column}_broad']):
            row['flag'] = 'consolidated'  # Indicate that both bounding and broad data were present
    return row

# Apply the consolidation function
df = df.apply(consolidate_addresses, axis=1)

# Drop the unnecessary broad columns after consolidation
df_cleaned = df.drop(columns=[col for col in df.columns if '_broad' in col])

# Save the cleaned data into a new CSV file
df_cleaned.to_csv('cleaned_addresses_with_flags.csv', index=False)

print("Address consolidation complete. All rows have been preserved and flagged.")
