from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime
import numpy as np
import zipfile
import shutil

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Kentucky"
STATE_ABBR = "KY"
URL = "https://eec.ky.gov/Environmental-Protection/Waste/underground-storage-tank/Pages/Resources.aspx"

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
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                print("Input folder cleared.")

def download_kentucky_data():
    """Download Kentucky UST data using Playwright"""
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
            print("Looking for 'Documents of Interest' section...")
            
            # First try to find the Documents of Interest section
            section_found = False
            section_selectors = [
                'text="Documents of Interest"',
                'h2:has-text("Documents of Interest")',
                'h3:has-text("Documents of Interest")',
                '//*[contains(text(), "Documents of Interest")]',
                'strong:has-text("Documents of Interest")'
            ]
            
            for selector in section_selectors:
                try:
                    if selector.startswith('//'):
                        section = page.locator(f'xpath={selector}')
                    else:
                        section = page.locator(selector)
                    
                    if section.count() > 0:
                        print("✓ Found 'Documents of Interest' section")
                        section.first.scroll_into_view_if_needed()
                        section_found = True
                        time.sleep(1)
                        break
                except:
                    continue
            
            # Now look for UST Statewide Database Report link
            print("\nLooking for 'UST Statewide Database Report' link...")
            
            download_selectors = [
                'a:has-text("UST Statewide Database Report")',
                'text="UST Statewide Database Report"',
                '//a[contains(text(), "UST Statewide Database Report")]',
                'a:has-text("Statewide Database Report")',
                '//a[contains(text(), "Statewide Database")]',
                'a[href*="database"]',
                'a[href*="UST"]'
            ]
            
            download_clicked = False
            
            for selector in download_selectors:
                try:
                    if selector.startswith('//'):
                        download_link = page.locator(f'xpath={selector}')
                    else:
                        download_link = page.locator(selector)
                    
                    if download_link.count() > 0:
                        print("✓ Found UST Statewide Database Report link")
                        
                        # Scroll to it
                        download_link.first.scroll_into_view_if_needed()
                        time.sleep(1)
                        
                        # Get href for debugging
                        href = download_link.first.get_attribute('href')
                        if href:
                            print(f"  Link URL: {href[:100]}...")
                        
                        # Click and wait for download
                        print("Clicking download link...")
                        with page.expect_download(timeout=60000) as download_info:
                            download_link.first.click()
                            print("Download started, waiting for completion...")
                        
                        download = download_info.value
                        suggested_filename = download.suggested_filename
                        
                        # Save the zip file
                        final_path = os.path.join(DOWNLOAD_PATH, suggested_filename)
                        download.save_as(final_path)
                        
                        downloaded_files.append(suggested_filename)
                        print(f"✓ Downloaded: {suggested_filename}")
                        print(f"  File size: {os.path.getsize(final_path) / 1024 / 1024:.2f} MB")
                        download_clicked = True
                        break
                        
                except Exception as e:
                    continue
            
            if not download_clicked:
                print("\n✗ Could not find UST Statewide Database Report link!")
                print("Taking screenshot for debugging...")
                
                screenshot_path = os.path.join(STATE_PATH, "kentucky_page_debug.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Screenshot saved to: {screenshot_path}")
                
                # List all links on the page
                print("\nLooking for any links with 'UST', 'Database', or 'Report'...")
                all_links = page.locator('a').all()
                for link in all_links:
                    try:
                        text = link.inner_text().strip()
                        href = link.get_attribute('href') or ''
                        if text and any(keyword in text.lower() for keyword in ['ust', 'database', 'report', 'statewide']):
                            print(f"  Found: '{text}'")
                            print(f"    Href: {href[:100]}...")
                    except:
                        pass
                        
        except Exception as e:
            print(f"Error during download: {e}")
            import traceback
            traceback.print_exc()
        
        browser.close()
        
    return downloaded_files

def extract_zip_file(zip_path):
    """Extract the Kentucky UST zip file"""
    print(f"\nExtracting {os.path.basename(zip_path)}...")
    
    extract_path = os.path.join(INPUT_PATH, "extracted")
    
    # Create extraction directory
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # List contents
            file_list = zip_ref.namelist()
            print(f"Zip file contains {len(file_list)} files:")
            for file in file_list:
                print(f"  - {file}")
            
            # Extract all files
            zip_ref.extractall(extract_path)
            print(f"✓ Extracted to: {extract_path}")
            
            # Look for Excel file
            excel_file = None
            for file in file_list:
                if file.endswith('.xlsx') or file.endswith('.xls'):
                    excel_file = os.path.join(extract_path, file)
                    break
            
            if excel_file and os.path.exists(excel_file):
                print(f"✓ Found Excel file: {excel_file}")
                return excel_file
            else:
                print("✗ Could not find Excel file in the zip")
                return None
                
    except Exception as e:
        print(f"Error extracting zip file: {e}")
        return None

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

