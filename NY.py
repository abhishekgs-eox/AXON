from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime
import numpy as np
import re

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "New York"
STATE_ABBR = "NY"
URL = "https://data.ny.gov/Energy-Environment/Bulk-Storage-Facilities-in-New-York-State/pteg-c78n"

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

def download_new_york_data():
    """Download New York state bulk storage facilities data"""
    downloaded_files = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            downloads_path=DOWNLOAD_PATH,
            args=[
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        context = browser.new_context(
            accept_downloads=True,
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ignore_https_errors=True,
            java_script_enabled=True,
            bypass_csp=True
        )
        
        page = context.new_page()
        
        print(f"Navigating to {URL}")
        page.goto(URL, wait_until='networkidle', timeout=60000)
        
        page.wait_for_load_state('domcontentloaded')
        time.sleep(5)
        
        try:
            # Take screenshot for debugging
            screenshot_path = os.path.join(STATE_PATH, "ny_data_page.png")
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved to: {screenshot_path}")
            
            # Try to scroll to make buttons visible
            print("Scrolling to find Export button...")
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)
            
            export_button = None
            
            # Method 1: Try to find and click Actions dropdown first
            print("Looking for Actions dropdown...")
            actions_selectors = [
                'button:has-text("Actions")',
                '[data-testid="actions-dropdown"]',
                '.btn-group button:has-text("Actions")',
                'button[aria-label*="Actions"]',
                '.dropdown-toggle:has-text("Actions")'
            ]
            
            for selector in actions_selectors:
                try:
                    actions_btn = page.locator(selector)
                    if actions_btn.count() > 0 and actions_btn.first.is_visible():
                        print(f"Found Actions button with: {selector}")
                        actions_btn.first.click()
                        time.sleep(2)
                        
                        # Now look for Export in the dropdown
                        export_selectors = [
                            'a:has-text("Export")',
                            'button:has-text("Export")',
                            '[data-testid="export-button"]',
                            '.dropdown-menu a:has-text("Export")',
                            '.dropdown-menu button:has-text("Export")'
                        ]
                        
                        for exp_selector in export_selectors:
                            try:
                                exp_btn = page.locator(exp_selector)
                                if exp_btn.count() > 0 and exp_btn.first.is_visible():
                                    export_button = exp_btn.first
                                    print(f"✓ Found Export in dropdown with: {exp_selector}")
                                    break
                            except:
                                continue
                        
                        if export_button:
                            break
                except:
                    continue
            
            # Method 2: Try direct Export button selectors
            if not export_button:
                print("Looking for direct Export button...")
                export_selectors = [
                    'button:has-text("Export")',
                    'a:has-text("Export")',
                    '[data-testid="export-button"]',
                    '.export-button',
                    'button.export-button',
                    '[aria-label*="Export"]',
                    'button[title*="Export"]'
                ]
                
                for selector in export_selectors:
                    try:
                        btn = page.locator(selector)
                        if btn.count() > 0:
                            # Try to scroll to the button
                            btn.first.scroll_into_view_if_needed()
                            time.sleep(1)
                            
                            if btn.first.is_visible():
                                export_button = btn.first
                                print(f"✓ Found Export button with: {selector}")
                                break
                    except:
                        continue
            
            # Method 3: Try to find CSV download links directly
            if not export_button:
                print("Looking for direct CSV download links...")
                csv_selectors = [
                    'a[href*=".csv"]',
                    'a[href*="export"]',
                    'a[href*="download"]',
                    'a[href*="rows.csv"]'
                ]
                
                for selector in csv_selectors:
                    try:
                        links = page.locator(selector).all()
                        for link in links:
                            href = link.get_attribute('href')
                            if href and ('csv' in href or 'export' in href):
                                export_button = link
                                print(f"✓ Found CSV download link: {href}")
                                break
                        if export_button:
                            break
                    except:
                        continue
            
            # Method 4: Try API endpoint directly
            if not export_button:
                print("Trying direct API endpoint...")
                try:
                    api_url = "https://data.ny.gov/resource/pteg-c78n.csv?$limit=50000"
                    print(f"Navigating to API: {api_url}")
                    
                    with page.expect_download(timeout=30000) as download_info:
                        page.goto(api_url, timeout=30000)
                        time.sleep(3)
                    
                    download = download_info.value
                    
                    # Save and convert to xlsx
                    temp_path = os.path.join(DOWNLOAD_PATH, "temp_api_download.csv")
                    download.save_as(temp_path)
                    
                    # Convert to xlsx
                    df = pd.read_csv(temp_path)
                    final_filename = f"{STATE_NAME.replace(' ', '_')}_bulk_storage_data.xlsx"
                    final_path = os.path.join(DOWNLOAD_PATH, final_filename)
                    df.to_excel(final_path, index=False)
                    
                    # Remove temp file
                    os.remove(temp_path)
                    
                    downloaded_files.append(final_filename)
                    print(f"✓ Downloaded via API: {final_filename}")
                    
                except Exception as api_error:
                    print(f"API approach failed: {api_error}")
                    
                    # Method 5: Try alternative API formats
                    try:
                        print("Trying alternative API formats...")
                        alt_urls = [
                            "https://data.ny.gov/resource/pteg-c78n.json?$limit=50000",
                            f"https://data.ny.gov/api/views/pteg-c78n/rows.csv?accessType=DOWNLOAD",
                            f"https://data.ny.gov/api/views/pteg-c78n/rows.json?accessType=DOWNLOAD"
                        ]
                        
                        for alt_url in alt_urls:
                            try:
                                print(f"Trying: {alt_url}")
                                with page.expect_download(timeout=20000) as download_info:
                                    page.goto(alt_url, timeout=20000)
                                    time.sleep(2)
                                
                                download = download_info.value
                                
                                # Handle different formats
                                if 'json' in alt_url:
                                    temp_path = os.path.join(DOWNLOAD_PATH, "temp_download.json")
                                    download.save_as(temp_path)
                                    
                                    # Convert JSON to DataFrame
                                    import json
                                    with open(temp_path, 'r') as f:
                                        data = json.load(f)
                                    df = pd.DataFrame(data)
                                    
                                    os.remove(temp_path)
                                else:
                                    temp_path = os.path.join(DOWNLOAD_PATH, "temp_download.csv")
                                    download.save_as(temp_path)
                                    df = pd.read_csv(temp_path)
                                    os.remove(temp_path)
                                
                                # Save as Excel
                                final_filename = f"{STATE_NAME.replace(' ', '_')}_bulk_storage_data.xlsx"
                                final_path = os.path.join(DOWNLOAD_PATH, final_filename)
                                df.to_excel(final_path, index=False)
                                
                                downloaded_files.append(final_filename)
                                print(f"✓ Downloaded via alternative API: {final_filename}")
                                break
                                
                            except Exception as alt_error:
                                print(f"Alternative URL failed: {alt_error}")
                                continue
                    
                    except Exception as alt_method_error:
                        print(f"Alternative method failed: {alt_method_error}")
            
            # If we found an export button, try to click it
            if export_button and not downloaded_files:
                try:
                    print("Clicking Export button...")
                    
                    # Scroll to button and wait
                    export_button.scroll_into_view_if_needed()
                    time.sleep(1)
                    
                    # Wait for download
                    with page.expect_download(timeout=60000) as download_info:
                        export_button.click()
                        print("Waiting for download...")
                    
                    download = download_info.value
                    
                    # Get the actual filename
                    suggested_filename = download.suggested_filename
                    print(f"Download suggested filename: {suggested_filename}")
                    
                    # Determine file extension
                    if suggested_filename:
                        file_extension = os.path.splitext(suggested_filename)[1]
                        if not file_extension:
                            file_extension = '.csv'
                    else:
                        file_extension = '.csv'
                    
                    # Save as xlsx format
                    final_filename = f"{STATE_NAME.replace(' ', '_')}_bulk_storage_data.xlsx"
                    final_path = os.path.join(DOWNLOAD_PATH, final_filename)
                    
                    # Save temp file first
                    temp_filename = f"temp_download{file_extension}"
                    temp_path = os.path.join(DOWNLOAD_PATH, temp_filename)
                    download.save_as(temp_path)
                    
                    # Convert to xlsx if needed
                    if file_extension.lower() == '.csv':
                        df = pd.read_csv(temp_path)
                        df.to_excel(final_path, index=False)
                        os.remove(temp_path)
                        print(f"✓ Converted CSV to Excel: {final_filename}")
                    else:
                        os.rename(temp_path, final_path)
                        print(f"✓ Saved Excel file: {final_filename}")
                    
                    downloaded_files.append(final_filename)
                    
                except Exception as click_error:
                    print(f"Error clicking export button: {click_error}")
            
            # Final fallback: Try to scrape data from the page
            if not downloaded_files:
                print("Attempting to scrape data from the page...")
                try:
                    # Look for table data
                    table_rows = page.locator('table tbody tr').all()
                    if table_rows:
                        print(f"Found {len(table_rows)} table rows")
                        
                        # Extract headers
                        headers = []
                        header_cells = page.locator('table thead th').all()
                        for cell in header_cells:
                            headers.append(cell.inner_text().strip())
                        
                        # Extract data
                        data = []
                        for row in table_rows[:100]:  # Limit to first 100 rows
                            row_data = []
                            cells = row.locator('td').all()
                            for cell in cells:
                                row_data.append(cell.inner_text().strip())
                            data.append(row_data)
                        
                        # Create DataFrame
                        df = pd.DataFrame(data, columns=headers)
                        
                        # Save as Excel
                        final_filename = f"{STATE_NAME.replace(' ', '_')}_bulk_storage_data.xlsx"
                        final_path = os.path.join(DOWNLOAD_PATH, final_filename)
                        df.to_excel(final_path, index=False)
                        
                        downloaded_files.append(final_filename)
                        print(f"✓ Scraped data and saved: {final_filename}")
                    
                except Exception as scrape_error:
                    print(f"Scraping failed: {scrape_error}")
                    
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

