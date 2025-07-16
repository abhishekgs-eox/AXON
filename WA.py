from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime
import numpy as np
import requests
import re

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Washington"
STATE_ABBR = "WA"
DIRECT_DOWNLOAD_URL = "https://apps.ecology.wa.gov/cleanupsearch/reports/ust/export?format=csv"

# Dynamic paths based on state
STATE_PATH = os.path.join(BASE_PATH, "states", STATE_NAME)
INPUT_PATH = os.path.join(STATE_PATH, "Input")
OUTPUT_PATH = os.path.join(STATE_PATH, "Output")
REQUIRED_PATH = os.path.join(STATE_PATH, "Required")
DOWNLOAD_PATH = INPUT_PATH

def setup_folder_structure():
    """Create all necessary folders for the state"""
    folders = [
        BASE_PATH,
        os.path.join(BASE_PATH, "states"),
        STATE_PATH,
        INPUT_PATH,
        OUTPUT_PATH,
        REQUIRED_PATH,
        os.path.join(BASE_PATH, "L-UST_Data")
    ]
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")
    
    log_path = os.path.join(STATE_PATH, "logs")
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_path, f"{STATE_NAME}_run_{timestamp}.log")
    
    return log_file

def clear_input_folder():
    """Clear existing files in input folder (optional)"""
    if os.path.exists(INPUT_PATH):
        files = os.listdir(INPUT_PATH)
        if files:
            response = input(f"Found {len(files)} files in Input folder. Clear them? (y/n): ")
            if response.lower() == 'y':
                for file in files:
                    file_path = os.path.join(INPUT_PATH, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                print("Input folder cleared.")

def clean_illegal_characters(text):
    """Remove illegal characters that can't be used in Excel"""
    if pd.isna(text) or text is None:
        return ''
    
    # Convert to string
    text = str(text)
    
    # Remove illegal XML characters
    illegal_xml_chars = [(0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F)]
    for low, high in illegal_xml_chars:
        for char in range(low, high + 1):
            text = text.replace(chr(char), '')
    
    # Remove other problematic characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return text

def clean_dataframe_for_excel(df):
    """Clean all string columns in dataframe for Excel compatibility"""
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(clean_illegal_characters)
    return df

def download_washington_data():
    """Download UST data from Washington Ecology website using direct URL"""
    downloaded_files = []
    
    print(f"\nDownloading from: {DIRECT_DOWNLOAD_URL}")
    
    try:
        # Use requests to download the file
        response = requests.get(DIRECT_DOWNLOAD_URL, timeout=60)
        response.raise_for_status()
        
        filename = f"{STATE_NAME}_UST_Data.csv"
        file_path = os.path.join(DOWNLOAD_PATH, filename)
        
        # Save the content
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        downloaded_files.append(filename)
        print(f"✓ Downloaded: {filename}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        
        # Try with Playwright as backup
        print("\nTrying with Playwright...")
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                downloads_path=DOWNLOAD_PATH
            )
            
            context = browser.new_context(
                accept_downloads=True,
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            try:
                with page.expect_download(timeout=60000) as download_info:
                    page.goto(DIRECT_DOWNLOAD_URL)
                    print("  Waiting for download...")
                
                download = download_info.value
                filename = f"{STATE_NAME}_UST_Data.csv"
                file_path = os.path.join(DOWNLOAD_PATH, filename)
                download.save_as(file_path)
                
                downloaded_files.append(filename)
                print(f"  ✓ Downloaded: {filename}")
                
            except Exception as e:
                print(f"  Error with Playwright download: {e}")
            
            browser.close()
    
    return downloaded_files

def determine_size_range(tank_size):
    """Determine size range based on tank size in gallons"""
    if pd.isna(tank_size) or tank_size == '':
        return ''
    
    try:
        size = float(tank_size)
        if size <= 5000:
            return "0-5000"
        elif size <= 10000:
            return "5001-10000"
        elif size <= 15000:
            return "10001-15000"
        elif size <= 20000:
            return "15001-20000"
        else:
            return "20000+"
    except:
        return ''

def parse_year_from_date(date_value):
    """Extract year from various date formats"""
    if pd.isna(date_value) or date_value == '':
        return ''
    
    try:
        if hasattr(date_value, 'year'):
            return str(date_value.year)
        
        date_str = str(date_value)
        
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y', '%Y']:
            try:
                dt = datetime.strptime(date_str.split()[0], fmt)
                return str(dt.year)
            except:
                continue
        
        if len(date_str) == 4 and date_str.isdigit():
            return date_str
            
        return ''
    except:
        return ''

def format_date_for_output(date_value):
    """Format date as YYYY/MM/DD"""
    if pd.isna(date_value) or date_value == '':
        return ''
    
    try:
        if hasattr(date_value, 'strftime'):
            return date_value.strftime('%Y/%m/%d')
        
        date_str = str(date_value)
        
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y']:
            try:
                dt = datetime.strptime(date_str.split()[0], fmt)
                return dt.strftime('%Y/%m/%d')
            except:
                continue
        
        return ''
    except:
        return ''

def safe_string(value):
    """Safely convert value to string, handling NaN and None"""
    if pd.isna(value) or value is None:
        return ''
    return clean_illegal_characters(str(value).strip())

def safe_int(value):
    """Safely convert value to integer, handling NaN and None"""
    if pd.isna(value) or value is None or value == '':
        return 0
    try:
        return int(float(value))
    except:
        return 0

def process_washington_ust_data():
    """Process Washington UST data"""
    ust_file = os.path.join(INPUT_PATH, f"{STATE_NAME}_UST_Data.csv")
    
    if not os.path.exists(ust_file):
        print(f"UST file not found: {ust_file}")
        return pd.DataFrame()
    
    try:
        # Read CSV file
        df_raw = pd.read_csv(ust_file, low_memory=False)
        print(f"Loaded UST data: {len(df_raw)} records")
        print(f"Columns found: {list(df_raw.columns)[:20]}...")  # Show first 20 columns
        
        # Clean the dataframe before saving
        df_raw_clean = clean_dataframe_for_excel(df_raw.copy())
        
        # Try to save raw data for debugging
        try:
            debug_file = os.path.join(REQUIRED_PATH, f"{STATE_NAME}_Raw_Debug.xlsx")
            df_raw_clean.to_excel(debug_file, index=False)
            print(f"Saved raw data for debugging to: {debug_file}")
        except Exception as e:
            print(f"Warning: Could not save debug file due to: {e}")
            # Try saving as CSV instead
            try:
                debug_csv = os.path.join(REQUIRED_PATH, f"{STATE_NAME}_Raw_Debug.csv")
                df_raw_clean.to_csv(debug_csv, index=False)
                print(f"Saved raw data as CSV instead: {debug_csv}")
            except:
                print("Warning: Could not save debug file in any format")
        
        processed_rows = []
        
        for idx, row in df_raw.iterrows():
            processed_row = {}
            
            # State information
            processed_row['state'] = STATE_NAME
            processed_row['state_name'] = STATE_ABBR
            
            # Map Washington specific columns
            processed_row['facility_id'] = safe_string(row.get('FacilitySiteID', ''))
            processed_row['tank_id'] = safe_string(row.get('USTID', ''))
            processed_row['tank_location'] = safe_string(row.get('Address', ''))
            processed_row['city'] = safe_string(row.get('City', ''))
            processed_row['zip'] = safe_string(row.get('ZipCode', ''))[:5]
            processed_row['county'] = safe_string(row.get('County', ''))
            
            # Tank type - all UST for Washington underground storage tanks
            processed_row['ust_or_ast'] = 'UST'
            
            # Installation date
            date_value = row.get('InstallDate', '')
            processed_row['year_installed'] = format_date_for_output(date_value)
            processed_row['tank_install_year_only'] = parse_year_from_date(date_value)
            
            # Tank size and range
            tank_size = row.get('TankCapacity', row.get('ActualCapacity', 0))
            processed_row['tank_size__gallons_'] = safe_int(tank_size)
            processed_row['size_range'] = determine_size_range(tank_size)
            
            # Construction details
            processed_row['tank_construction'] = safe_string(row.get('TankMaterial', ''))
            processed_row['piping_construction'] = safe_string(row.get('PipeMaterial', ''))
            
            # Tank construction rating based on material
            tank_mat = processed_row['tank_construction'].lower()
            if 'fiberglass' in tank_mat or 'frp' in tank_mat:
                processed_row['tank_construction_rating'] = 'A'
            elif 'steel' in tank_mat and ('coated' in tank_mat or 'protected' in tank_mat or 'cathodic' in tank_mat):
                processed_row['tank_construction_rating'] = 'B'
            elif 'steel' in tank_mat:
                processed_row['tank_construction_rating'] = 'C'
            else:
                processed_row['tank_construction_rating'] = ''
            
            # Secondary containment - check tank construction
            tank_const = safe_string(row.get('TankConstruction', '')).lower()
            if 'double' in tank_const or 'secondary' in tank_const:
                processed_row['secondary_containment__ast_'] = 'Yes'
            else:
                processed_row['secondary_containment__ast_'] = ''
            
            # Content/Product
            processed_row['content_description'] = safe_string(row.get('StoredSubstance', ''))
            
            # Tank tightness - check release detection
            release_detection = safe_string(row.get('TankReleaseDetection', ''))
            if release_detection and release_detection.lower() != 'none':
                processed_row['tank_tightness'] = 'Yes'
            else:
                processed_row['tank_tightness'] = ''
            
            # Facility name
            processed_row['facility_name'] = safe_string(row.get('SiteName', ''))
            
            # Tank status
            processed_row['tank_status'] = safe_string(row.get('TankStatus', ''))
            
            # LUST information - initially no
            processed_row['lust'] = 'No'
            processed_row['lust_status'] = ''
            
            # Last synch date
            processed_row['last_synch_date'] = datetime.now().strftime('%Y/%m/%d')
            
            processed_rows.append(processed_row)
        
        return pd.DataFrame(processed_rows)
        
    except Exception as e:
        print(f"Error processing UST file: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def process_lust_data_formatted(formatted_df):
    """Process statewide LUST data and update the formatted dataframe"""
    try:
        print('\n=== Processing Statewide LUST Data ===')
        lust_file = os.path.join(BASE_PATH, "L-UST_Data", "LustDataAllStates.xlsx")
        
        if not os.path.exists(lust_file):
            print(f"Warning: Statewide LUST data file not found at {lust_file}")
            return formatted_df
            
        LustData = pd.read_excel(lust_file)
        WA_Lust = LustData[LustData['State Name'] == STATE_NAME]
        
        if len(WA_Lust) == 0:
            print(f"No statewide LUST records found for {STATE_NAME}")
            return formatted_df
        
        print(f'Found {len(WA_Lust)} statewide LUST records for {STATE_NAME}')
        
        # Save Washington LUST data
        wa_lust_file = os.path.join(REQUIRED_PATH, f'{STATE_NAME}_Statewide_LustData.xlsx')
        WA_Lust.to_excel(wa_lust_file, index=False)
        
        # Create location matching key
        if 'Address' in WA_Lust.columns and 'City' in WA_Lust.columns:
            WA_Lust['location_city'] = (WA_Lust['Address'].astype(str).str.strip() + '_' + 
                                        WA_Lust['City'].astype(str).str.strip()).str.upper()
            
            formatted_df['location_city'] = (formatted_df['tank_location'].astype(str) + '_' + 
                                            formatted_df['city'].astype(str)).str.upper()
            
            # Remove duplicates from LUST data
            WA_Lust_unique = WA_Lust.drop_duplicates(subset='location_city', keep='first')
            
            # Count how many records will be updated
            existing_lust = (formatted_df['lust'] == 'Yes').sum()
            
            # Merge to find matches
            merged = formatted_df.merge(WA_Lust_unique[['location_city', 'Status']], 
                                      on='location_city', how='left')
            
            # Update lust and lust_status where matches found
            matches = merged['Status'].notna()
            formatted_df.loc[matches, 'lust'] = 'Yes'
            formatted_df.loc[matches, 'lust_status'] = merged.loc[matches, 'Status']
            
            # Remove temporary column
            formatted_df = formatted_df.drop('location_city', axis=1)
            
            new_lust = (formatted_df['lust'] == 'Yes').sum()
            print(f'Updated {new_lust - existing_lust} records with statewide LUST information')
            print(f'Total LUST sites: {new_lust}')
        
        return formatted_df
        
    except Exception as e:
        print(f"Error processing statewide LUST data: {e}")
        return formatted_df

def process_all_washington_data():
    """Process all downloaded Washington data files"""
    print(f"\n=== Starting data processing for {STATE_NAME} ===\n")
    
    # Process UST data
    formatted_df = process_washington_ust_data()
    
    if formatted_df.empty:
        print("No UST data to process!")
        return
    
    # Ensure all columns are in the correct order
    column_order = [
        'state', 'state_name', 'facility_id', 'tank_id', 'tank_location',
        'city', 'zip', 'ust_or_ast', 'year_installed', 'tank_install_year_only',
        'tank_size__gallons_', 'size_range', 'tank_construction', 'piping_construction',
        'secondary_containment__ast_', 'content_description', 'tank_tightness',
        'facility_name', 'lust', 'tank_construction_rating', 'county',
        'tank_status', 'lust_status', 'last_synch_date'
    ]
    
    # Ensure all columns exist
    for col in column_order:
        if col not in formatted_df.columns:
            formatted_df[col] = ''
    
    formatted_df = formatted_df[column_order]
    
    # Save the formatted data
    output_file = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Formatted.xlsx')
    formatted_df.to_excel(output_file, index=False)
    print(f"\n✓ Saved formatted data to: {output_file}")
    print(f"  Total records: {len(formatted_df)}")
    print(f"  Total counties: {formatted_df['county'].nunique()}")
    print(f"  Total facilities: {formatted_df['facility_id'].nunique()}")
    
    # Process statewide LUST data
    formatted_df = process_lust_data_formatted(formatted_df)
    
    # Save final data with LUST info
    final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
    formatted_df.to_excel(final_output, index=False)
    print(f"\n✓ Saved final formatted data with LUST info to: {final_output}")
    
    # Also save as CSV
    csv_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.csv')
    formatted_df.to_csv(csv_output, index=False)
    print(f"✓ Also saved as CSV: {csv_output}")
    
    # Show summary statistics
    print(f"\n=== Summary Statistics ===")
    print(f"Total counties: {formatted_df['county'].nunique()}")
    print(f"Total facilities: {formatted_df['facility_id'].nunique()}")
    print(f"Total tanks: {len(formatted_df)}")
    print(f"UST tanks: {(formatted_df['ust_or_ast'] == 'UST').sum()}")
    print(f"Active tanks: {(formatted_df['tank_status'].str.lower().str.contains('active', na=False)).sum()}")
    print(f"LUST sites: {(formatted_df['lust'] == 'Yes').sum()}")
    
    # Show tank status breakdown
    print(f"\nTank status breakdown:")
    status_counts = formatted_df['tank_status'].value_counts().head(10)
    for status, count in status_counts.items():
        if status:  # Only show non-empty values
            print(f"  {status}: {count}")
    
    # Show county breakdown
    print(f"\nRecords by county (top 10):")
    county_counts = formatted_df['county'].value_counts().head(10)
    for county, count in county_counts.items():
        print(f"  {county}: {count}")
    
    # Show sample of mapped data
    print("\nSample of mapped data (first 3 records):")
    sample_cols = ['facility_id', 'facility_name', 'city', 'county', 'tank_status', 'tank_construction', 'lust']
    print(formatted_df[sample_cols].head(3).to_string())

def main():
    """Main function to orchestrate the entire process"""
    print(f"{'='*60}")
    print(f"Starting {STATE_NAME} UST Data Download and Processing")
    print(f"{'='*60}")
    print(f"Base path: {BASE_PATH}")
    print(f"Direct download URL: {DIRECT_DOWNLOAD_URL}")
    
    # Setup folder structure
    log_file = setup_folder_structure()
    print(f"Log file: {log_file}")
    
    # Optional: Clear input folder
    clear_input_folder()
    
    # Download files
    print(f"\n=== Downloading {STATE_NAME} UST data ===\n")
    downloaded_files = download_washington_data()
    
    if downloaded_files:
        print(f"\n✓ Successfully downloaded {len(downloaded_files)} file(s):")
        for file in downloaded_files:
            print(f"  - {file}")
    else:
        print("\n✗ No files were downloaded.")
        print("Please check:")
        print("1. The direct download URL is accessible")
        print("2. Your internet connection")
        return
    
    # Wait for files to be completely written
    time.sleep(3)
    
    # Process all data
    process_all_washington_data()
    
    print(f"\n{'='*60}")
    print(f'{STATE_NAME} processing completed!')
    print(f"{'='*60}")

if __name__ == "__main__":
    main()