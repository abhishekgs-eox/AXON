from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime
import numpy as np

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Massachusetts"
STATE_ABBR = "MA"
URL = "https://ma-ust.windsorcloud.com/ust/facility/search/list?0"

# Dynamic paths based on state
STATE_PATH = os.path.join(BASE_PATH, "states", STATE_NAME)
INPUT_PATH = os.path.join(STATE_PATH, "Input")
OUTPUT_PATH = os.path.join(STATE_PATH, "Output")
REQUIRED_PATH = os.path.join(STATE_PATH, "Required")
DOWNLOAD_PATH = INPUT_PATH

# Standard column order for final output
COLUMN_ORDER = [
    'state', 'state_name', 'facility_id', 'tank_id', 'tank_location',
    'city', 'zip', 'ust_or_ast', 'year_installed', 'tank_install_year_only',
    'tank_size__gallons_', 'size_range', 'tank_construction', 'piping_construction',
    'secondary_containment__ast_', 'content_description', 'tank_tightness',
    'facility_name', 'lust', 'tank_construction_rating', 'county',
    'tank_status', 'lust_status', 'last_synch_date'
]

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

def download_massachusetts_data():
    """Download Massachusetts UST data by clicking Export"""
    downloaded_files = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # Set to False to see the browser
            downloads_path=DOWNLOAD_PATH
        )
        
        context = browser.new_context(
            accept_downloads=True,
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        try:
            print(f"Navigating to {URL}")
            page.goto(URL, wait_until='networkidle', timeout=60000)
            
            # Wait for page to fully load
            print("Waiting for page to load completely...")
            page.wait_for_load_state('domcontentloaded')
            page.wait_for_load_state('networkidle')
            time.sleep(5)
            
            # Look for Export button under Actions
            print("Looking for Export button...")
            
            # Try multiple selectors for Export button
            export_selectors = [
                'button:has-text("Export")',
                'a:has-text("Export")',
                'input[value="Export"]',
                '//button[contains(text(), "Export")]',
                '//a[contains(text(), "Export")]',
                'button.export',
                'a.export',
                '.actions button:has-text("Export")',
                '.actions a:has-text("Export")',
                '[title="Export"]',
                '[aria-label="Export"]'
            ]
            
            export_found = False
            
            for selector in export_selectors:
                try:
                    if selector.startswith('//'):
                        export_btn = page.locator(f'xpath={selector}')
                    else:
                        export_btn = page.locator(selector)
                    
                    if export_btn.count() > 0:
                        print(f"Found Export button using selector: {selector}")
                        
                        # Prepare for download
                        expected_filename = f"{STATE_NAME}_UST_Facilities_Export.csv"
                        
                        # Click Export and wait for download
                        with page.expect_download(timeout=30000) as download_info:
                            export_btn.first.click()
                            print("Clicked Export button, waiting for download...")
                        
                        download = download_info.value
                        
                        # Save the file
                        final_path = os.path.join(DOWNLOAD_PATH, expected_filename)
                        download.save_as(final_path)
                        
                        downloaded_files.append(expected_filename)
                        print(f"✓ Downloaded: {expected_filename}")
                        export_found = True
                        break
                        
                except Exception as e:
                    continue
            
            if not export_found:
                print("✗ Could not find Export button")
                
                # Take screenshot for debugging
                screenshot_path = os.path.join(STATE_PATH, f"{STATE_NAME}_page_debug.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Screenshot saved to: {screenshot_path}")
                
                # Try to find any buttons or links on the page
                print("\nDebugging - Looking for all buttons and links...")
                buttons = page.locator('button').all()
                print(f"Found {len(buttons)} buttons")
                for i, btn in enumerate(buttons[:10]):  # Show first 10
                    try:
                        text = btn.inner_text()
                        if text:
                            print(f"  Button {i+1}: {text}")
                    except:
                        pass
                
                links = page.locator('a').all()
                print(f"Found {len(links)} links")
                for i, link in enumerate(links[:10]):  # Show first 10
                    try:
                        text = link.inner_text()
                        if text and 'export' in text.lower():
                            print(f"  Link {i+1}: {text}")
                    except:
                        pass
                        
        except Exception as e:
            print(f"Error during download: {e}")
            import traceback
            traceback.print_exc()
            
            # Save screenshot on error
            screenshot_path = os.path.join(STATE_PATH, f"{STATE_NAME}_error_debug.png")
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"Error screenshot saved to: {screenshot_path}")
        
        browser.close()
        
    return downloaded_files

def safe_string(value):
    """Safely convert value to string"""
    if pd.isna(value) or value is None:
        return ''
    return str(value).strip()

def safe_int(value):
    """Safely convert value to integer"""
    if pd.isna(value) or value is None or value == '':
        return 0
    try:
        return int(float(value))
    except:
        return 0

