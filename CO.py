from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime
import numpy as np

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Colorado"
STATE_ABBR = "CO"
URL = "https://data.colorado.gov/Energy/Regulated-Storage-Tanks-in-Colorado-Oil-Public-Saf/qszy-xfii/about_data"

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

def download_colorado_data():
    """Download Colorado UST data using Playwright"""
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
        
        # Wait for page to load completely
        page.wait_for_load_state('domcontentloaded')
        time.sleep(3)
        
        try:
            # STEP 1: Click on Data tab
            print("Looking for Data tab...")
            data_tab = page.locator('xpath=/html/body/main/div/div[1]/div/div[2]/div/forge-tab-bar/forge-tab[2]')
            if data_tab.count() > 0:
                print("✓ Found Data tab")
                data_tab.click()
                print("✓ Clicked on Data tab")
                time.sleep(3)  # Wait for tab content to load
            else:
                print("Data tab not found")
                screenshot_path = os.path.join(STATE_PATH, "colorado_data_tab_debug.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Screenshot saved to: {screenshot_path}")
                browser.close()
                return downloaded_files
            
            # STEP 2: Click on Export button
            print("Looking for Export button...")
            export_button = page.locator('xpath=/html/body/main/div/div[1]/div/div[2]/div/div/div/forge-button/div')
            if export_button.count() > 0:
                print("✓ Found Export button")
                export_button.click()
                print("✓ Clicked Export button, waiting for dialog...")
                time.sleep(3)  # Wait for export dialog to appear
            else:
                print("Export button not found")
                screenshot_path = os.path.join(STATE_PATH, "colorado_export_debug.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Screenshot saved to: {screenshot_path}")
                browser.close()
                return downloaded_files
            
            # STEP 3: Click on Download button in the dialog
            print("Looking for Download button in dialog...")
            download_button = page.locator('xpath=/html/body/main/div/div[1]/div/div[1]/forge-dialog/div/forge-scaffold/div[3]/forge-toolbar/forge-button[2]')
            if download_button.count() > 0:
                print("✓ Found Download button")
                
                # Wait for download
                with page.expect_download(timeout=30000) as download_info:
                    download_button.click()
                    print("✓ Clicked Download button, waiting for file...")
                
                download = download_info.value
                suggested_filename = download.suggested_filename
                
                # Save to our download directory
                final_path = os.path.join(DOWNLOAD_PATH, suggested_filename)
                download.save_as(final_path)
                
                downloaded_files.append(suggested_filename)
                print(f"✓ Downloaded: {suggested_filename}")
                print(f"  File size: {os.path.getsize(final_path) / 1024 / 1024:.2f} MB")
                
            else:
                print("Download button not found in dialog")
                screenshot_path = os.path.join(STATE_PATH, "colorado_download_debug.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Screenshot saved to: {screenshot_path}")
                    
        except Exception as e:
            print(f"Error during download: {e}")
            # Take screenshot on error
            try:
                error_screenshot = os.path.join(STATE_PATH, "colorado_error_debug.png")
                page.screenshot(path=error_screenshot)
                print(f"Error screenshot saved to: {error_screenshot}")
            except:
                pass
            
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