def process_kentucky_data(excel_file):
    """Process the Kentucky UST Excel file"""
    print(f"\n=== Starting data processing for {STATE_NAME} ===\n")
    
    if not excel_file or not os.path.exists(excel_file):
        print("No Excel file to process!")
        return
    
    print(f"Processing file: {os.path.basename(excel_file)}")
    
    try:
        # Read Excel file
        print("Reading Excel file...")
        df_raw = pd.read_excel(excel_file)
        
        print(f"File shape: {df_raw.shape}")
        print(f"\nColumns found in source file:")
        for i, col in enumerate(df_raw.columns):
            print(f"  {i+1}. {col}")
        
        # Process each row with Kentucky specific column mappings
        processed_rows = []
        
        for idx, row in df_raw.iterrows():
            processed_row = {}
            
            # State information
            processed_row['state'] = STATE_NAME
            processed_row['state_name'] = STATE_ABBR
            
            # Map Kentucky specific columns
            processed_row['facility_id'] = safe_string(row.get('AI_ID', ''))
            processed_row['tank_id'] = safe_string(row.get('SUBJECT_ITEM_ID', ''))
            processed_row['tank_location'] = safe_string(row.get('ADDRESS_1', ''))
            processed_row['city'] = safe_string(row.get('MAILING_ADDRESS_MUNICIPALITY', ''))
            processed_row['zip'] = safe_string(row.get('MAILING_ADDRESS_ZIP', ''))[:5]
            processed_row['county'] = safe_string(row.get('COUNTY', ''))
            
            # Tank type from AI_TYPE
            ai_type = safe_string(row.get('AI_TYPE', ''))
            if 'ust' in ai_type.lower() or 'underground' in ai_type.lower():
                processed_row['ust_or_ast'] = 'UST'
            elif 'ast' in ai_type.lower() or 'aboveground' in ai_type.lower():
                processed_row['ust_or_ast'] = 'AST'
            else:
                # Default to UST for Kentucky underground storage tanks
                processed_row['ust_or_ast'] = 'UST'
            
            # Installation date
            date_value = row.get('TANK_INSTALL_DATE', '')
            processed_row['year_installed'] = format_date_for_output(date_value)
            processed_row['tank_install_year_only'] = parse_year_from_date(date_value)
            
            # Tank size and range
            tank_size = row.get('CAPACITY_MSR', 0)
            processed_row['tank_size__gallons_'] = safe_int(tank_size)
            processed_row['size_range'] = determine_size_range(tank_size)
            
            # Construction details
            processed_row['tank_construction'] = safe_string(row.get('TANK_MATERIAL_CODE', ''))
            processed_row['piping_construction'] = safe_string(row.get('PIPE_MATERIAL_CODE', ''))
            
            # Tank construction rating - could use manufacturer codes
            tank_manufctr = safe_string(row.get('TANK_MANUFCTR_CODE', ''))
            pipe_manufctr = safe_string(row.get('PIPE_MANUFCTR_CODE', ''))
            processed_row['tank_construction_rating'] = tank_manufctr
            
            # Secondary containment - check spill/overfill prevention
            spill_prevent = safe_string(row.get('TANK_SPILL_PREVENT_CODE', ''))
            overfill_prevent = safe_string(row.get('TANK_OVERFILL_PREVENT_CODE', ''))
            if spill_prevent or overfill_prevent:
                processed_row['secondary_containment__ast_'] = 'Yes'
            else:
                processed_row['secondary_containment__ast_'] = ''
            
            # Content/Product
            processed_row['content_description'] = safe_string(row.get('TANK_SUBSTANCE_CODE', ''))
            
            # Tank tightness - check test dates
            last_tank_test = safe_string(row.get('LAST_TANK_TEST_DATE', ''))
            last_line_test = safe_string(row.get('LAST_LINE_TEST_DATE', ''))
            if last_tank_test or last_line_test:
                processed_row['tank_tightness'] = 'Yes'
            else:
                processed_row['tank_tightness'] = ''
            
            # Facility name - use AI_NAME or OWNER_NAME
            facility_name = safe_string(row.get('AI_NAME', ''))
            owner_name = safe_string(row.get('OWNER_NAME', ''))
            processed_row['facility_name'] = facility_name if facility_name else owner_name
            
            # Tank status
            tank_status = safe_string(row.get('TANK_STATUS_CODE', ''))
            
            # Check for closure/removal dates
            temp_close = safe_string(row.get('TEMP_CLOSE_DATE', ''))
            closed_in_place = safe_string(row.get('CLOSED_IN_PLACE_DATE', ''))
            removal_date = safe_string(row.get('REMOVAL_DATE', ''))
            
            if removal_date:
                tank_status = f'Removed {removal_date}'
            elif closed_in_place:
                tank_status = f'Closed in Place {closed_in_place}'
            elif temp_close:
                tank_status = f'Temporarily Closed {temp_close}'
                
            processed_row['tank_status'] = tank_status
            
            # LUST information - not directly in Kentucky data
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
        print(formatted_df[['facility_id', 'tank_id', 'facility_name', 'city', 'county', 'tank_status']].head(3).to_string())
        
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
        
        # Check general LUST file
        lust_file = os.path.join(BASE_PATH, "L-UST_Data", "LustDataAllStates.xlsx")
        
        if not os.path.exists(lust_file):
            print(f"Warning: LUST data file not found at {lust_file}")
            final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
            formatted_df.to_excel(final_output, index=False)
            return formatted_df
            
        LustData = pd.read_excel(lust_file)
        KY_Lust = LustData[LustData['State Name'] == STATE_NAME]
        
        if len(KY_Lust) == 0:
            print(f"No LUST records found for {STATE_NAME}")
            final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
            formatted_df.to_excel(final_output, index=False)
            return formatted_df
        
        print(f'Found {len(KY_Lust)} LUST records for {STATE_NAME} in general file')
        
        # Save Kentucky LUST data
        ky_lust_file = os.path.join(REQUIRED_PATH, f'{STATE_NAME}LustData.xlsx')
        KY_Lust.to_excel(ky_lust_file, index=False)
        
        # Create location matching key
        if 'Address' in KY_Lust.columns and 'City' in KY_Lust.columns:
            KY_Lust['location_city'] = (KY_Lust['Address'].astype(str).str.strip() + '_' + 
                                        KY_Lust['City'].astype(str).str.strip()).str.upper()
            
            formatted_df['location_city'] = (formatted_df['tank_location'].astype(str) + '_' + 
                                            formatted_df['city'].astype(str)).str.upper()
            
            # Remove duplicates from LUST data
            KY_Lust_unique = KY_Lust.drop_duplicates(subset='location_city', keep='first')
            
            # Merge to find matches
            merged = formatted_df.merge(KY_Lust_unique[['location_city', 'Status']], 
                                      on='location_city', how='left')
            
            # Update lust and lust_status where matches found
            matches = merged['Status'].notna()
            formatted_df.loc[matches, 'lust'] = 'Yes'
            formatted_df.loc[matches, 'lust_status'] = merged.loc[matches, 'Status']
            
            # For non-matches, set to 'No'
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
        print(f"Total counties: {formatted_df['county'].nunique()}")
        print(f"UST tanks: {(formatted_df['ust_or_ast'] == 'UST').sum()}")
        print(f"AST tanks: {(formatted_df['ust_or_ast'] == 'AST').sum()}")
        print(f"LUST sites: {(formatted_df['lust'] == 'Yes').sum()}")
        
        # Show county breakdown
        print(f"\nTop 10 counties by tank count:")
        county_counts = formatted_df['county'].value_counts().head(10)
        for county, count in county_counts.items():
            print(f"  {county}: {count}")
        
        return formatted_df
        
    except Exception as e:
        print(f"Error processing LUST data: {e}")
        final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
        formatted_df.to_excel(final_output, index=False)
        return formatted_df

