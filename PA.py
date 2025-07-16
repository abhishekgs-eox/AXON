from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime
import numpy as np

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Pennsylvania"
STATE_ABBR = "PA"
URL = "http://cedatareporting.pa.gov/Reportserver/Pages/ReportViewer.aspx?/Public/DEP/Tanks/SSRS/TANKS"

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

def download_pennsylvania_data():
    """Download tank data from Pennsylvania DEP website"""
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
            print(f"Navigating to {URL}")
            page.goto(URL, wait_until='networkidle', timeout=120000)
            page.wait_for_load_state('domcontentloaded')
            time.sleep(10)  # Give report viewer time to load
            
            # Look for View Report button
            print("\nLooking for 'View Report' button...")
            view_report_selectors = [
                'button:has-text("View Report")',
                'input[value="View Report"]',
                '#ReportViewerControl_ctl04_ctl00',  # Common ID for SSRS View Report button
                '//button[contains(text(), "View Report")]',
                '//input[@value="View Report"]',
                '.ToolBarButtonsCell input[type="submit"]',
                'input[title="View Report"]'
            ]
            
            view_clicked = False
            for selector in view_report_selectors:
                try:
                    if selector.startswith('//'):
                        element = page.locator(f'xpath={selector}')
                    else:
                        element = page.locator(selector).first
                    
                    if element.is_visible():
                        print(f"✓ Found View Report button")
                        element.click()
                        print("  Clicked View Report, waiting for data to load...")
                        view_clicked = True
                        time.sleep(15)  # Wait for report to generate
                        break
                except Exception as e:
                    continue
            
            if not view_clicked:
                print("  ✗ Could not find View Report button")
                # Take screenshot for debugging
                screenshot_path = os.path.join(STATE_PATH, "pennsylvania_view_debug.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"  Screenshot saved to: {screenshot_path}")
            
            # Wait for the report to fully load
            print("\nWaiting for report to fully load...")
            page.wait_for_load_state('networkidle', timeout=60000)
            time.sleep(5)
            
            # Look for Export dropdown
            print("\nLooking for Export dropdown...")
            export_selectors = [
                '#ReportViewerControl_ctl05_ctl04_ctl00_ButtonImg',  # Common ID for SSRS Export button
                'a[title="Export"]',
                'img[alt="Export"]',
                '//a[contains(@title, "Export")]',
                '#ReportViewerControl_ctl05_ctl04_ctl00',
                '.ToolBarButtonsCell a[title*="Export"]',
                'a:has(img[alt="Export"])'
            ]
            
            export_clicked = False
            for selector in export_selectors:
                try:
                    if selector.startswith('//'):
                        element = page.locator(f'xpath={selector}')
                    else:
                        element = page.locator(selector).first
                    
                    if element.is_visible():
                        print(f"✓ Found Export dropdown")
                        element.click()
                        print("  Clicked Export dropdown")
                        export_clicked = True
                        time.sleep(2)
                        break
                except Exception as e:
                    continue
            
            if not export_clicked:
                print("  ✗ Could not find Export dropdown")
                # Take screenshot for debugging
                screenshot_path = os.path.join(STATE_PATH, "pennsylvania_export_debug.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"  Screenshot saved to: {screenshot_path}")
            
            # Select CSV from dropdown
            print("\nLooking for CSV option...")
            csv_selectors = [
                'a:has-text("CSV (comma delimited)")',
                'a:has-text("CSV")',
                '//a[contains(text(), "CSV")]',
                '#ReportViewerControl_ctl05_ctl04_ctl00_Menu a[href*="CSV"]',
                '.ExportMenu a:has-text("CSV")'
            ]
            
            csv_downloaded = False
            for selector in csv_selectors:
                try:
                    if selector.startswith('//'):
                        element = page.locator(f'xpath={selector}')
                    else:
                        element = page.locator(selector).first
                    
                    if element.is_visible():
                        print(f"✓ Found CSV option")
                        
                        # Prepare for download
                        with page.expect_download(timeout=120000) as download_info:
                            element.click()
                            print("  Clicked CSV, waiting for download...")
                        
                        download = download_info.value
                        filename = f"{STATE_NAME}_Tank_Data.csv"
                        file_path = os.path.join(DOWNLOAD_PATH, filename)
                        download.save_as(file_path)
                        
                        downloaded_files.append(filename)
                        print(f"  ✓ Downloaded: {filename}")
                        csv_downloaded = True
                        break
                except Exception as e:
                    continue
            
            if not csv_downloaded:
                print("  ✗ Could not download CSV file")
                # Take screenshot for debugging
                screenshot_path = os.path.join(STATE_PATH, "pennsylvania_csv_debug.png")
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

def process_pennsylvania_tank_data():
    """Process Pennsylvania tank data"""
    tank_file = os.path.join(INPUT_PATH, f"{STATE_NAME}_Tank_Data.csv")
    
    if not os.path.exists(tank_file):
        print(f"Tank file not found: {tank_file}")
        return pd.DataFrame()
    
    try:
        # Read CSV file
        df_raw = pd.read_csv(tank_file, low_memory=False)
        print(f"Loaded tank data: {len(df_raw)} records")
        print(f"Columns found: {list(df_raw.columns)}")
        
        # Save raw data for debugging
        debug_file = os.path.join(REQUIRED_PATH, f"{STATE_NAME}_Raw_Debug.xlsx")
        df_raw.to_excel(debug_file, index=False)
        print(f"Saved raw data for debugging to: {debug_file}")
        
        processed_rows = []
        
        for idx, row in df_raw.iterrows():
            processed_row = {}
            
            # State information
            processed_row['state'] = STATE_NAME
            processed_row['state_name'] = STATE_ABBR
            
            # Map Pennsylvania specific columns
            processed_row['facility_id'] = safe_string(row.get('SITE_ID', ''))
            processed_row['tank_id'] = safe_string(row.get('SEQ_NUMBER', row.get('TANK_CODE', '')))
            
            # Address
            address1 = safe_string(row.get('PF_ADDRESS1', ''))
            address2 = safe_string(row.get('PF_ADDRESS2', ''))
            processed_row['tank_location'] = f"{address1} {address2}".strip()
            
            processed_row['city'] = safe_string(row.get('PF_CITY', ''))
            processed_row['zip'] = safe_string(row.get('PF_ZIP', ''))[:5]
            processed_row['county'] = safe_string(row.get('COUNTY', ''))
            
            # Tank type - check permit type
            permit_type = safe_string(row.get('PERMIT_TYPE', '')).lower()
            if 'ast' in permit_type or 'above' in permit_type:
                processed_row['ust_or_ast'] = 'AST'
            else:
                processed_row['ust_or_ast'] = 'UST'
            
            # Installation date
            date_value = row.get('DATE_INSTALLED', '')
            processed_row['year_installed'] = format_date_for_output(date_value)
            processed_row['tank_install_year_only'] = parse_year_from_date(date_value)
            
            # Tank size and range
            tank_size = row.get('CAPACITY', 0)
            processed_row['tank_size__gallons_'] = safe_int(tank_size)
            processed_row['size_range'] = determine_size_range(tank_size)
            
            # Construction details - not directly available
            processed_row['tank_construction'] = ''
            processed_row['piping_construction'] = ''
            processed_row['tank_construction_rating'] = ''
            
            # Secondary containment - not directly available
            processed_row['secondary_containment__ast_'] = ''
            
            # Content/Product
            processed_row['content_description'] = safe_string(row.get('SUBSTANCE_CODE', ''))
            
            # Tank tightness - check inspection dates
            last_inspection = safe_string(row.get('DATE_LAST_INSPECTION', ''))
            if last_inspection:
                processed_row['tank_tightness'] = 'Yes'
            else:
                processed_row['tank_tightness'] = ''
            
            # Facility name
            processed_row['facility_name'] = safe_string(row.get('PF_NAME', ''))
            
            # Tank status
            processed_row['tank_status'] = safe_string(row.get('STATUS', ''))
            
            # LUST information - initially no
            processed_row['lust'] = 'No'
            processed_row['lust_status'] = ''
            
            # Last synch date
            processed_row['last_synch_date'] = datetime.now().strftime('%Y/%m/%d')
            
            processed_rows.append(processed_row)
        
        return pd.DataFrame(processed_rows)
        
    except Exception as e:
        print(f"Error processing tank file: {e}")
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
        PA_Lust = LustData[LustData['State Name'] == STATE_NAME]
        
        if len(PA_Lust) == 0:
            print(f"No statewide LUST records found for {STATE_NAME}")
            return formatted_df
        
        print(f'Found {len(PA_Lust)} statewide LUST records for {STATE_NAME}')
        
        # Save Pennsylvania LUST data
        pa_lust_file = os.path.join(REQUIRED_PATH, f'{STATE_NAME}_Statewide_LustData.xlsx')
        PA_Lust.to_excel(pa_lust_file, index=False)
        
        # Create location matching key
        if 'Address' in PA_Lust.columns and 'City' in PA_Lust.columns:
            PA_Lust['location_city'] = (PA_Lust['Address'].astype(str).str.strip() + '_' + 
                                        PA_Lust['City'].astype(str).str.strip()).str.upper()
            
            formatted_df['location_city'] = (formatted_df['tank_location'].astype(str) + '_' + 
                                            formatted_df['city'].astype(str)).str.upper()
            
            # Remove duplicates from LUST data
            PA_Lust_unique = PA_Lust.drop_duplicates(subset='location_city', keep='first')
            
            # Count how many records will be updated
            existing_lust = (formatted_df['lust'] == 'Yes').sum()
            
            # Merge to find matches
            merged = formatted_df.merge(PA_Lust_unique[['location_city', 'Status']], 
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

def process_all_pennsylvania_data():
    """Process all downloaded Pennsylvania data files"""
    print(f"\n=== Starting data processing for {STATE_NAME} ===\n")
    
    # Process tank data
    formatted_df = process_pennsylvania_tank_data()
    
    if formatted_df.empty:
        print("No tank data to process!")
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
    print(f"AST tanks: {(formatted_df['ust_or_ast'] == 'AST').sum()}")
    print(f"LUST sites: {(formatted_df['lust'] == 'Yes').sum()}")
    
    # Show tank status breakdown
    print(f"\nTank status breakdown:")
    status_counts = formatted_df['tank_status'].value_counts()
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    # Show county breakdown
    print(f"\nRecords by county (top 10):")
    county_counts = formatted_df['county'].value_counts().head(10)
    for county, count in county_counts.items():
        print(f"  {county}: {count}")
    
    # Show sample of mapped data
    print("\nSample of mapped data (first 3 records):")
    sample_cols = ['facility_id', 'facility_name', 'city', 'county', 'tank_status', 'ust_or_ast', 'lust']
    print(formatted_df[sample_cols].head(3).to_string())

def main():
    """Main function to orchestrate the entire process"""
    print(f"{'='*60}")
    print(f"Starting {STATE_NAME} Tank Data Download and Processing")
    print(f"{'='*60}")
    print(f"Base path: {BASE_PATH}")
    print(f"Target URL: {URL}")
    
    # Setup folder structure
    log_file = setup_folder_structure()
    print(f"Log file: {log_file}")
    
    # Optional: Clear input folder
    clear_input_folder()
    
    # Download files
    print(f"\n=== Downloading {STATE_NAME} tank data ===\n")
    downloaded_files = download_pennsylvania_data()
    
    if downloaded_files:
        print(f"\n✓ Successfully downloaded {len(downloaded_files)} file(s):")
        for file in downloaded_files:
            print(f"  - {file}")
    else:
        print("\n✗ No files were downloaded.")
        print("Please check:")
        print("1. The website is accessible")
        print("2. The View Report button is visible and clickable")
        print("3. The Export dropdown is available after the report loads")
        print("4. The screenshots in the state folder for debugging")
        return
    
    # Wait for files to be completely written
    time.sleep(3)
    
    # Process all data
    process_all_pennsylvania_data()
    
    print(f"\n{'='*60}")
    print(f'{STATE_NAME} processing completed!')
    print(f"{'='*60}")

if __name__ == "__main__":
    main()