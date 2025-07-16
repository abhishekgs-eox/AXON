from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime
import numpy as np

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Georgia"
STATE_ABBR = "GA"
URL = "https://epd.georgia.gov/ust-data-and-reporting"

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

def download_georgia_data():
    """Download Georgia UST data using Playwright"""
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
            print("Looking for 'Data for All Georgia Counties' link...")
            
            # Try different selectors for the download link
            download_selectors = [
                'a:has-text("Data for All Georgia Counties")',
                'text="Data for All Georgia Counties"',
                '//a[contains(text(), "Data for All Georgia Counties")]',
                'a:has-text("All Georgia Counties")',
                '//a[contains(text(), "All Georgia Counties")]',
                'a[href*="counties"]',
                'a[href*=".csv"]',
                '.content a:has-text("Counties")'
            ]
            
            download_found = False
            
            for selector in download_selectors:
                try:
                    if selector.startswith('//'):
                        locator = page.locator(f'xpath={selector}')
                    else:
                        locator = page.locator(selector)
                    
                    if locator.count() > 0:
                        print(f"✓ Found download link using selector: {selector}")
                        
                        # Scroll to element to ensure it's visible
                        locator.first.scroll_into_view_if_needed()
                        time.sleep(1)
                        
                        # Check if it's a direct download link
                        href = locator.first.get_attribute('href')
                        if href:
                            print(f"Link URL: {href[:100]}...")
                        
                        # Wait for download
                        with page.expect_download(timeout=30000) as download_info:
                            locator.first.click()
                            print("Clicked download link, waiting for file...")
                        
                        download = download_info.value
                        suggested_filename = download.suggested_filename
                        
                        # Save to our download directory
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
                print("\n✗ Could not find the 'Data for All Georgia Counties' link!")
                print("Taking screenshot for debugging...")
                
                screenshot_path = os.path.join(STATE_PATH, "georgia_page_debug.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Screenshot saved to: {screenshot_path}")
                
                # List all links on the page for debugging
                print("\n=== All links found on page ===")
                links = page.locator('a').all()
                for i, link in enumerate(links[:30]):  # Show first 30 links
                    try:
                        text = link.inner_text().strip()
                        href = link.get_attribute('href') or ''
                        if text and ('data' in text.lower() or 'counties' in text.lower() or 'georgia' in text.lower() or 'csv' in text.lower()):
                            print(f"\n{i+1}. Text: '{text}'")
                            print(f"   Href: {href[:100]}...")
                    except:
                        pass
                        
        except Exception as e:
            print(f"Error during download: {e}")
            
            # Try to capture any error dialogs
            try:
                page.screenshot(path=os.path.join(STATE_PATH, "error_screenshot.png"))
            except:
                pass
        
        # Close browser
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