def get_size_range(gallons):
    """Categorize tank size into ranges"""
    if pd.isna(gallons) or gallons <= 0:
        return 'Unknown'
    elif gallons <= 550:
        return '0-550'
    elif gallons <= 1100:
        return '551-1100'
    elif gallons <= 2000:
        return '1101-2000'
    elif gallons <= 5000:
        return '2001-5000'
    elif gallons <= 10000:
        return '5001-10000'
    elif gallons <= 20000:
        return '10001-20000'
    else:
        return '>20000'

def process_massachusetts_data():
    """Process the downloaded Massachusetts UST data"""
    print(f"\n=== Starting data processing for {STATE_NAME} ===\n")
    
    # Find the exported file
    exported_file = None
    for file in os.listdir(INPUT_PATH):
        if file.endswith(('.csv', '.xlsx', '.xls')) and STATE_NAME in file:
            exported_file = os.path.join(INPUT_PATH, file)
            break
    
    if not exported_file:
        print("✗ No exported file found!")
        return
    
    print(f"Processing: {os.path.basename(exported_file)}")
    
    try:
        # Read the file
        if exported_file.endswith('.csv'):
            df_raw = pd.read_csv(exported_file)
        else:
            df_raw = pd.read_excel(exported_file)
        
        print(f"Read {len(df_raw)} records")
        print(f"Columns found: {list(df_raw.columns)}")
        
        # Massachusetts column mappings
        ma_columns = {
            'UST Facility ID': 'facility_id',
            'Facility Name': 'facility_name',
            'Facility Address Line 1': 'tank_location',
            'Facility City': 'city',
            'Facility Zip': 'zip',
            'Owner Name': 'owner_name',
            'Owner Contact Name': 'owner_contact',
            'Operator Name': 'operator_name',
            'Operator Contact Name': 'operator_contact',
            'Last Inspection Date': 'last_inspection',
            'Next Inspection Due Date': 'next_inspection',
            'Last Cert Compliance Date': 'last_cert_compliance',
            'Next Cert Compliance Due Date': 'next_cert_compliance'
        }
        
        # Since this is facility-level data, we'll create one record per facility
        processed_rows = []
        
        for idx, row in df_raw.iterrows():
            processed_row = {}
            
            # State information
            processed_row['state'] = STATE_ABBR
            processed_row['state_name'] = STATE_NAME
            
            # Map available columns
            processed_row['facility_id'] = safe_string(row.get('UST Facility ID', ''))
            processed_row['facility_name'] = safe_string(row.get('Facility Name', ''))
            processed_row['tank_location'] = safe_string(row.get('Facility Address Line 1', ''))
            processed_row['city'] = safe_string(row.get('Facility City', ''))
            processed_row['zip'] = safe_string(row.get('Facility Zip', ''))[:5]
            
            # Since this is facility data without tank details, we'll set tank fields as empty
            processed_row['tank_id'] = ''
            processed_row['ust_or_ast'] = 'UST'  # Default to UST
            processed_row['year_installed'] = ''
            processed_row['tank_install_year_only'] = ''
            processed_row['tank_size__gallons_'] = 0
            processed_row['size_range'] = 'Unknown'
            processed_row['tank_construction'] = ''
            processed_row['piping_construction'] = ''
            processed_row['secondary_containment__ast_'] = ''
            processed_row['content_description'] = ''
            processed_row['tank_tightness'] = 'No'
            processed_row['tank_construction_rating'] = 'Unknown'
            processed_row['county'] = ''  # Massachusetts data doesn't include county
            processed_row['tank_status'] = 'Active'  # Assume active if in the system
            processed_row['lust'] = 'No'
            processed_row['lust_status'] = ''
            
            # Use last inspection date for last_synch_date if available
            last_inspection = row.get('Last Inspection Date', '')
            if pd.notna(last_inspection) and last_inspection:
                try:
                    date_obj = pd.to_datetime(last_inspection, errors='coerce')
                    if pd.notna(date_obj):
                        processed_row['last_synch_date'] = date_obj.strftime('%Y-%m-%d')
                    else:
                        processed_row['last_synch_date'] = datetime.now().strftime('%Y-%m-%d')
                except:
                    processed_row['last_synch_date'] = datetime.now().strftime('%Y-%m-%d')
            else:
                processed_row['last_synch_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Store additional Massachusetts-specific info in a note
            owner_info = safe_string(row.get('Owner Name', ''))
            operator_info = safe_string(row.get('Operator Name', ''))
            if owner_info or operator_info:
                note = f"Owner: {owner_info}, Operator: {operator_info}"
                # You could add this to an unused field or create a new column
            
            processed_rows.append(processed_row)
        
        # Create DataFrame with processed data
        formatted_df = pd.DataFrame(processed_rows)
        
        # Ensure all columns are present in the correct order
        for col in COLUMN_ORDER:
            if col not in formatted_df.columns:
                formatted_df[col] = ''
        
        formatted_df = formatted_df[COLUMN_ORDER]
        
        # Save the formatted data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Formatted_{timestamp}.xlsx')
        formatted_df.to_excel(output_file, index=False)
        print(f"\n✓ Saved formatted data to: {output_file}")
        
        # Also save as CSV
        csv_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Formatted_{timestamp}.csv')
        formatted_df.to_csv(csv_output, index=False)
        print(f"✓ Saved CSV version to: {csv_output}")
        
        print(f"\nData Summary:")
        print(f"  Total facilities: {len(formatted_df)}")
        print(f"  Total unique facilities: {formatted_df['facility_id'].nunique()}")
        print(f"  Cities: {formatted_df['city'].nunique()}")
        
        # Process LUST data if available
        process_lust_data_formatted(formatted_df, timestamp)
        
    except Exception as e:
        print(f"Error processing data: {e}")
        import traceback
        traceback.print_exc()

def process_lust_data_formatted(formatted_df, timestamp):
    """Process LUST data and update the formatted dataframe"""
    try:
        print('\n=== Processing LUST Data ===')
        lust_file = os.path.join(BASE_PATH, "L-UST_Data", "LustDataAllStates.xlsx")
        
        if not os.path.exists(lust_file):
            print(f"Warning: LUST data file not found at {lust_file}")
            final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_UST_Data_Final_Formatted_{timestamp}.xlsx')
            formatted_df.to_excel(final_output, index=False)
            return formatted_df
            
        LustData = pd.read_excel(lust_file)
        MA_Lust = LustData[LustData['State Name'] == STATE_NAME]
        
        if len(MA_Lust) == 0:
            print(f"No LUST records found for {STATE_NAME}")
            final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_UST_Data_Final_Formatted_{timestamp}.xlsx')
            formatted_df.to_excel(final_output, index=False)
            return formatted_df
        
        print(f'Found {len(MA_Lust)} LUST records for {STATE_NAME}')
        
        # Save Massachusetts LUST data
        ma_lust_file = os.path.join(REQUIRED_PATH, f'{STATE_NAME}LustData.xlsx')
        MA_Lust.to_excel(ma_lust_file, index=False)
        
        # Create matching keys
        if 'Address' in MA_Lust.columns and 'City' in MA_Lust.columns:
            MA_Lust['location_city'] = (MA_Lust['Address'].astype(str).str.strip().str.upper() + '_' + 
                                        MA_Lust['City'].astype(str).str.strip().str.upper())
            
            formatted_df['location_city'] = (formatted_df['tank_location'].astype(str).str.strip().str.upper() + '_' + 
                                            formatted_df['city'].astype(str).str.strip().str.upper())
            
            # Remove duplicates from LUST data
            MA_Lust_unique = MA_Lust.drop_duplicates(subset='location_city', keep='first')
            
            # Merge to find matches
            merged = formatted_df.merge(MA_Lust_unique[['location_city', 'Status']], 
                                      on='location_city', how='left')
            
            # Update lust and lust_status where matches found
            matches = merged['Status'].notna()
            formatted_df.loc[matches, 'lust'] = 'Yes'
            formatted_df.loc[matches, 'lust_status'] = merged.loc[matches, 'Status']
            
            # Remove temporary column
            formatted_df = formatted_df.drop('location_city', axis=1)
            
            print(f'Updated {matches.sum()} records with LUST information')
        
        # Save final merged data
        final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_UST_Data_Final_Formatted_{timestamp}.xlsx')
        formatted_df.to_excel(final_output, index=False)
        print(f"✓ Saved final formatted data with LUST info to: {final_output}")
        
        # Also save as CSV
        csv_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_UST_Data_Final_Formatted_{timestamp}.csv')
        formatted_df.to_csv(csv_output, index=False)
        print(f"✓ Also saved as CSV: {csv_output}")
        
        # Show summary statistics
        print(f"\n=== Final Summary Statistics ===")
        print(f"Total facilities: {formatted_df['facility_id'].nunique()}")
        print(f"Total records: {len(formatted_df)}")
        print(f"LUST sites: {(formatted_df['lust'] == 'Yes').sum()}")
        
        # Show city breakdown (top 10)
        print(f"\nRecords by city (top 10):")
        city_counts = formatted_df['city'].value_counts().head(10)
        for city, count in city_counts.items():
            print(f"  {city}: {count}")
        
        return formatted_df
        
    except Exception as e:
        print(f"Error processing LUST data: {e}")
        final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_UST_Data_Final_Formatted_{timestamp}.xlsx')
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
    
    # Download data
    print(f"\n=== Downloading {STATE_NAME} UST data ===\n")
    downloaded_files = download_massachusetts_data()
    
    if downloaded_files:
        print(f"\n✓ Successfully downloaded {len(downloaded_files)} file(s)")
    else:
        print("\n✗ No files were downloaded.")
        print("Please check:")
        print("1. The website is accessible")
        print("2. The Export button is visible")
        print("3. You may need to be logged in or have proper permissions")
        print("4. Check the screenshots in the state folder for debugging")
        return
    
    # Wait for files to be completely written
    time.sleep(3)
    
    # Process the data
    process_massachusetts_data()
    
    print(f"\n{'='*60}")
    print(f'{STATE_NAME} processing completed!')
    print(f"{'='*60}")

if __name__ == "__main__":
    main()