def process_new_york_file(file_path):
    """Process New York state bulk storage facilities file"""
    try:
        print(f"Processing file: {file_path}")
        
        # Read Excel file
        df_raw = pd.read_excel(file_path)
        
        print(f"Raw data shape: {df_raw.shape}")
        print("Raw columns:", df_raw.columns.tolist())
        
        # Show first few rows to understand structure
        print("\nFirst 3 rows of raw data:")
        print(df_raw.head(3))
        
        processed_rows = []
        
        for idx, row in df_raw.iterrows():
            processed_row = {}
            
            # State information
            processed_row['state'] = STATE_NAME
            processed_row['state_name'] = STATE_ABBR
            
            # Map New York specific columns
            possible_facility_id_cols = ['Facility ID', 'ID', 'Facility_ID', 'FacilityID', 'facility_id', 'facility_number', 'Program Number']
            possible_tank_id_cols = ['Tank ID', 'Tank_ID', 'TankID', 'tank_id', 'Tank Number', 'tank_number']
            possible_address_cols = ['Address', 'Facility Address', 'Street Address', 'Location', 'facility_address', 'Address 1', 'Address 2']
            possible_city_cols = ['City', 'Municipality', 'Town', 'facility_city']
            possible_county_cols = ['County', 'County Name', 'county_name']
            possible_zip_cols = ['Zip', 'ZIP', 'Zip Code', 'ZIP Code', 'Postal Code', 'zip_code']
            possible_facility_name_cols = ['Facility Name', 'Name', 'Facility_Name', 'FacilityName', 'facility_name']
            possible_capacity_cols = ['Capacity', 'Tank Capacity', 'Volume', 'Size', 'Gallons', 'capacity_gallons', 'Capacity in Gallons']
            possible_content_cols = ['Content', 'Product', 'Substance', 'Material', 'product_stored', 'Tank Type Name']
            possible_status_cols = ['Status', 'Tank Status', 'Facility Status', 'facility_status']
            possible_install_date_cols = ['Install Date', 'Installation Date', 'Date Installed', 'Built Date', 'date_installed']
            possible_type_cols = ['Type', 'Tank Type', 'Facility Type', 'Storage Type', 'facility_type']
            
            # Helper function to find column value
            def find_column_value(possible_cols, default=''):
                for col in possible_cols:
                    if col in row.index:
                        return safe_string(row.get(col, default))
                return default
            
            # Map the columns
            processed_row['facility_id'] = find_column_value(possible_facility_id_cols)
            processed_row['tank_id'] = find_column_value(possible_tank_id_cols)
            processed_row['tank_location'] = find_column_value(possible_address_cols)
            processed_row['city'] = find_column_value(possible_city_cols)
            processed_row['zip'] = find_column_value(possible_zip_cols)[:5]
            processed_row['county'] = find_column_value(possible_county_cols)
            processed_row['facility_name'] = find_column_value(possible_facility_name_cols)
            
            # Tank type - default to UST for bulk storage
            tank_type = find_column_value(possible_type_cols)
            if 'underground' in tank_type.lower() or 'ust' in tank_type.lower():
                processed_row['ust_or_ast'] = 'UST'
            elif 'above' in tank_type.lower() or 'ast' in tank_type.lower():
                processed_row['ust_or_ast'] = 'AST'
            else:
                processed_row['ust_or_ast'] = 'UST'  # Default assumption
            
            # Installation date
            install_date = find_column_value(possible_install_date_cols)
            processed_row['year_installed'] = format_date_for_output(install_date)
            processed_row['tank_install_year_only'] = parse_year_from_date(install_date)
            
            # Tank size and range
            capacity = find_column_value(possible_capacity_cols)
            processed_row['tank_size__gallons_'] = safe_int(capacity)
            processed_row['size_range'] = determine_size_range(capacity)
            
            # Construction details
            processed_row['tank_construction'] = ''
            processed_row['piping_construction'] = ''
            processed_row['tank_construction_rating'] = ''
            processed_row['secondary_containment__ast_'] = ''
            processed_row['tank_tightness'] = ''
            
            # Content/Product
            processed_row['content_description'] = find_column_value(possible_content_cols)
            
            # Tank status
            processed_row['tank_status'] = find_column_value(possible_status_cols)
            
            # LUST information
            processed_row['lust'] = ''
            processed_row['lust_status'] = ''
            
            # Last synch date
            processed_row['last_synch_date'] = datetime.now().strftime('%Y/%m/%d')
            
            processed_rows.append(processed_row)
        
        return pd.DataFrame(processed_rows)
        
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def process_all_new_york_data():
    """Process all downloaded New York data files"""
    print(f"\n=== Starting data processing for {STATE_NAME} ===\n")
    
    all_data_frames = []
    
    # Process each file in input folder
    for file in os.listdir(INPUT_PATH):
        if file.endswith('.xlsx') and 'New_York' in file:
            file_path = os.path.join(INPUT_PATH, file)
            print(f"Processing: {file}")
            
            df = process_new_york_file(file_path)
            if not df.empty:
                all_data_frames.append(df)
                print(f"  Processed {len(df)} records")
    
    if not all_data_frames:
        print("No data frames to combine!")
        print("Files in input folder:")
        for file in os.listdir(INPUT_PATH):
            print(f"  - {file}")
        return
    
    # Combine all data
    print(f"\nCombining data from {len(all_data_frames)} file(s)...")
    formatted_df = pd.concat(all_data_frames, ignore_index=True)
    
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
    
    # Save the formatted data as xlsx
    output_file = os.path.join(OUTPUT_PATH, f'{STATE_NAME.replace(" ", "_")}_Formatted.xlsx')
    formatted_df.to_excel(output_file, index=False)
    print(f"\n✓ Saved formatted data to: {output_file}")
    print(f"  Total records: {len(formatted_df)}")
    print(f"  Total counties: {formatted_df['county'].nunique()}")
    print(f"  Total facilities: {formatted_df['facility_id'].nunique()}")
    
    # Show sample of mapped data
    print("\nSample of mapped data (first 3 records):")
    print(formatted_df[['facility_id', 'tank_id', 'facility_name', 'city', 'county', 'tank_status']].head(3).to_string())
    
    # Process LUST data if available
    process_lust_data_formatted(formatted_df)

