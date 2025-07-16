from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime
import numpy as np

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output\"
STATE_NAME = "Illinois"
STATE_ABBR = "IL"
URL = "https://webapps.sfm.illinois.gov/ustsearch/"
# need to take data from EPA

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

def download_illinois_data():
    """Download Illinois UST data using Playwright"""
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
            print("Looking for Search button...")
            
            # Find and click the Search button
            search_selectors = [
                'button:has-text("Search")',
                'input[type="submit"][value="Search"]',
                'button[type="submit"]:has-text("Search")',
                '#search-button',
                '.btn:has-text("Search")',
                '//button[contains(text(), "Search")]',
                '//input[@value="Search"]'
            ]
            
            search_clicked = False
            
            for selector in search_selectors:
                try:
                    if selector.startswith('//'):
                        search_btn = page.locator(f'xpath={selector}')
                    else:
                        search_btn = page.locator(selector)
                    
                    if search_btn.count() > 0:
                        print("✓ Found Search button")
                        search_btn.first.click()
                        search_clicked = True
                        print("Clicked Search, waiting for results...")
                        break
                except:
                    continue
            
            if not search_clicked:
                print("Could not find Search button, taking screenshot...")
                screenshot_path = os.path.join(STATE_PATH, "illinois_search_debug.png")
                page.screenshot(path=screenshot_path)
                print(f"Screenshot saved to: {screenshot_path}")
                return downloaded_files
            
            # Wait for results to start loading
            print("Waiting for search results to load...")
            time.sleep(5)
            
            # Wait for network to settle
            try:
                page.wait_for_load_state('networkidle', timeout=60000)
            except:
                print("Network timeout, but continuing...")
            
            # Additional wait for large datasets
            print("Waiting for all data to load (this may take a while for large datasets)...")
            time.sleep(10)
            
            # Check if results are loading by looking for common indicators
            loading_complete = False
            max_wait = 60  # Maximum 60 seconds
            wait_count = 0
            
            while not loading_complete and wait_count < max_wait:
                try:
                    # Look for "Search Results" text
                    results_text = page.locator('text=/Search Results.*matches found/i')
                    if results_text.count() > 0:
                        result_text = results_text.first.inner_text()
                        print(f"✓ Found: {result_text}")
                        loading_complete = True
                        break
                    
                    # Also check for table rows as indicator
                    rows = page.locator('tr')
                    if rows.count() > 10:  # Assuming more than 10 rows means data loaded
                        print(f"Found {rows.count()} table rows")
                        loading_complete = True
                        break
                    
                except:
                    pass
                
                time.sleep(2)
                wait_count += 2
                print(f"Still waiting... ({wait_count}s)")
            
            # Scroll to bottom of page to find Export button
            print("\nScrolling to bottom of page...")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            
            # Try to find the Search Results text first
            print("Looking for Search Results text...")
            results_found = False
            
            try:
                # Look for "Search Results - X matches found" pattern
                results_locators = [
                    'text=/Search Results.*matches found/i',
                    'text=/Search Results/i',
                    '//*[contains(text(), "Search Results")]',
                    '//*[contains(text(), "matches found")]'
                ]
                
                for locator in results_locators:
                    try:
                        if locator.startswith('//'):
                            results_elem = page.locator(f'xpath={locator}')
                        else:
                            results_elem = page.locator(locator)
                        
                        if results_elem.count() > 0:
                            results_text = results_elem.first.inner_text()
                            print(f"✓ Found results text: {results_text}")
                            results_found = True
                            
                            # Scroll this element into view
                            results_elem.first.scroll_into_view_if_needed()
                            time.sleep(1)
                            break
                    except:
                        continue
            except:
                print("Could not find Search Results text")
            
            # Now look for Export to Excel button near the bottom
            print("\nLooking for Export to Excel button at bottom of page...")
            
            # First try to find it near the Search Results text
            export_clicked = False
            
            if results_found:
                # Look for Export button near the results text
                try:
                    # Get the parent element and look for Export button within it
                    export_near_results = page.locator('text=/Export.*Excel/i').last
                    if export_near_results.count() > 0:
                        print("✓ Found Export to Excel button near results")
                        
                        # Scroll to it
                        export_near_results.scroll_into_view_if_needed()
                        time.sleep(1)
                        
                        # Click and wait for download
                        with page.expect_download(timeout=30000) as download_info:
                            export_near_results.click()
                            print("Clicked Export to Excel, waiting for download...")
                        
                        download = download_info.value
                        suggested_filename = download.suggested_filename
                        
                        # Save with state prefix
                        final_filename = f"{STATE_NAME}_UST_Export.xlsx"
                        final_path = os.path.join(DOWNLOAD_PATH, final_filename)
                        download.save_as(final_path)
                        
                        downloaded_files.append(final_filename)
                        print(f"✓ Downloaded: {final_filename}")
                        print(f"  File size: {os.path.getsize(final_path) / 1024 / 1024:.2f} MB")
                        export_clicked = True
                except:
                    pass
            
            # If not found near results, try general search at bottom
            if not export_clicked:
                export_selectors = [
                    'button:has-text("Export to Excel")',
                    'a:has-text("Export to Excel")',
                    'input[value="Export to Excel"]',
                    '//button[contains(text(), "Export to Excel")]',
                    '//a[contains(text(), "Export to Excel")]',
                    'text="Export to Excel"'
                ]
                
                # Get all matching elements and take the last one (bottom of page)
                for selector in export_selectors:
                    try:
                        if selector.startswith('//'):
                            export_btns = page.locator(f'xpath={selector}').all()
                        else:
                            export_btns = page.locator(selector).all()
                        
                        if export_btns:
                            # Take the last one (should be at bottom)
                            export_btn = export_btns[-1]
                            print(f"✓ Found Export to Excel button (using last occurrence)")
                            
                            # Scroll to element
                            export_btn.scroll_into_view_if_needed()
                            time.sleep(1)
                            
                            # Click and wait for download
                            with page.expect_download(timeout=30000) as download_info:
                                export_btn.click()
                                print("Clicked Export to Excel, waiting for download...")
                            
                            download = download_info.value
                            suggested_filename = download.suggested_filename
                            
                            # Save with state prefix
                            final_filename = f"{STATE_NAME}_UST_Export.xlsx"
                            final_path = os.path.join(DOWNLOAD_PATH, final_filename)
                            download.save_as(final_path)
                            
                            downloaded_files.append(final_filename)
                            print(f"✓ Downloaded: {final_filename}")
                            print(f"  File size: {os.path.getsize(final_path) / 1024 / 1024:.2f} MB")
                            export_clicked = True
                            break
                    except Exception as e:
                        continue
            
            if not export_clicked:
                print("\nCould not find Export to Excel button")
                print("Taking full page screenshot...")
                screenshot_path = os.path.join(STATE_PATH, "illinois_full_page_debug.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Screenshot saved to: {screenshot_path}")
                
                # Also take screenshot of bottom of page
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)
                screenshot_bottom = os.path.join(STATE_PATH, "illinois_bottom_debug.png")
                page.screenshot(path=screenshot_bottom)
                print(f"Bottom screenshot saved to: {screenshot_bottom}")
                
                # List all buttons/links at the bottom
                print("\nLooking for any Export/Excel related elements...")
                all_elements = page.locator('button, a, input[type="button"], input[type="submit"]').all()
                
                # Get last 20 elements (bottom of page)
                for elem in all_elements[-20:]:
                    try:
                        text = elem.inner_text() or elem.get_attribute('value') or ''
                        if text and ('export' in text.lower() or 'excel' in text.lower()):
                            print(f"  Found: '{text}'")
                    except:
                        pass
                        
        except Exception as e:
            print(f"Error during download: {e}")
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