def main():
    """Main function to orchestrate the entire process"""
    print(f"{'='*60}")
    print(f"Starting {STATE_NAME} UST Database Download and Processing")
    print(f"{'='*60}")
    print(f"Base path: {BASE_PATH}")
    print(f"Target URL: {URL}")
    
    # Setup folder structure
    log_file = setup_folder_structure()
    print(f"Log file: {log_file}")
    
    # Optional: Clear input folder
    clear_input_folder()
    
    # Download files
    print(f"\n=== Downloading UST database for {STATE_NAME} ===\n")
    print("Looking for 'UST Statewide Database Report' under 'Documents of Interest'...")
    
    downloaded_files = download_kentucky_data()
    
    if not downloaded_files:
        print("\n✗ No files were downloaded.")
        print("Please check:")
        print("1. The website is accessible")
        print("2. The 'Documents of Interest' section exists")
        print("3. The 'UST Statewide Database Report' link is available")
        print("4. The screenshots in the state folder for debugging")
        return
    
    print(f"\n✓ Successfully downloaded {len(downloaded_files)} file(s)")
    
    # Extract zip file
    zip_file = None
    for file in downloaded_files:
        if file.endswith('.zip'):
            zip_file = os.path.join(DOWNLOAD_PATH, file)
            break
    
    if not zip_file:
        print("No zip file found!")
        return
    
    # Extract and find Excel file
    excel_file = extract_zip_file(zip_file)
    
    if not excel_file:
        print("Could not find or extract Excel file!")
        return
    
    # Process the data
    process_kentucky_data(excel_file)
    
    print(f"\n{'='*60}")
    print(f'{STATE_NAME} processing completed!')
    print(f"{'='*60}")

if __name__ == "__main__":
    main()