def process_lust_data_formatted(formatted_df):
    """Process LUST data and update the formatted dataframe"""
    try:
        print('\n=== Processing LUST Data ===')
        lust_file = os.path.join(BASE_PATH, "L-UST_Data", "LustDataAllStates.xlsx")
        
        if not os.path.exists(lust_file):
            print(f"Warning: LUST data file not found at {lust_file}")
            final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME.replace(" ", "_")}_Final_Formatted.xlsx')
            formatted_df.to_excel(final_output, index=False)
            return formatted_df
            
        LustData = pd.read_excel(lust_file)
        NY_Lust = LustData[LustData['State Name'] == STATE_NAME]
        
        if len(NY_Lust) == 0:
            print(f"No LUST records found for {STATE_NAME}")
            final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME.replace(" ", "_")}_Final_Formatted.xlsx')
            formatted_df.to_excel(final_output, index=False)
            return formatted_df
        
        print(f'Found {len(NY_Lust)} LUST records for {STATE_NAME}')
        
        # Save New York LUST data
        ny_lust_file = os.path.join(REQUIRED_PATH, f'{STATE_NAME.replace(" ", "_")}_LustData.xlsx')
        NY_Lust.to_excel(ny_lust_file, index=False)
        
        # Create location matching key
        if 'Address' in NY_Lust.columns and 'City' in NY_Lust.columns:
            NY_Lust['location_city'] = (NY_Lust['Address'].astype(str).str.strip() + '_' + 
                                        NY_Lust['City'].astype(str).str.strip()).str.upper()
            
            formatted_df['location_city'] = (formatted_df['tank_location'].astype(str) + '_' + 
                                            formatted_df['city'].astype(str)).str.upper()
            
            # Remove duplicates from LUST data
            NY_Lust_unique = NY_Lust.drop_duplicates(subset='location_city', keep='first')
            
            # Merge to find matches
            merged = formatted_df.merge(NY_Lust_unique[['location_city', 'Status']], 
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
        
        # Save final merged data as xlsx
        final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME.replace(" ", "_")}_Final_Formatted.xlsx')
        formatted_df.to_excel(final_output, index=False)
        print(f"✓ Saved final formatted data with LUST info to: {final_output}")
        
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
        
        # Show tank status breakdown
        print(f"\nTank status breakdown:")
        status_counts = formatted_df['tank_status'].value_counts()
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        # Show size range breakdown
        print(f"\nSize range breakdown:")
        size_counts = formatted_df['size_range'].value_counts()
        for size_range, count in size_counts.items():
            print(f"  {size_range}: {count}")
        
        # Show LUST status breakdown
        print(f"\nLUST status breakdown:")
        lust_status_counts = formatted_df['lust_status'].value_counts()
        for status, count in lust_status_counts.items():
            if status:  # Only show non-empty statuses
                print(f"  {status}: {count}")
        
        return formatted_df
        
    except Exception as e:
        print(f"Error processing LUST data: {e}")
        import traceback
        traceback.print_exc()
        
        # Save without LUST data
        final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME.replace(" ", "_")}_Final_Formatted.xlsx')
        formatted_df.to_excel(final_output, index=False)
        return formatted_df

