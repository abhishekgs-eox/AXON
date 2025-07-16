from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime
import numpy as np

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Connecticut"
STATE_ABBR = "CT"
URL = "https://catalog.data.gov/dataset/underground-storage-tanks-usts-facility-and-tank-details/resource/5a58d5ee-eecb-4946-b52d-68762da9a5ca"

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

def download_connecticut_data():
    """Download Connecticut UST data using Playwright"""
    downloaded_files = []
    
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
        
        print(f"Navigating to {URL}")
        page.goto(URL, wait_until='networkidle')
        
        page.wait_for_load_state('domcontentloaded')
        time.sleep(3)
        
        try:
            print("Looking for Download button...")
            
            download_selectors = [
                'a:has-text("Download")',
                'button:has-text("Download")',
                '.btn:has-text("Download")',
                'a.btn-primary:has-text("Download")',
                '#download-button',
                '//a[contains(text(), "Download")]',
                '//button[contains(text(), "Download")]',
                'a[href*=".csv"]',
                'a[href*="download"]',
                '.resource-download',
                'text="Download"'
            ]
            
            download_found = False
            
            for selector in download_selectors:
                try:
                    if selector.startswith('//'):
                        locator = page.locator(f'xpath={selector}')
                    else:
                        locator = page.locator(selector)
                    
                    if locator.count() > 0:
                        print(f"✓ Found Download button using selector: {selector}")
                        
                        locator.first.scroll_into_view_if_needed()
                        time.sleep(1)
                        
                        with page.expect_download(timeout=30000) as download_info:
                            locator.first.click()
                            print("Clicked download button, waiting for file...")
                        
                        download = download_info.value
                        suggested_filename = download.suggested_filename
                        
                        final_path = os.path.join(DOWNLOAD_PATH, suggested_filename)
                        download.save_as(final_path)
                        
                        downloaded_files.append(suggested_filename)
                        print(f"✓ Downloaded: {suggested_filename}")
                        print(f"  File size: {os.path.getsize(final_path) / 1024 / 1024:.2f} MB")
                        download_found = True
                        break
                        
                except Exception as e:
                    continue
            
            if not download_found:
                print("\n✗ Could not find the download button!")
                screenshot_path = os.path.join(STATE_PATH, "connecticut_page_debug.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Screenshot saved to: {screenshot_path}")
                        
        except Exception as e:
            print(f"Error during download: {e}")
        
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
    return str(value).strip()

def safe_int(value):
    """Safely convert value to integer, handling NaN and None"""
    if pd.isna(value) or value is None or value == '':
        return 0
    try:
        return int(float(value))
    except:
        return 0

