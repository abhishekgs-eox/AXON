from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime
import numpy as np

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Delaware"
STATE_ABBR = "DE"
UST_URL = "https://data.delaware.gov/Energy-and-Environment/Underground-Storage-Tanks/jaq4-q4vs/about_data"
AST_URL = "https://data.delaware.gov/Energy-and-Environment/Aboveground-Storage-Tanks/cgmv-7ssg/about_data"

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

def download_delaware_data_from_url(url, tank_type):
    """Download Delaware data from a specific URL"""
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
        
        print(f"\nNavigating to {tank_type} URL: {url}")
        page.goto(url, wait_until='networkidle')
        
        page.wait_for_load_state('domcontentloaded')
        time.sleep(3)
        
        try:
            print(f"Looking for Export button for {tank_type} data...")
            
            # Click the Export button
            export_selectors = [
                'button:has-text("Export")',
                'a:has-text("Export")',
                '.export-btn',
                '#export-btn',
                'button[aria-label="Export"]',
                '//button[contains(text(), "Export")]',
                'text="Export"'
            ]
            
            export_found = False
            
            for selector in export_selectors:
                try:
                    if selector.startswith('//'):
                        locator = page.locator(f'xpath={selector}')
                    else:
                        locator = page.locator(selector)
                    
                    if locator.count() > 0:
                        print(f"✓ Found Export button using selector: {selector}")
                        locator.first.click()
                        export_found = True
                        time.sleep(2)
                        break
                except:
                    continue
            
            if export_found:
                # After clicking Export, look for CSV option
                print("Looking for CSV download option...")
                
                csv_selectors = [
                    'text="CSV"',
                    'a:has-text("CSV")',
                    'button:has-text("CSV")',
                    '[data-format="csv"]',
                    '.export-csv',
                    '//a[contains(text(), "CSV")]',
                    'label:has-text("CSV")',
                    'input[value="csv"]'
                ]
                
                csv_found = False
                
                for selector in csv_selectors:
                    try:
                        if selector.startswith('//'):
                            locator = page.locator(f'xpath={selector}')
                        else:
                            locator = page.locator(selector)
                        
                        if locator.count() > 0:
                            print(f"✓ Found CSV option")
                            locator.first.click()
                            csv_found = True
                            time.sleep(1)
                            break
                    except:
                        continue
                
                # Now click the Download button in the modal
                print("Looking for Download button in export dialog...")
                
                download_button_selectors = [
                    'button:has-text("Download")',
                    'button.btn-primary:has-text("Download")',
                    '.btn:has-text("Download")',
                    '//button[contains(text(), "Download") and @type="submit"]',
                    'button[type="submit"]:has-text("Download")'
                ]
                
                for selector in download_button_selectors:
                    try:
                        if selector.startswith('//'):
                            download_btn = page.locator(f'xpath={selector}')
                        else:
                            download_btn = page.locator(selector)
                        
                        download_buttons = download_btn.all()
                        for btn in download_buttons:
                            if btn.is_visible():
                                print("✓ Found Download button")
                                
                                # Create unique filename for each tank type
                                original_filename = f"{tank_type}_data.csv"
                                
                                with page.expect_download(timeout=30000) as download_info:
                                    btn.click()
                                    print(f"Clicked Download button for {tank_type}, waiting for file...")
                                
                                download = download_info.value
                                
                                # Save with tank type prefix
                                final_filename = f"{STATE_NAME}_{tank_type}_data.csv"
                                final_path = os.path.join(DOWNLOAD_PATH, final_filename)
                                download.save_as(final_path)
                                
                                downloaded_files.append(final_filename)
                                print(f"✓ Downloaded: {final_filename}")
                                print(f"  File size: {os.path.getsize(final_path) / 1024 / 1024:.2f} MB")
                                break
                        
                        if downloaded_files:
                            break
                            
                    except Exception as e:
                        continue
            
            if not downloaded_files:
                print(f"Failed to download {tank_type} data, taking screenshot...")
                screenshot_path = os.path.join(STATE_PATH, f"delaware_{tank_type}_debug.png")
                page.screenshot(path=screenshot_path)
                print(f"Screenshot saved to: {screenshot_path}")
                    
        except Exception as e:
            print(f"Error during {tank_type} download: {e}")
        
        browser.close()
        
    return downloaded_files