def process_illinois_data():
    """Process the downloaded Illinois data with exact formatting"""
    print(f"\n=== Starting data processing for {STATE_NAME} ===\n")
    
    # Find the downloaded file
    downloaded_file = None
    for file in os.listdir(INPUT_PATH):
        if file.endswith('.xlsx') or file.endswith('.xls'):
            if STATE_NAME in file:
                downloaded_file = file
                break
    
    if not downloaded_file:
        print("No Excel file found in Input folder!")
        return
    
    print(f"Processing file: {downloaded_file}")
    
    try:
        file_path = os.path.join(INPUT_PATH, downloaded_file)
        
        # Read Excel file
        print("Reading Excel file...")
        df_raw = pd.read_excel(file_path)
        
        print(f"File shape: {df_raw.shape}")
        print(f"\nColumns found in source file:")
        for i, col in enumerate(df_raw.columns):
            print(f"  {i+1}. {col}")
        
        # Process each row with Illinois specific column mappings
        processed_rows = []
        
        for idx, row in df_raw.iterrows():
            processed_row = {}
            
            # State information
            processed_row['state'] = STATE_NAME
            processed_row['state_name'] = STATE_ABBR
            
            # Map Illinois specific columns
            processed_row['facility_id'] = safe_string(row.get('Facility ID', ''))
            processed_row['tank_id'] = safe_string(row.get('Tank ID', ''))
            processed_row['tank_location'] = safe_string(row.get('Address', ''))
            processed_row['city'] = safe_string(row.get('City', ''))
            processed_row['zip'] = safe_string(row.get('Zip', ''))[:5]
            processed_row['county'] = safe_string(row.get('County', ''))
            
            # Tank type - from Facility Type
            facility_type = safe_string(row.get('Facility Type', ''))
            if 'underground' in facility_type.lower() or 'ust' in facility_type.lower():
                processed_row['ust_or_ast'] = 'UST'
            elif 'aboveground' in facility_type.lower() or 'ast' in facility_type.lower():
                processed_row['ust_or_ast'] = 'AST'
            else:
                # Default to UST for Illinois underground storage tanks
                processed_row['ust_or_ast'] = 'UST'
            
            # Installation date
            date_value = row.get('Date Installed', '')
            processed_row['year_installed'] = format_date_for_output(date_value)
            processed_row['tank_install_year_only'] = parse_year_from_date(date_value)
            
            # Tank size and range
            tank_size = row.get('Tank Capacity', 0)
            processed_row['tank_size__gallons_'] = safe_int(tank_size)
            processed_row['size_range'] = determine_size_range(tank_size)
            
            # Construction details - not directly in Illinois data
            processed_row['tank_construction'] = ''
            processed_row['piping_construction'] = ''
            processed_row['tank_construction_rating'] = ''
            
            # Secondary containment - not directly in Illinois data
            processed_row['secondary_containment__ast_'] = ''
            
            # Content/Product
            processed_row['content_description'] = safe_string(row.get('Product', ''))
            
            # Tank tightness - not in Illinois data
            processed_row['tank_tightness'] = ''
            
            # Facility name
            processed_row['facility_name'] = safe_string(row.get('Facility Name', ''))
            
            # Tank status
            tank_status = safe_string(row.get('Tank Status', ''))
            facility_status = safe_string(row.get('Facility Status', ''))
            
            # Use tank status if available, otherwise use facility status
            if tank_status:
                processed_row['tank_status'] = tank_status
            elif facility_status:
                processed_row['tank_status'] = facility_status
            else:
                processed_row['tank_status'] = ''
            
            # LUST information - check for red tag or other indicators
            red_tag_date = safe_string(row.get('Red Tag Issue Date', ''))
            if red_tag_date:
                processed_row['lust'] = 'Yes'
                processed_row['lust_status'] = f'Red Tag: {red_tag_date}'
            else:
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
        
        # Note: Illinois data includes Red Tag information which indicates LUST
        red_tag_count = (formatted_df['lust'] == 'Yes').sum()
        print(f"Found {red_tag_count} tanks with Red Tag (potential LUST) in Illinois data")
        
        # Also check general LUST file
        lust_file = os.path.join(BASE_PATH, "L-UST_Data", "LustDataAllStates.xlsx")
        
        if not os.path.exists(lust_file):
            print(f"Warning: LUST data file not found at {lust_file}")
            final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
            formatted_df.to_excel(final_output, index=False)
            return formatted_df
            
        LustData = pd.read_excel(lust_file)
        IL_Lust = LustData[LustData['State Name'] == STATE_NAME]
        
        if len(IL_Lust) == 0:
            print(f"No additional LUST records found for {STATE_NAME}")
            final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
            formatted_df.to_excel(final_output, index=False)
            return formatted_df
        
        print(f'Found {len(IL_Lust)} LUST records for {STATE_NAME} in general file')
        
        # Save Illinois LUST data
        il_lust_file = os.path.join(REQUIRED_PATH, f'{STATE_NAME}LustData.xlsx')
        IL_Lust.to_excel(il_lust_file, index=False)
        
        # Create location matching key
        if 'Address' in IL_Lust.columns and 'City' in IL_Lust.columns:
            IL_Lust['location_city'] = (IL_Lust['Address'].astype(str).str.strip() + '_' + 
                                        IL_Lust['City'].astype(str).str.strip()).str.upper()
            
            formatted_df['location_city'] = (formatted_df['tank_location'].astype(str) + '_' + 
                                            formatted_df['city'].astype(str)).str.upper()
            
            # Remove duplicates from LUST data
            IL_Lust_unique = IL_Lust.drop_duplicates(subset='location_city', keep='first')
            
            # Merge to find matches
            merged = formatted_df.merge(IL_Lust_unique[['location_city', 'Status']], 
                                      on='location_city', how='left')
            
            # Update lust and lust_status where matches found (only if not already marked)
            matches = merged['Status'].notna()
            no_existing_lust = formatted_df['lust'] != 'Yes'
            update_mask = matches & no_existing_lust
            
            formatted_df.loc[update_mask, 'lust'] = 'Yes'
            formatted_df.loc[update_mask, 'lust_status'] = merged.loc[update_mask, 'Status']
            
            # For non-matches that don't have Red Tag, set to 'No'
            no_matches = ~matches
            no_red_tag = formatted_df['lust'] != 'Yes'
            formatted_df.loc[no_matches & no_red_tag, 'lust'] = 'No'
            
            # Remove temporary column
            formatted_df = formatted_df.drop('location_city', axis=1)
            
            print(f'Updated {update_mask.sum()} additional records with LUST information')
        
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
        print(f"LUST sites (total): {(formatted_df['lust'] == 'Yes').sum()}")
        print(f"  - Red Tag sites: {red_tag_count}")
        print(f"  - Other LUST sites: {(formatted_df['lust'] == 'Yes').sum() - red_tag_count}")
        
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
    print("Process:")
    print("1. Click Search button")
    print("2. Wait for ALL results to load (may take time)")
    print("3. Scroll to bottom of page")
    print("4. Find 'Search Results - X matches found'")
    print("5. Click Export to Excel below that")
    
    downloaded_files = download_illinois_data()
    
    if downloaded_files:
        print(f"\n✓ Successfully downloaded {len(downloaded_files)} file(s):")
        for file in downloaded_files:
            print(f"  - {file}")
    else:
        print("\n✗ No files were downloaded.")
        print("Please check:")
        print("1. The website is accessible")
        print("2. The Search button is clickable")
        print("3. Results are loading completely")
        print("4. The Export to Excel option is at the bottom of the page")
        print("5. The screenshots in the state folder for debugging")
        return
    
    # Wait for files to be completely written
    time.sleep(3)
    
    # Process the data
    process_illinois_data()
    
    print(f"\n{'='*60}")
    print(f'{STATE_NAME} processing completed!')
    print(f"{'='*60}")

if __name__ == "__main__":
    main()