def process_connecticut_data():
    """Process the downloaded Connecticut data with exact formatting"""
    print(f"\n=== Starting data processing for {STATE_NAME} ===\n")
    
    # Find the downloaded file
    downloaded_file = None
    for file in os.listdir(INPUT_PATH):
        if file.endswith('.csv') or file.endswith('.xlsx'):
            downloaded_file = file
            break
    
    if not downloaded_file:
        print("No CSV or Excel file found in Input folder!")
        return
    
    print(f"Processing file: {downloaded_file}")
    
    try:
        file_path = os.path.join(INPUT_PATH, downloaded_file)
        
        # Read file based on extension
        if downloaded_file.endswith('.csv'):
            print("Reading CSV file...")
            df_raw = pd.read_csv(file_path)
        else:
            print("Reading Excel file...")
            df_raw = pd.read_excel(file_path)
        
        print(f"File shape: {df_raw.shape}")
        print(f"\nColumns found in source file:")
        for i, col in enumerate(df_raw.columns):
            print(f"  {i+1}. {col}")
        
        # Process each row with Connecticut specific column mappings
        processed_rows = []
        
        for idx, row in df_raw.iterrows():
            processed_row = {}
            
            # State information
            processed_row['state'] = STATE_NAME
            processed_row['state_name'] = STATE_ABBR
            
            # Map Connecticut specific columns
            processed_row['facility_id'] = safe_string(row.get('UST Site ID Number', ''))
            processed_row['tank_id'] = safe_string(row.get('Tank No.', ''))
            processed_row['tank_location'] = safe_string(row.get('Site Address', ''))
            processed_row['city'] = safe_string(row.get('Site City', ''))
            processed_row['zip'] = safe_string(row.get('Site Zip', ''))[:5]
            
            # County - not in CT data, leave empty
            processed_row['county'] = ''
            
            # Tank type - All UST for Connecticut underground storage tanks
            processed_row['ust_or_ast'] = 'UST'
            
            # Installation date
            date_value = row.get('Installation Date', '')
            processed_row['year_installed'] = format_date_for_output(date_value)
            processed_row['tank_install_year_only'] = parse_year_from_date(date_value)
            
            # Tank size and range
            tank_size = row.get('Estimated Total Capacity (gallons)', 0)
            processed_row['tank_size__gallons_'] = safe_int(tank_size)
            processed_row['size_range'] = determine_size_range(tank_size)
            
            # Construction details
            processed_row['tank_construction'] = safe_string(row.get('Construction Type - Tank', ''))
            processed_row['piping_construction'] = safe_string(row.get('Construction Type - Piping', ''))
            
            # Tank construction rating - use Tank Details if available
            tank_details = safe_string(row.get('Tank Details', ''))
            processed_row['tank_construction_rating'] = tank_details
            
            # Secondary containment - Check spill/overfill protection
            spill_protection = safe_string(row.get('Spill Protection', ''))
            overfill_protection = safe_string(row.get('Overfill Protection', ''))
            if spill_protection.lower() == 'yes' or overfill_protection.lower() == 'yes':
                processed_row['secondary_containment__ast_'] = 'Yes'
            else:
                processed_row['secondary_containment__ast_'] = ''
            
            # Content/Product
            processed_row['content_description'] = safe_string(row.get('Substance Currently Stored', ''))
            
            # Tank tightness - not in CT data
            processed_row['tank_tightness'] = ''
            
            # Facility name
            processed_row['facility_name'] = safe_string(row.get('Site Name', ''))
            
            # Tank status
            processed_row['tank_status'] = safe_string(row.get('Status of Tank', ''))
            
            # LUST information - will be updated later
            processed_row['lust'] = ''
            processed_row['lust_status'] = ''
            
            # Last synch date
            processed_row['last_synch_date'] = datetime.now().strftime('%Y/%m/%d')
            
            processed_rows.append(processed_row)
        
        # Create dataframe from processed rows
        formatted_df = pd.DataFrame(processed_rows)
        
        # Ensure all columns are in the correct order
        column_order = [
            'state', 'state_name', 'facility_id', 'tank_id', 'tank_location',
            'city', 'zip', 'ust_or_ast', 'year_installed', 'tank_install_year_only',
            'tank_size__gallons_', 'size_range', 'tank_construction', 'piping_construction',
            'secondary_containment__ast_', 'content_description', 'tank_tightness',
            'facility_name', 'lust', 'tank_construction_rating', 'county',
            'tank_status', 'lust_status', 'last_synch_date'
        ]
        
        formatted_df = formatted_df[column_order]
        
        # Save the formatted data
        output_file = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Formatted.xlsx')
        formatted_df.to_excel(output_file, index=False)
        print(f"\n✓ Saved formatted data to: {output_file}")
        print(f"  Total records: {len(formatted_df)}")
        
        # Show sample of mapped data
        print("\nSample of mapped data (first 3 records):")
        print(formatted_df[['facility_id', 'tank_id', 'facility_name', 'city', 'tank_status']].head(3).to_string())
        
        # Process LUST data if available
        process_lust_data_formatted(formatted_df)
        
    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()