def download_all_delaware_data():
    """Download both UST and AST data for Delaware"""
    all_downloaded_files = []
    
    # Download UST data
    ust_files = download_delaware_data_from_url(UST_URL, "UST")
    all_downloaded_files.extend(ust_files)
    
    # Wait a bit between downloads
    time.sleep(2)
    
    # Download AST data
    ast_files = download_delaware_data_from_url(AST_URL, "AST")
    all_downloaded_files.extend(ast_files)
    
    return all_downloaded_files

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

def process_delaware_file(file_path, tank_type):
    """Process a single Delaware data file"""
    print(f"\nProcessing {tank_type} file: {os.path.basename(file_path)}")
    
    # Read the CSV file
    df_raw = pd.read_csv(file_path)
    
    print(f"File shape: {df_raw.shape}")
    print(f"Columns found: {list(df_raw.columns)}")
    
    processed_rows = []
    
    for idx, row in df_raw.iterrows():
        processed_row = {}
        
        # State information
        processed_row['state'] = STATE_NAME
        processed_row['state_name'] = STATE_ABBR
        
        # Map Delaware specific columns
        processed_row['facility_id'] = safe_string(row.get('ProgID', ''))
        processed_row['tank_id'] = safe_string(row.get('UnitID', ''))
        processed_row['tank_location'] = safe_string(row.get('Facility_Address1', ''))
        processed_row['city'] = safe_string(row.get('Facility_City', ''))
        processed_row['zip'] = safe_string(row.get('Facility_Zip', ''))[:5]
        
        # County - not in Delaware data
        processed_row['county'] = ''
        
        # Tank type - UST or AST based on which file we're processing
        processed_row['ust_or_ast'] = tank_type
        
        # Installation date
        date_value = row.get('Install_Date', '')
        processed_row['year_installed'] = format_date_for_output(date_value)
        processed_row['tank_install_year_only'] = parse_year_from_date(date_value)
        
        # Tank size and range
        tank_size = row.get('Capacity', 0)
        processed_row['tank_size__gallons_'] = safe_int(tank_size)
        processed_row['size_range'] = determine_size_range(tank_size)
        
        # Construction details
        processed_row['tank_construction'] = safe_string(row.get('Tank_Material', ''))
        processed_row['piping_construction'] = ''  # Not in Delaware data
        
        # Tank construction rating - use Alt_Tank_ID if available
        processed_row['tank_construction_rating'] = safe_string(row.get('Alt_Tank_ID', ''))
        
        # Secondary containment - not directly in Delaware data
        processed_row['secondary_containment__ast_'] = ''
        
        # Content/Product
        processed_row['content_description'] = safe_string(row.get('Tank_Substance', ''))
        
        # Tank tightness - not in Delaware data
        processed_row['tank_tightness'] = ''
        
        # Facility name
        processed_row['facility_name'] = safe_string(row.get('Site_Name_UsedBy_Program', ''))
        
        # Tank status
        processed_row['tank_status'] = safe_string(row.get('Tank_Status', ''))
        
        # LUST information - will be updated later
        processed_row['lust'] = ''
        processed_row['lust_status'] = ''
        
        # Last synch date
        processed_row['last_synch_date'] = datetime.now().strftime('%Y/%m/%d')
        
        processed_rows.append(processed_row)
    
    return pd.DataFrame(processed_rows)

