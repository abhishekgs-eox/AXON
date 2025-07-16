import requests
import pandas as pd
import time
import os
from datetime import datetime
import numpy as np

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output\EPAF"
EPA_PATH = os.path.join(BASE_PATH, "EPA_Data")
OUTPUT_PATH = os.path.join(EPA_PATH, "Output")

# Create directories if they don't exist
os.makedirs(OUTPUT_PATH, exist_ok=True)

# EPA API Configuration
FACILITY_URL = "https://services.arcgis.com/cJ9YHowT8TU7DUyn/arcgis/rest/services/UST_Finder_Feature_Layer_2/FeatureServer/0/query"

def fetch_epa_facility_data():
    """Fetch all EPA facility data"""
    print("="*60)
    print("EPA FACILITY DATA FETCHER")
    print("="*60)
    print(f"Output Path: {OUTPUT_PATH}")
    print("\nFetching EPA facility data...")
    
    # Pagination parameters
    batch_size = 2000
    offset = 0
    all_records = []
    
    while True:
        params = {
            'where': '1=1',
            'outFields': '*',
            'f': 'json',
            'resultRecordCount': batch_size,
            'resultOffset': offset
        }
        
        try:
            response = requests.get(FACILITY_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            features = data.get('features', [])
            if not features:
                break
            
            records = [f['attributes'] for f in features]
            all_records.extend(records)
            
            print(f"✓ Fetched {len(records)} records at offset {offset}")
            offset += batch_size
            
            # Be polite to the server
            time.sleep(0.2)
            
        except Exception as e:
            print(f"✗ Error fetching data at offset {offset}: {e}")
            break
    
    print(f"\n✓ Total records fetched: {len(all_records)}")
    return all_records

def process_facility_data(records):
    """Process facility data without renaming columns"""
    print("\nProcessing facility data...")
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Process LUST field if it exists (using original column name)
    if 'HasLUST' in df.columns:
        df['HasLUST'] = df['HasLUST'].apply(lambda x: 'Yes' if x else 'No')
    
    # Convert date fields (using original column names)
    date_columns = ['LastUpdated']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Add processing metadata
    df['data_source'] = 'EPA'
    df['fetch_date'] = datetime.now()
    
    # Clean zip codes (using original column name)
    if 'ZipCode' in df.columns:
        df['ZipCode'] = df['ZipCode'].astype(str).str[:5]
    
    # Sort by state and facility ID (using original column names)
    if 'State' in df.columns and 'RegistryID' in df.columns:
        df = df.sort_values(['State', 'RegistryID'])
    
    print(f"✓ Processed {len(df)} facility records")
    return df

def save_combined_data(df):
    """Save combined and processed data as final file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save as final CSV file
    final_file = os.path.join(OUTPUT_PATH, f"EPA_Facility_Data_Final_{timestamp}.csv")
    df.to_csv(final_file, index=False)
    print(f"\n✓ Saved final data: {final_file}")
    
    return final_file

def main():
    """Main function"""
    try:
        # Fetch data
        records = fetch_epa_facility_data()
        
        if not records:
            print("\n✗ No data fetched!")
            return
        
        # Process data
        df = process_facility_data(records)
        
        # Save combined data
        output_file = save_combined_data(df)
        
        # Summary
        print("\n" + "="*60)
        print("FACILITY DATA FETCH COMPLETE!")
        print("="*60)
        print(f"Total facilities: {len(df)}")
        if 'State' in df.columns:
            print(f"States covered: {df['State'].nunique()}")
        print(f"\nOutput saved to: {OUTPUT_PATH}")
        
    except Exception as e:
        print(f"\n✗ Error in main process: {e}")

if __name__ == "__main__":
    main()