def process_georgia_data():
    """Process the downloaded Georgia data with exact formatting"""
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
        
        # Process each row with Georgia specific column mappings
        processed_rows = []
        
        for idx, row in df_raw.iterrows():
            processed_row = {}
            
            # State information
            processed_row['state'] = STATE_NAME
            processed_row['state_name'] = STATE_ABBR
            
            # Map Georgia specific columns
            processed_row['facility_id'] = safe_string(row.get('Facility ID', ''))
            processed_row['tank_id'] = safe_string(row.get('UST Legacy Tank No.', ''))
            processed_row['tank_location'] = safe_string(row.get('Facility Street Address', ''))
            processed_row['city'] = safe_string(row.get('Facility City', ''))
            processed_row['zip'] = ''  # Not in Georgia data
            processed_row['county'] = safe_string(row.get('County', ''))
            
            # Tank type - All UST for Georgia underground storage tanks
            processed_row['ust_or_ast'] = 'UST'
            
            # Installation date
            date_value = row.get('Tank Installation Date', '')
            processed_row['year_installed'] = format_date_for_output(date_value)
            processed_row['tank_install_year_only'] = parse_year_from_date(date_value)
            
            # Tank size and range
            tank_size = row.get('Tank Capacity', 0)
            processed_row['tank_size__gallons_'] = safe_int(tank_size)
            processed_row['size_range'] = determine_size_range(tank_size)
            
            # Construction details
            processed_row['tank_construction'] = safe_string(row.get('Construction Description', ''))
            processed_row['piping_construction'] = safe_string(row.get('Pipe Type Name', ''))
            
            # Tank construction rating - use Pipe Description if available
            processed_row['tank_construction_rating'] = safe_string(row.get('Pipe Description', ''))
            
            # Secondary containment - Check overfill/spill protection
            overfill_type = safe_string(row.get('Tank Overfill type', ''))
            overfill_exempt = safe_string(row.get('Tank OverfillExempt', ''))
            spill_exempt = safe_string(row.get('Tank SpillExempt', ''))
            
            # If has overfill type and not exempt, consider it has secondary containment
            if overfill_type and overfill_exempt.lower() != 'yes' and spill_exempt.lower() != 'yes':
                processed_row['secondary_containment__ast_'] = 'Yes'
            else:
                processed_row['secondary_containment__ast_'] = ''
            
            # Content/Product
            processed_row['content_description'] = safe_string(row.get('Content Description', ''))
            
            # Tank tightness - not directly in Georgia data
            processed_row['tank_tightness'] = ''
            
            # Facility name
            processed_row['facility_name'] = safe_string(row.get('Facility Name', ''))
            
            # Tank status
            processed_row['tank_status'] = safe_string(row.get('Tank Status', ''))
            
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
        lust_file = os.path.join(BASE_PATH, "L-UST_Data", "LustDataAllStates.xlsx")
        
        if not os.path.exists(lust_file):
            print(f"Warning: LUST data file not found at {lust_file}")
            final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
            formatted_df.to_excel(final_output, index=False)
            return formatted_df
            
        LustData = pd.read_excel(lust_file)
        GA_Lust = LustData[LustData['State Name'] == STATE_NAME]
        
        if len(GA_Lust) == 0:
            print(f"No LUST records found for {STATE_NAME}")
            final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
            formatted_df.to_excel(final_output, index=False)
            return formatted_df
        
        print(f'Found {len(GA_Lust)} LUST records for {STATE_NAME}')
        
        # Save Georgia LUST data
        ga_lust_file = os.path.join(REQUIRED_PATH, f'{STATE_NAME}LustData.xlsx')
        GA_Lust.to_excel(ga_lust_file, index=False)
        
        # Create location matching key
        if 'Address' in GA_Lust.columns and 'City' in GA_Lust.columns:
            GA_Lust['location_city'] = (GA_Lust['Address'].astype(str).str.strip() + '_' + 
                                        GA_Lust['City'].astype(str).str.strip()).str.upper()
            
            formatted_df['location_city'] = (formatted_df['tank_location'].astype(str) + '_' + 
                                            formatted_df['city'].astype(str)).str.upper()
            
            # Remove duplicates from LUST data
            GA_Lust_unique = GA_Lust.drop_duplicates(subset='location_city', keep='first')
            
            # Merge to find matches
            merged = formatted_df.merge(GA_Lust_unique[['location_city', 'Status']], 
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
        print(f"Total counties: {formatted_df['county'].nunique()}")
        print(f"Active tanks: {(formatted_df['tank_status'].str.lower().str.contains('active', na=False)).sum()}")
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
    downloaded_files = download_georgia_data()
    
    if downloaded_files:
        print(f"\n✓ Successfully downloaded {len(downloaded_files)} file(s):")
        for file in downloaded_files:
            print(f"  - {file}")
    else:
        print("\n✗ No files were downloaded.")
        print("Please check:")
        print("1. The website is accessible")
        print("2. The 'Data for All Georgia Counties' link is visible")
        print("3. The screenshots in the state folder for debugging")
        return
    
    # Wait for files to be completely written
    time.sleep(3)
    
    # Process the data
    process_georgia_data()
    
    print(f"\n{'='*60}")
    print(f'{STATE_NAME} processing completed!')
    print(f"{'='*60}")

if __name__ == "__main__":
    main()