def process_lust_data_formatted(formatted_df):
    """Process LUST data and update the formatted dataframe"""
    try:
        print('\n=== Processing LUST Data ===')
        lust_file = os.path.join(BASE_PATH, "L-UST_Data", "LustDataAllStates.xlsx")
        
        if not os.path.exists(lust_file):
            print(f"Warning: LUST data file not found at {lust_file}")
            final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
            formatted_df.to_excel(final_output, index=False)
            return formatted_df
            
        LustData = pd.read_excel(lust_file)
        CT_Lust = LustData[LustData['State Name'] == STATE_NAME]
        
        if len(CT_Lust) == 0:
            print(f"No LUST records found for {STATE_NAME}")
            final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
            formatted_df.to_excel(final_output, index=False)
            return formatted_df
        
        print(f'Found {len(CT_Lust)} LUST records for {STATE_NAME}')
        
        # Save Connecticut LUST data
        ct_lust_file = os.path.join(REQUIRED_PATH, f'{STATE_NAME}LustData.xlsx')
        CT_Lust.to_excel(ct_lust_file, index=False)
        
        # Create location matching key
        if 'Address' in CT_Lust.columns and 'City' in CT_Lust.columns:
            CT_Lust['location_city'] = (CT_Lust['Address'].astype(str).str.strip() + '_' + 
                                        CT_Lust['City'].astype(str).str.strip()).str.upper()
            
            formatted_df['location_city'] = (formatted_df['tank_location'].astype(str) + '_' + 
                                            formatted_df['city'].astype(str)).str.upper()
            
            # Remove duplicates from LUST data
            CT_Lust_unique = CT_Lust.drop_duplicates(subset='location_city', keep='first')
            
            # Merge to find matches
            merged = formatted_df.merge(CT_Lust_unique[['location_city', 'Status']], 
                                      on='location_city', how='left')
            
            # Update lust and lust_status where matches found
            matches = merged['Status'].notna()
            formatted_df.loc[matches, 'lust'] = 'Yes'
            formatted_df.loc[matches, 'lust_status'] = merged.loc[matches, 'Status']
            
            # For non-matches, explicitly set to 'No'
            formatted_df.loc[~matches, 'lust'] = 'No'
            
            # Remove temporary column
            formatted_df = formatted_df.drop('location_city', axis=1)
            
            print(f'Updated {matches.sum()} records with LUST information')
        
        # Save final merged data
        final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
        formatted_df.to_excel(final_output, index=False)
        print(f"✓ Saved final formatted data with LUST info to: {final_output}")
        
        # Also save as CSV
        csv_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.csv')
        formatted_df.to_csv(csv_output, index=False)
        print(f"✓ Also saved as CSV: {csv_output}")
        
        # Show summary statistics
        print(f"\n=== Summary Statistics ===")
        print(f"Total facilities: {formatted_df['facility_id'].nunique()}")
        print(f"Total tanks: {len(formatted_df)}")
        print(f"Active tanks: {(formatted_df['tank_status'].str.lower() == 'active').sum()}")
        print(f"LUST sites: {(formatted_df['lust'] == 'Yes').sum()}")
        
        return formatted_df
        
    except Exception as e:
        print(f"Error processing LUST data: {e}")
        final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
        formatted_df.to_excel(final_output, index=False)
        return formatted_df

def main():
    """Main function to orchestrate the entire process"""
    print(f"{'='*60}")
    print(f"Starting {STATE_NAME} UST Data Download and Processing")
    print(f"{'='*60}")
    print(f"Base path: {BASE_PATH}")
    print(f"Target URL: {URL}")
    
    # Setup folder structure
    log_file = setup_folder_structure()
    print(f"Log file: {log_file}")
    
    # Optional: Clear input folder
    clear_input_folder()
    
    # Download files
    print(f"\n=== Downloading UST data for {STATE_NAME} ===\n")
    downloaded_files = download_connecticut_data()
    
    if downloaded_files:
        print(f"\n✓ Successfully downloaded {len(downloaded_files)} file(s):")
        for file in downloaded_files:
            print(f"  - {file}")
    else:
        print("\n✗ No files were downloaded.")
        print("Please check:")
        print("1. The website is accessible")
        print("2. The download link is visible")
        print("3. The screenshots in the state folder for debugging")
        return
    
    # Wait for files to be completely written
    time.sleep(3)
    
    # Process the data
    process_connecticut_data()
    
    print(f"\n{'='*60}")
    print(f'{STATE_NAME} processing completed!')
    print(f"{'='*60}")

if __name__ == "__main__":
    main()