def main():
    """Main execution function"""
    print(f"=== New York UST Data Processing Script ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup folder structure
    log_file = setup_folder_structure()
    print(f"Log file: {log_file}")
    
    # Clear input folder if needed
    clear_input_folder()
    
    # Download New York data
    print("\n=== Starting Data Download ===")
    downloaded_files = download_new_york_data()
    
    if downloaded_files:
        print(f"\n✓ Successfully downloaded {len(downloaded_files)} file(s):")
        for file in downloaded_files:
            print(f"  - {file}")
        
        # Process the downloaded data
        print("\n=== Starting Data Processing ===")
        process_all_new_york_data()
        
    else:
        print("\n❌ No files were downloaded. Please check the download process.")
        
        # Check if there are existing files to process
        existing_files = []
        if os.path.exists(INPUT_PATH):
            existing_files = [f for f in os.listdir(INPUT_PATH) if f.endswith('.xlsx')]
        
        if existing_files:
            print(f"\nFound {len(existing_files)} existing Excel files in input folder:")
            for file in existing_files:
                print(f"  - {file}")
            
            response = input("Would you like to process these existing files? (y/n): ")
            if response.lower() == 'y':
                process_all_new_york_data()
            else:
                print("Skipping processing of existing files.")
        else:
            print("No existing files found in input folder.")
    
    print(f"\n=== Processing Complete ===")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Check the output folder: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