def process_delaware_data():
    """Process all downloaded Delaware data files"""
    print(f"\n=== Starting data processing for {STATE_NAME} ===\n")
    
    all_data_frames = []
    
    # Process UST file
    ust_file = None
    for file in os.listdir(INPUT_PATH):
        if 'UST' in file and file.endswith('.csv'):
            ust_file = os.path.join(INPUT_PATH, file)
            break
    
    if ust_file:
        ust_df = process_delaware_file(ust_file, 'UST')
        all_data_frames.append(ust_df)
        print(f"Processed {len(ust_df)} UST records")
    
    # Process AST file
    ast_file = None
    for file in os.listdir(INPUT_PATH):
        if 'AST' in file and file.endswith('.csv'):
            ast_file = os.path.join(INPUT_PATH, file)
            break
    
    if ast_file:
        ast_df = process_delaware_file(ast_file, 'AST')
        all_data_frames.append(ast_df)
        print(f"Processed {len(ast_df)} AST records")
    
    if not all_data_frames:
        print("No data files found to process!")
        return
    
    # Combine all dataframes
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
    
    # Save the formatted data
    output_file = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Formatted.xlsx')
    formatted_df.to_excel(output_file, index=False)
    print(f"\n✓ Saved formatted data to: {output_file}")
    print(f"  Total records: {len(formatted_df)}")
    print(f"  UST records: {(formatted_df['ust_or_ast'] == 'UST').sum()}")
    print(f"  AST records: {(formatted_df['ust_or_ast'] == 'AST').sum()}")
    
    # Show sample of mapped data
    print("\nSample of mapped data (first 3 records):")
    print(formatted_df[['facility_id', 'tank_id', 'facility_name', 'city', 'ust_or_ast', 'tank_status']].head(3).to_string())
    
    # Process LUST data if available
    process_lust_data_formatted(formatted_df)

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
        DE_Lust = LustData[LustData['State Name'] == STATE_NAME]
        
        if len(DE_Lust) == 0:
            print(f"No LUST records found for {STATE_NAME}")
            final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
            formatted_df.to_excel(final_output, index=False)
            return formatted_df
        
        print(f'Found {len(DE_Lust)} LUST records for {STATE_NAME}')
        
        # Save Delaware LUST data
        de_lust_file = os.path.join(REQUIRED_PATH, f'{STATE_NAME}LustData.xlsx')
        DE_Lust.to_excel(de_lust_file, index=False)
        
        # Create location matching key
        if 'Address' in DE_Lust.columns and 'City' in DE_Lust.columns:
            DE_Lust['location_city'] = (DE_Lust['Address'].astype(str).str.strip() + '_' + 
                                        DE_Lust['City'].astype(str).str.strip()).str.upper()
            
            formatted_df['location_city'] = (formatted_df['tank_location'].astype(str) + '_' + 
                                            formatted_df['city'].astype(str)).str.upper()
            
            # Remove duplicates from LUST data
            DE_Lust_unique = DE_Lust.drop_duplicates(subset='location_city', keep='first')
            
            # Merge to find matches
            merged = formatted_df.merge(DE_Lust_unique[['location_city', 'Status']], 
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
        print(f"UST tanks: {(formatted_df['ust_or_ast'] == 'UST').sum()}")
        print(f"AST tanks: {(formatted_df['ust_or_ast'] == 'AST').sum()}")
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
    print(f"Starting {STATE_NAME} UST/AST Data Download and Processing")
    print(f"{'='*60}")
    print(f"Base path: {BASE_PATH}")
    print(f"UST URL: {UST_URL}")
    print(f"AST URL: {AST_URL}")
    
    # Setup folder structure
    log_file = setup_folder_structure()
    print(f"Log file: {log_file}")
    
    # Optional: Clear input folder
    clear_input_folder()
    
    # Download files from both URLs
    print(f"\n=== Downloading UST and AST data for {STATE_NAME} ===\n")
    downloaded_files = download_all_delaware_data()
    
    if downloaded_files:
        print(f"\n✓ Successfully downloaded {len(downloaded_files)} file(s):")
        for file in downloaded_files:
            print(f"  - {file}")
    else:
        print("\n✗ No files were downloaded.")
        print("Please check:")
        print("1. Both websites are accessible")
        print("2. The Export buttons are visible")
        print("3. The screenshots in the state folder for debugging")
        return
    
    # Wait for files to be completely written
    time.sleep(3)
    
    # Process the data
    process_delaware_data()
    
    print(f"\n{'='*60}")
    print(f'{STATE_NAME} processing completed!')
    print(f"{'='*60}")

if __name__ == "__main__":
    main()