def process_colorado_data():
    """Process the downloaded Colorado data with exact formatting"""
    print(f"\n=== Starting data processing for {STATE_NAME} ===\n")
    
    # Find the downloaded file - could be .csv or .xlsx
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
        
        # Process each row
        processed_rows = []
        
        # Common column name mappings for Colorado data
        for idx, row in df_raw.iterrows():
            processed_row = {}
            
            # State information
            processed_row['state'] = STATE_NAME
            processed_row['state_name'] = STATE_ABBR
            
            # Facility and tank IDs - adjust based on actual column names
            processed_row['facility_id'] = safe_string(row.get('Facility ID', row.get('FacilityID', row.get('FacilityId', row.get('Site ID', '')))))
            processed_row['tank_id'] = safe_string(row.get('Tank ID', row.get('TankID', row.get('TankId', row.get('Tank Number', '')))))
            
            # Location information
            processed_row['tank_location'] = safe_string(row.get('Address', row.get('Street Address', row.get('Street', row.get('Location', '')))))
            processed_row['city'] = safe_string(row.get('City', row.get('Municipality', '')))
            processed_row['zip'] = safe_string(row.get('Zip', row.get('Zip Code', row.get('ZipCode', row.get('Postal Code', '')))))[:5]
            processed_row['county'] = safe_string(row.get('County', row.get('County Name', '')))
            
            # Tank type - UST or AST
            tank_type = safe_string(row.get('Tank Type', row.get('Type', row.get('Storage Type', row.get('TankType', '')))))
            if 'underground' in tank_type.lower() or 'ust' in tank_type.lower():
                processed_row['ust_or_ast'] = 'UST'
            elif 'aboveground' in tank_type.lower() or 'ast' in tank_type.lower():
                processed_row['ust_or_ast'] = 'AST'
            else:
                processed_row['ust_or_ast'] = tank_type
            
            # Installation date
            date_value = row.get('Install Date', row.get('Installation Date', row.get('InstallDate', row.get('Date Installed', ''))))
            processed_row['year_installed'] = format_date_for_output(date_value)
            processed_row['tank_install_year_only'] = parse_year_from_date(date_value)
            
            # Tank size and range
            tank_size = row.get('Capacity', row.get('Tank Capacity', row.get('TankCapacity', row.get('Size', row.get('Volume', 0)))))
            processed_row['tank_size__gallons_'] = safe_int(tank_size)
            processed_row['size_range'] = determine_size_range(tank_size)
            
            # Construction details
            processed_row['tank_construction'] = safe_string(row.get('Tank Construction', row.get('TankConstruction', row.get('Tank Material', row.get('Construction Type', '')))))
            processed_row['piping_construction'] = safe_string(row.get('Piping Construction', row.get('PipingConstruction', row.get('Piping Material', row.get('Piping Type', '')))))
            processed_row['tank_construction_rating'] = safe_string(row.get('Construction Rating', row.get('Tank Rating', row.get('TankRating', ''))))
            
            # Secondary containment
            containment = safe_string(row.get('Secondary Containment', row.get('SecondaryContainment', row.get('Double Walled', row.get('Containment', '')))))
            processed_row['secondary_containment__ast_'] = containment
            
            # Content/Product
            processed_row['content_description'] = safe_string(row.get('Product', row.get('Contents', row.get('Substance', row.get('Material Stored', row.get('Product Stored', ''))))))
            
            # Tank tightness
            processed_row['tank_tightness'] = safe_string(row.get('Tank Tightness', row.get('TankTightness', row.get('Tightness Testing', ''))))
            
            # Facility name
            processed_row['facility_name'] = safe_string(row.get('Facility Name', row.get('FacilityName', row.get('Company Name', row.get('Business Name', '')))))
            
            # Tank status
            processed_row['tank_status'] = safe_string(row.get('Status', row.get('Tank Status', row.get('TankStatus', row.get('Operating Status', '')))))
            
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
        print(formatted_df.head(3).to_string())
        
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
        CO_Lust = LustData[LustData['State Name'] == STATE_NAME]
        
        if len(CO_Lust) == 0:
            print(f"No LUST records found for {STATE_NAME}")
            final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
            formatted_df.to_excel(final_output, index=False)
            return formatted_df
        
        print(f'Found {len(CO_Lust)} LUST records for {STATE_NAME}')
        
        # Save Colorado LUST data
        co_lust_file = os.path.join(REQUIRED_PATH, f'{STATE_NAME}LustData.xlsx')
        CO_Lust.to_excel(co_lust_file, index=False)
        
        # Create location matching key
        if 'Address' in CO_Lust.columns and 'City' in CO_Lust.columns:
            CO_Lust['location_city'] = (CO_Lust['Address'].astype(str).str.strip() + '_' + 
                                        CO_Lust['City'].astype(str).str.strip()).str.upper()
            
            formatted_df['location_city'] = (formatted_df['tank_location'].astype(str) + '_' + 
                                            formatted_df['city'].astype(str)).str.upper()
            
            # Remove duplicates from LUST data
            CO_Lust_unique = CO_Lust.drop_duplicates(subset='location_city', keep='first')
            
            # Merge to find matches
            merged = formatted_df.merge(CO_Lust_unique[['location_city', 'Status']], 
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
    downloaded_files = download_colorado_data()
    
    if downloaded_files:
        print(f"\n✓ Successfully downloaded {len(downloaded_files)} file(s):")
        for file in downloaded_files:
            print(f"  - {file}")
    else:
        print("\n✗ No files were downloaded.")
        print("Please check:")
        print("1. The website is accessible")
        print("2. The Export button is visible")
        print("3. The screenshots in the state folder for debugging")
        return
    
    # Wait for files to be completely written
    time.sleep(3)
    
    # Process the data
    process_colorado_data()
    
    print(f"\n{'='*60}")
    print(f'{STATE_NAME} processing completed!')
    print(f"{'='*60}")

if __name__ == "__main__":
    main()