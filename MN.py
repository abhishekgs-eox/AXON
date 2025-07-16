from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime
import numpy as np

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Minnesota"
STATE_ABBR = "MN"
URL = "https://webapp.pca.state.mn.us/tank-leak/sites?activityType=LS"

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

def download_minnesota_data():
    """Download Tank site and Leak site data from Minnesota PCA website"""
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
        
        try:
            # First download Tank sites
            print(f"Navigating to {URL}")
            page.goto(URL.replace('activityType=LS', 'activityType=TS'), wait_until='networkidle', timeout=60000)
            page.wait_for_load_state('domcontentloaded')
            time.sleep(5)
            
            print("\nLooking for download/export button for Tank sites...")
            
            # Common selectors for export/download buttons
            export_selectors = [
                'button:has-text("Export")',
                'button:has-text("Download")',
                'a:has-text("Export")',
                'a:has-text("Download")',
                'button[title*="Export"]',
                'button[title*="Download"]',
                '#exportButton',
                '.export-button',
                'button[aria-label*="Export"]',
                '//button[contains(text(), "Export")]',
                '//button[contains(@class, "export")]',
                'button:has-text("CSV")',
                'button:has-text("Excel")'
            ]
            
            # Try to find and click search button first if needed
            search_selectors = [
                'button:has-text("Search")',
                'button[type="submit"]',
                'input[type="submit"][value="Search"]',
                '#searchButton'
            ]
            
            for selector in search_selectors:
                try:
                    if selector.startswith('//'):
                        search_btn = page.locator(f'xpath={selector}')
                    else:
                        search_btn = page.locator(selector)
                    
                    if search_btn.count() > 0:
                        print("Found search button, clicking...")
                        search_btn.first.click()
                        time.sleep(5)  # Wait for results to load
                        break
                except:
                    continue
            
            # Now try to download Tank sites
            tank_downloaded = False
            for selector in export_selectors:
                try:
                    if selector.startswith('//'):
                        element = page.locator(f'xpath={selector}')
                    else:
                        element = page.locator(selector)
                    
                    if element.count() > 0:
                        print(f"✓ Found export element for Tank sites")
                        
                        # Prepare for download
                        with page.expect_download(timeout=60000) as download_info:
                            element.first.click()
                            print("  Clicked export button, waiting for download...")
                        
                        download = download_info.value
                        tank_filename = f"{STATE_NAME}_Tank_Sites.xlsx"
                        tank_path = os.path.join(DOWNLOAD_PATH, tank_filename)
                        download.save_as(tank_path)
                        
                        downloaded_files.append(tank_filename)
                        print(f"  ✓ Downloaded: {tank_filename}")
                        tank_downloaded = True
                        break
                except Exception as e:
                    continue
            
            if not tank_downloaded:
                print("  ✗ Could not download Tank sites")
                # Take screenshot for debugging
                screenshot_path = os.path.join(STATE_PATH, "minnesota_tank_debug.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"  Screenshot saved to: {screenshot_path}")
            
            time.sleep(3)
            
            # Now download Leak sites
            print("\nNavigating to Leak sites...")
            page.goto(URL, wait_until='networkidle', timeout=60000)
            page.wait_for_load_state('domcontentloaded')
            time.sleep(5)
            
            # Search for leak sites
            for selector in search_selectors:
                try:
                    if selector.startswith('//'):
                        search_btn = page.locator(f'xpath={selector}')
                    else:
                        search_btn = page.locator(selector)
                    
                    if search_btn.count() > 0:
                        print("Found search button, clicking...")
                        search_btn.first.click()
                        time.sleep(5)  # Wait for results to load
                        break
                except:
                    continue
            
            # Download Leak sites
            leak_downloaded = False
            for selector in export_selectors:
                try:
                    if selector.startswith('//'):
                        element = page.locator(f'xpath={selector}')
                    else:
                        element = page.locator(selector)
                    
                    if element.count() > 0:
                        print(f"✓ Found export element for Leak sites")
                        
                        # Prepare for download
                        with page.expect_download(timeout=60000) as download_info:
                            element.first.click()
                            print("  Clicked export button, waiting for download...")
                        
                        download = download_info.value
                        leak_filename = f"{STATE_NAME}_Leak_Sites.xlsx"
                        leak_path = os.path.join(DOWNLOAD_PATH, leak_filename)
                        download.save_as(leak_path)
                        
                        downloaded_files.append(leak_filename)
                        print(f"  ✓ Downloaded: {leak_filename}")
                        leak_downloaded = True
                        break
                except Exception as e:
                    continue
            
            if not leak_downloaded:
                print("  ✗ Could not download Leak sites")
                # Take screenshot for debugging
                screenshot_path = os.path.join(STATE_PATH, "minnesota_leak_debug.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"  Screenshot saved to: {screenshot_path}")
                
        except Exception as e:
            print(f"Error during download process: {e}")
            import traceback
            traceback.print_exc()
        
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

def read_file_robust(file_path):
    """Try multiple methods to read a file"""
    print(f"Attempting to read file: {file_path}")
    
    # Try reading as Excel first
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        print("Successfully read as Excel file")
        return df
    except:
        pass
    
    # Try reading as CSV
    try:
        df = pd.read_csv(file_path, low_memory=False)
        print("Successfully read as CSV")
        return df
    except:
        pass
    
    # Try reading as TSV
    try:
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        print("Successfully read as TSV")
        return df
    except:
        pass
    
    print("Could not read file with any method")
    return None

def process_minnesota_tank_data():
    """Process Minnesota Tank site data"""
    tank_file = os.path.join(INPUT_PATH, f"{STATE_NAME}_Tank_Sites.xlsx")
    
    if not os.path.exists(tank_file):
        # Try alternate filename
        files = [f for f in os.listdir(INPUT_PATH) if 'tank' in f.lower() and f.endswith(('.xlsx', '.xls', '.csv'))]
        if files:
            tank_file = os.path.join(INPUT_PATH, files[0])
        else:
            print(f"Tank file not found")
            return pd.DataFrame()
    
    df_raw = read_file_robust(tank_file)
    if df_raw is None:
        return pd.DataFrame()
    
    print(f"Loaded Tank data: {len(df_raw)} records")
    print(f"Columns found: {list(df_raw.columns)}")
    
    processed_rows = []
    
    for idx, row in df_raw.iterrows():
        # Since Minnesota has tank count, we may need to create multiple rows
        tank_count = safe_int(row.get('tankCount', 1))
        if tank_count == 0:
            tank_count = 1
        
        for tank_num in range(1, tank_count + 1):
            processed_row = {}
            
            # State information
            processed_row['state'] = STATE_NAME
            processed_row['state_name'] = STATE_ABBR
            
            # Map Minnesota specific columns
            processed_row['facility_id'] = safe_string(row.get('siteId', row.get('activityId', '')))
            processed_row['tank_id'] = f"{tank_num}" if tank_count > 1 else "1"
            processed_row['tank_location'] = safe_string(row.get('addressStreet', ''))
            processed_row['city'] = safe_string(row.get('city', ''))
            processed_row['zip'] = safe_string(row.get('zipCode', ''))[:5]
            processed_row['county'] = safe_string(row.get('county', ''))
            
            # Tank type - for Tank sites, default to UST
            processed_row['ust_or_ast'] = 'UST'
            
            # Installation date - not available in Minnesota data
            processed_row['year_installed'] = ''
            processed_row['tank_install_year_only'] = ''
            
            # Tank size - not available in Minnesota data
            processed_row['tank_size__gallons_'] = 0
            processed_row['size_range'] = ''
            
            # Construction details - not available
            processed_row['tank_construction'] = ''
            processed_row['piping_construction'] = ''
            processed_row['tank_construction_rating'] = ''
            
            # Secondary containment - not available
            processed_row['secondary_containment__ast_'] = ''
            
            # Content/Product - not available
            processed_row['content_description'] = ''
            
            # Tank tightness - not available
            processed_row['tank_tightness'] = ''
            
            # Facility name
            processed_row['facility_name'] = safe_string(row.get('activityName', ''))
            
            # Tank status - based on activity type
            activity_type = safe_string(row.get('activityType', ''))
            if activity_type == 'TS':
                processed_row['tank_status'] = 'Active'
            else:
                processed_row['tank_status'] = ''
            
            # LUST information - initially no
            processed_row['lust'] = 'No'
            processed_row['lust_status'] = ''
            
            # Last synch date
            processed_row['last_synch_date'] = datetime.now().strftime('%Y/%m/%d')
            
            # Store lat/long for potential future use
            processed_row['latitude'] = safe_string(row.get('lat', ''))
            processed_row['longitude'] = safe_string(row.get('long', ''))
            
            processed_rows.append(processed_row)
    
    return pd.DataFrame(processed_rows)

def process_minnesota_leak_data():
    """Process Minnesota Leak site data"""
    leak_file = os.path.join(INPUT_PATH, f"{STATE_NAME}_Leak_Sites.xlsx")
    
    if not os.path.exists(leak_file):
        # Try alternate filename
        files = [f for f in os.listdir(INPUT_PATH) if 'leak' in f.lower() and f.endswith(('.xlsx', '.xls', '.csv'))]
        if files:
            leak_file = os.path.join(INPUT_PATH, files[0])
        else:
            print(f"Leak file not found")
            return None
    
    leak_df = read_file_robust(leak_file)
    if leak_df is None:
        return None
    
    print(f"Loaded Leak data: {len(leak_df)} records")
    print(f"Columns found: {list(leak_df.columns)}")
    
    # Save to Required folder
    leak_output = os.path.join(REQUIRED_PATH, f"{STATE_NAME}_Leak_Raw.xlsx")
    leak_df.to_excel(leak_output, index=False)
    print(f"Saved raw Leak data to: {leak_output}")
    
    return leak_df

def merge_leak_with_tank_data(formatted_df, leak_df):
    """Merge Leak information with Tank data"""
    if leak_df is None or leak_df.empty:
        print("No Leak data to merge")
        return formatted_df
    
    try:
        print("\n=== Merging Leak data with Tank data ===")
        
        # Create matching keys based on site ID
        leak_sites = set(leak_df['siteId'].astype(str).unique())
        
        # Mark facilities with leak incidents
        formatted_df['lust'] = formatted_df['facility_id'].astype(str).apply(
            lambda x: 'Yes' if x in leak_sites else 'No'
        )
        
        # Also try matching by address
        leak_df['address_city'] = (leak_df['addressStreet'].astype(str).str.upper() + '_' + 
                                   leak_df['city'].astype(str).str.upper())
        formatted_df['address_city'] = (formatted_df['tank_location'].astype(str).str.upper() + '_' + 
                                        formatted_df['city'].astype(str).str.upper())
        
        # Update LUST info for address matches not already marked
        leak_addresses = set(leak_df['address_city'].unique())
        mask = formatted_df['address_city'].isin(leak_addresses) & (formatted_df['lust'] != 'Yes')
        formatted_df.loc[mask, 'lust'] = 'Yes'
        formatted_df.loc[mask, 'lust_status'] = 'Active'  # Minnesota doesn't provide status details
        
        # Remove temporary column
        formatted_df = formatted_df.drop('address_city', axis=1)
        
        lust_count = (formatted_df['lust'] == 'Yes').sum()
        print(f"Matched {lust_count} facilities with leak incidents")
        
        return formatted_df
        
    except Exception as e:
        print(f"Error merging Leak data: {e}")
        return formatted_df

def process_lust_data_formatted(formatted_df):
    """Process statewide LUST data and update the formatted dataframe"""
    try:
        print('\n=== Processing Statewide LUST Data ===')
        lust_file = os.path.join(BASE_PATH, "L-UST_Data", "LustDataAllStates.xlsx")
        
        if not os.path.exists(lust_file):
            print(f"Warning: Statewide LUST data file not found at {lust_file}")
            return formatted_df
            
        LustData = pd.read_excel(lust_file)
        MN_Lust = LustData[LustData['State Name'] == STATE_NAME]
        
        if len(MN_Lust) == 0:
            print(f"No statewide LUST records found for {STATE_NAME}")
            return formatted_df
        
        print(f'Found {len(MN_Lust)} statewide LUST records for {STATE_NAME}')
        
        # Save Minnesota LUST data
        mn_lust_file = os.path.join(REQUIRED_PATH, f'{STATE_NAME}_Statewide_LustData.xlsx')
        MN_Lust.to_excel(mn_lust_file, index=False)
        
        # Create location matching key
        if 'Address' in MN_Lust.columns and 'City' in MN_Lust.columns:
            MN_Lust['location_city'] = (MN_Lust['Address'].astype(str).str.strip() + '_' + 
                                        MN_Lust['City'].astype(str).str.strip()).str.upper()
            
            formatted_df['location_city'] = (formatted_df['tank_location'].astype(str) + '_' + 
                                            formatted_df['city'].astype(str)).str.upper()
            
            # Remove duplicates from LUST data
            MN_Lust_unique = MN_Lust.drop_duplicates(subset='location_city', keep='first')
            
            # Count how many records will be updated
            existing_lust = (formatted_df['lust'] == 'Yes').sum()
            
            # Merge to find additional matches
            merged = formatted_df.merge(MN_Lust_unique[['location_city', 'Status']], 
                                      on='location_city', how='left')
            
            # Update lust and lust_status where matches found and not already marked
            new_matches = merged['Status'].notna() & (formatted_df['lust'] != 'Yes')
            formatted_df.loc[new_matches, 'lust'] = 'Yes'
            formatted_df.loc[new_matches, 'lust_status'] = merged.loc[new_matches, 'Status']
            
            # Remove temporary column
            formatted_df = formatted_df.drop('location_city', axis=1)
            
            new_lust = (formatted_df['lust'] == 'Yes').sum()
            print(f'Updated {new_lust - existing_lust} additional records with statewide LUST information')
            print(f'Total LUST sites now: {new_lust}')
        
        return formatted_df
        
    except Exception as e:
        print(f"Error processing statewide LUST data: {e}")
        return formatted_df

def process_all_minnesota_data():
    """Process all downloaded Minnesota data files"""
    print(f"\n=== Starting data processing for {STATE_NAME} ===\n")
    
    # Process Tank data
    formatted_df = process_minnesota_tank_data()
    
    if formatted_df.empty:
        print("No Tank data to process!")
        return
    
    # Process Leak data
    leak_df = process_minnesota_leak_data()
    
    # Ensure all columns are in the correct order (excluding lat/long)
    column_order = [
        'state', 'state_name', 'facility_id', 'tank_id', 'tank_location',
        'city', 'zip', 'ust_or_ast', 'year_installed', 'tank_install_year_only',
        'tank_size__gallons_', 'size_range', 'tank_construction', 'piping_construction',
        'secondary_containment__ast_', 'content_description', 'tank_tightness',
        'facility_name', 'lust', 'tank_construction_rating', 'county',
        'tank_status', 'lust_status', 'last_synch_date'
    ]
    
    # Keep lat/long for reference but not in final output
    if 'latitude' in formatted_df.columns:
        lat_long_df = formatted_df[['facility_id', 'latitude', 'longitude']].drop_duplicates()
        lat_long_file = os.path.join(REQUIRED_PATH, f"{STATE_NAME}_Coordinates.xlsx")
        lat_long_df.to_excel(lat_long_file, index=False)
        print(f"Saved coordinates to: {lat_long_file}")
        formatted_df = formatted_df.drop(['latitude', 'longitude'], axis=1)
    
    formatted_df = formatted_df[column_order]
    
    # Save the formatted data (without Leak info first)
    output_file = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Formatted.xlsx')
    formatted_df.to_excel(output_file, index=False)
    print(f"\n✓ Saved formatted data to: {output_file}")
    print(f"  Total records: {len(formatted_df)}")
    print(f"  Total counties: {formatted_df['county'].nunique()}")
    print(f"  Total facilities: {formatted_df['facility_id'].nunique()}")
    
    # Merge with Leak data
    formatted_df = merge_leak_with_tank_data(formatted_df, leak_df)
    
    # Process statewide LUST data
    formatted_df = process_lust_data_formatted(formatted_df)
    
    # Save final merged data
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
    print(f"AST tanks: {(formatted_df['ust_or_ast'] == 'AST').sum()}")
    print(f"LUST sites: {(formatted_df['lust'] == 'Yes').sum()}")
    
    # Show county breakdown
    print(f"\nRecords by county (top 10):")
    county_counts = formatted_df['county'].value_counts().head(10)
    for county, count in county_counts.items():
        print(f"  {county}: {count}")
    
    # Show sample of mapped data
    print("\nSample of mapped data (first 3 records):")
    print(formatted_df[['facility_id', 'facility_name', 'city', 'county', 'tank_status', 'lust']].head(3).to_string())

def main():
    """Main function to orchestrate the entire process"""
    print(f"{'='*60}")
    print(f"Starting {STATE_NAME} Tank/Leak Data Download and Processing")
    print(f"{'='*60}")
    print(f"Base path: {BASE_PATH}")
    print(f"Target URL: {URL}")
    
    # Setup folder structure
    log_file = setup_folder_structure()
    print(f"Log file: {log_file}")
    
    # Optional: Clear input folder
    clear_input_folder()
    
    # Download files
    print(f"\n=== Downloading {STATE_NAME} Tank and Leak data ===\n")
    downloaded_files = download_minnesota_data()
    
    if downloaded_files:
        print(f"\n✓ Successfully downloaded {len(downloaded_files)} file(s):")
        for file in downloaded_files:
            print(f"  - {file}")
    else:
        print("\n✗ No files were downloaded.")
        print("Note: You may need to manually download the files from the website")
        print("1. Go to the URL and click on 'Tank site' in the search")
        print("2. Export/Download the results")
        print("3. Then select 'Leak site' and export those results")
        print("4. Place both files in the Input folder and run the script again")
        
        # Check if files already exist in input folder
        existing_files = [f for f in os.listdir(INPUT_PATH) if f.endswith(('.xlsx', '.xls', '.csv'))]
        if existing_files:
            print(f"\nFound {len(existing_files)} existing files in Input folder:")
            for f in existing_files:
                print(f"  - {f}")
            proceed = input("\nProceed with processing these files? (y/n): ")
            if proceed.lower() != 'y':
                return
        else:
            return
    
    # Wait for files to be completely written
    time.sleep(3)
    
    # Process all data
    process_all_minnesota_data()
    
    print(f"\n{'='*60}")
    print(f'{STATE_NAME} processing completed!')
    print(f"{'='*60}")

if __name__ == "__main__":
    main()