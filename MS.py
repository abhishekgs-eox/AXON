from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime
import numpy as np

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Mississippi"
STATE_ABBR = "MS"
URL = "https://www.mdeq.ms.gov/water/groundwater-assessment-and-remediation/underground-storage-tanks/musterweb/"

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

def download_mississippi_data():
    """Download UST and LUST data files from Mississippi MDEQ website"""
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
            page.goto(URL, wait_until='networkidle', timeout=60000)
            page.wait_for_load_state('domcontentloaded')
            time.sleep(5)
            
            # Download UST Facilities & Owners Information
            print("\nLooking for UST Facilities & Owners Information link...")
            ust_link_selectors = [
                'a:has-text("UST Facilities & Owners Information")',
                'a:has-text("UST Facilities")',
                '//a[contains(text(), "UST Facilities")]',
                'a[href*="csv"][href*="UST"]',
                'a[href*="facilities"]'
            ]
            
            ust_downloaded = False
            for selector in ust_link_selectors:
                try:
                    if selector.startswith('//'):
                        link = page.locator(f'xpath={selector}')
                    else:
                        link = page.locator(selector)
                    
                    if link.count() > 0:
                        print("✓ Found UST Facilities link")
                        
                        # Prepare for download
                        with page.expect_download(timeout=60000) as download_info:
                            link.first.click()
                            print("  Clicked UST link, waiting for download...")
                        
                        download = download_info.value
                        ust_filename = f"{STATE_NAME}_UST_Facilities.csv"
                        ust_path = os.path.join(DOWNLOAD_PATH, ust_filename)
                        download.save_as(ust_path)
                        
                        downloaded_files.append(ust_filename)
                        print(f"  ✓ Downloaded: {ust_filename}")
                        ust_downloaded = True
                        break
                except Exception as e:
                    continue
            
            if not ust_downloaded:
                print("  ✗ Could not download UST Facilities file")
                # Take screenshot for debugging
                screenshot_path = os.path.join(STATE_PATH, "mississippi_ust_debug.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"  Screenshot saved to: {screenshot_path}")
            
            time.sleep(3)
            
            # Download Leaking UST (LUST) Information
            print("\nLooking for Leaking UST (LUST) Information link...")
            lust_link_selectors = [
                'a:has-text("Leaking UST (LUST) Information")',
                'a:has-text("Leaking UST")',
                'a:has-text("LUST Information")',
                '//a[contains(text(), "Leaking UST")]',
                '//a[contains(text(), "LUST")]',
                'a[href*="csv"][href*="LUST"]',
                'a[href*="leaking"]'
            ]
            
            lust_downloaded = False
            for selector in lust_link_selectors:
                try:
                    if selector.startswith('//'):
                        link = page.locator(f'xpath={selector}')
                    else:
                        link = page.locator(selector)
                    
                    if link.count() > 0:
                        print("✓ Found LUST Information link")
                        
                        # Prepare for download
                        with page.expect_download(timeout=60000) as download_info:
                            link.first.click()
                            print("  Clicked LUST link, waiting for download...")
                        
                        download = download_info.value
                        lust_filename = f"{STATE_NAME}_LUST_Information.csv"
                        lust_path = os.path.join(DOWNLOAD_PATH, lust_filename)
                        download.save_as(lust_path)
                        
                        downloaded_files.append(lust_filename)
                        print(f"  ✓ Downloaded: {lust_filename}")
                        lust_downloaded = True
                        break
                except Exception as e:
                    continue
            
            if not lust_downloaded:
                print("  ✗ Could not download LUST Information file")
                # Take screenshot for debugging
                screenshot_path = os.path.join(STATE_PATH, "mississippi_lust_debug.png")
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

def process_mississippi_ust_data():
    """Process Mississippi UST Facilities data"""
    ust_file = os.path.join(INPUT_PATH, f"{STATE_NAME}_UST_Facilities.csv")
    
    if not os.path.exists(ust_file):
        print(f"UST file not found: {ust_file}")
        return pd.DataFrame()
    
    # Try different encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']
    df_raw = None
    
    for encoding in encodings:
        try:
            df_raw = pd.read_csv(ust_file, encoding=encoding, low_memory=False)
            print(f"Successfully read UST file with encoding: {encoding}")
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error with encoding {encoding}: {e}")
            continue
    
    if df_raw is None:
        print("Could not read UST file with any encoding. Trying with error handling...")
        try:
            df_raw = pd.read_csv(ust_file, encoding='latin-1', low_memory=False, on_bad_lines='skip')
        except:
            print("Failed to read UST file even with error handling")
            return pd.DataFrame()
    
    try:
        print(f"Loaded UST data: {len(df_raw)} records")
        print(f"Columns found: {list(df_raw.columns)[:10]}...")  # Show first 10 columns for debugging
        
        processed_rows = []
        
        for idx, row in df_raw.iterrows():
            processed_row = {}
            
            # State information
            processed_row['state'] = STATE_NAME
            processed_row['state_name'] = STATE_ABBR
            
            # Map Mississippi specific columns
            processed_row['facility_id'] = safe_string(row.get('FACILITY_ID', ''))
            processed_row['tank_id'] = safe_string(row.get('TANK_INDEX', ''))
            processed_row['tank_location'] = safe_string(row.get('LocAddr', ''))
            processed_row['city'] = safe_string(row.get('LocCity', ''))
            processed_row['zip'] = safe_string(row.get('LocZip', ''))[:5]
            processed_row['county'] = safe_string(row.get('County', ''))
            
            # Tank type - check TankTypes field
            tank_type = safe_string(row.get('TankTypes', ''))
            if 'underground' in tank_type.lower() or 'ust' in tank_type.lower():
                processed_row['ust_or_ast'] = 'UST'
            elif 'aboveground' in tank_type.lower() or 'ast' in tank_type.lower():
                processed_row['ust_or_ast'] = 'AST'
            else:
                processed_row['ust_or_ast'] = 'UST'  # Default to UST
            
            # Installation date
            date_value = row.get('DATEINSTALLEDTANK', '')
            processed_row['year_installed'] = format_date_for_output(date_value)
            processed_row['tank_install_year_only'] = parse_year_from_date(date_value)
            
            # Tank size and range
            tank_size = row.get('TANK_CAPACITY', 0)
            processed_row['tank_size__gallons_'] = safe_int(tank_size)
            processed_row['size_range'] = determine_size_range(tank_size)
            
            # Construction details
            processed_row['tank_construction'] = safe_string(row.get('TankMatDesc', ''))
            processed_row['piping_construction'] = safe_string(row.get('pipeMatDesc', ''))
            
            # Tank construction rating based on material
            tank_mat = safe_string(row.get('TankMatDesc', '')).lower()
            if 'fiberglass' in tank_mat or 'frp' in tank_mat:
                processed_row['tank_construction_rating'] = 'A'
            elif 'steel' in tank_mat and ('coated' in tank_mat or 'protected' in tank_mat):
                processed_row['tank_construction_rating'] = 'B'
            elif 'steel' in tank_mat:
                processed_row['tank_construction_rating'] = 'C'
            else:
                processed_row['tank_construction_rating'] = ''
            
            # Secondary containment
            overfill = safe_string(row.get('OverfillPrevention', ''))
            spill = safe_string(row.get('SpillPrevention', ''))
            if overfill.lower() == 'y' or spill.lower() == 'y':
                processed_row['secondary_containment__ast_'] = 'Yes'
            else:
                processed_row['secondary_containment__ast_'] = ''
            
            # Content/Product
            processed_row['content_description'] = safe_string(row.get('TankSubstance', ''))
            
            # Tank tightness - check for leak detection
            tank_ld = safe_string(row.get('TankLD', ''))
            pipe_ld = safe_string(row.get('pipeLD', ''))
            if tank_ld.lower() == 'y' or pipe_ld.lower() == 'y':
                processed_row['tank_tightness'] = 'Yes'
            else:
                processed_row['tank_tightness'] = ''
            
            # Facility name
            processed_row['facility_name'] = safe_string(row.get('FacName', ''))
            
            # Tank status
            processed_row['tank_status'] = safe_string(row.get('TankStatus', ''))
            
            # LUST information - will be updated later
            processed_row['lust'] = ''
            processed_row['lust_status'] = ''
            
            # Last synch date
            processed_row['last_synch_date'] = datetime.now().strftime('%Y/%m/%d')
            
            processed_rows.append(processed_row)
        
        return pd.DataFrame(processed_rows)
        
    except Exception as e:
        print(f"Error processing UST file: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()
    
def process_mississippi_lust_data():
    """Process Mississippi LUST Information data"""
    lust_file = os.path.join(INPUT_PATH, f"{STATE_NAME}_LUST_Information.csv")
    
    if not os.path.exists(lust_file):
        print(f"LUST file not found: {lust_file}")
        return None
    
    # Try different encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']
    lust_df = None
    
    for encoding in encodings:
        try:
            lust_df = pd.read_csv(lust_file, encoding=encoding, low_memory=False)
            print(f"Successfully read LUST file with encoding: {encoding}")
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error with encoding {encoding}: {e}")
            continue
    
    if lust_df is None:
        print("Could not read LUST file with any encoding. Trying with error handling...")
        try:
            lust_df = pd.read_csv(lust_file, encoding='latin-1', low_memory=False, on_bad_lines='skip')
        except:
            print("Failed to read LUST file even with error handling")
            return None
    
    try:
        print(f"Loaded LUST data: {len(lust_df)} records")
        print(f"Columns found: {list(lust_df.columns)[:10]}...")  # Show first 10 columns for debugging
        
        # Save to Required folder
        lust_output = os.path.join(REQUIRED_PATH, f"{STATE_NAME}_LUST_Raw.xlsx")
        lust_df.to_excel(lust_output, index=False)
        print(f"Saved raw LUST data to: {lust_output}")
        
        return lust_df
        
    except Exception as e:
        print(f"Error processing LUST file: {e}")
        return None
    
def merge_lust_with_ust_data(formatted_df, lust_df):
    """Merge LUST information with UST data"""
    if lust_df is None or lust_df.empty:
        print("No LUST data to merge")
        formatted_df['lust'] = 'No'
        return formatted_df
    
    try:
        print("\n=== Merging LUST data with UST data ===")
        
        # Create matching keys based on facility ID
        lust_facilities = set(lust_df['FACILITY_ID'].astype(str).unique())
        
        # Mark facilities with LUST incidents
        formatted_df['lust'] = formatted_df['facility_id'].astype(str).apply(
            lambda x: 'Yes' if x in lust_facilities else 'No'
        )
        
        # For facilities with LUST, get the status
        lust_status_map = {}
        for _, row in lust_df.iterrows():
            fac_id = str(row['FACILITY_ID'])
            status = safe_string(row.get('MGPTF_STATUS', ''))
            if fac_id not in lust_status_map:
                lust_status_map[fac_id] = status
        
        formatted_df['lust_status'] = formatted_df.apply(
            lambda row: lust_status_map.get(str(row['facility_id']), '') if row['lust'] == 'Yes' else '',
            axis=1
        )
        
        lust_count = (formatted_df['lust'] == 'Yes').sum()
        print(f"Matched {lust_count} facilities with LUST incidents")
        
        return formatted_df
        
    except Exception as e:
        print(f"Error merging LUST data: {e}")
        formatted_df['lust'] = 'No'
        return formatted_df

def process_all_mississippi_data():
    """Process all downloaded Mississippi data files"""
    print(f"\n=== Starting data processing for {STATE_NAME} ===\n")
    
    # Process UST data
    formatted_df = process_mississippi_ust_data()
    
    if formatted_df.empty:
        print("No UST data to process!")
        return
    
    # Process LUST data
    lust_df = process_mississippi_lust_data()
    
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
    
    # Save the formatted data (without LUST info first)
    output_file = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Formatted.xlsx')
    formatted_df.to_excel(output_file, index=False)
    print(f"\n✓ Saved formatted data to: {output_file}")
    print(f"  Total records: {len(formatted_df)}")
    print(f"  Total counties: {formatted_df['county'].nunique()}")
    print(f"  Total facilities: {formatted_df['facility_id'].nunique()}")
    
    # Merge with LUST data
    formatted_df = merge_lust_with_ust_data(formatted_df, lust_df)
    
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
    print(formatted_df[['facility_id', 'tank_id', 'facility_name', 'city', 'county', 'tank_status', 'lust']].head(3).to_string())
    
    # Process statewide LUST data if available
    process_lust_data_formatted(formatted_df)

def process_lust_data_formatted(formatted_df):
    """Process statewide LUST data and update the formatted dataframe"""
    try:
        print('\n=== Processing Statewide LUST Data ===')
        lust_file = os.path.join(BASE_PATH, "L-UST_Data", "LustDataAllStates.xlsx")
        
        if not os.path.exists(lust_file):
            print(f"Warning: Statewide LUST data file not found at {lust_file}")
            return formatted_df
            
        LustData = pd.read_excel(lust_file)
        MS_Lust = LustData[LustData['State Name'] == STATE_NAME]
        
        if len(MS_Lust) == 0:
            print(f"No statewide LUST records found for {STATE_NAME}")
            return formatted_df
        
        print(f'Found {len(MS_Lust)} statewide LUST records for {STATE_NAME}')
        
        # Save Mississippi LUST data
        ms_lust_file = os.path.join(REQUIRED_PATH, f'{STATE_NAME}_Statewide_LustData.xlsx')
        MS_Lust.to_excel(ms_lust_file, index=False)
        
        # Create location matching key
        if 'Address' in MS_Lust.columns and 'City' in MS_Lust.columns:
            MS_Lust['location_city'] = (MS_Lust['Address'].astype(str).str.strip() + '_' + 
                                        MS_Lust['City'].astype(str).str.strip()).str.upper()
            
            formatted_df['location_city'] = (formatted_df['tank_location'].astype(str) + '_' + 
                                            formatted_df['city'].astype(str)).str.upper()
            
            # Remove duplicates from LUST data
            MS_Lust_unique = MS_Lust.drop_duplicates(subset='location_city', keep='first')
            
            # Count how many records will be updated
            existing_lust = (formatted_df['lust'] == 'Yes').sum()
            
            # Merge to find additional matches
            merged = formatted_df.merge(MS_Lust_unique[['location_city', 'Status']], 
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
        
        # Save updated final data
        final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted_with_Statewide_LUST.xlsx')
        formatted_df.to_excel(final_output, index=False)
        print(f"✓ Saved final data with statewide LUST info to: {final_output}")
        
        return formatted_df
        
    except Exception as e:
        print(f"Error processing statewide LUST data: {e}")
        return formatted_df

def main():
    """Main function to orchestrate the entire process"""
    print(f"{'='*60}")
    print(f"Starting {STATE_NAME} UST/LUST Data Download and Processing")
    print(f"{'='*60}")
    print(f"Base path: {BASE_PATH}")
    print(f"Target URL: {URL}")
    
    # Setup folder structure
    log_file = setup_folder_structure()
    print(f"Log file: {log_file}")
    
    # Optional: Clear input folder
    clear_input_folder()
    
    # Download files
    print(f"\n=== Downloading {STATE_NAME} UST and LUST data ===\n")
    downloaded_files = download_mississippi_data()
    
    if downloaded_files:
        print(f"\n✓ Successfully downloaded {len(downloaded_files)} file(s):")
        for file in downloaded_files:
            print(f"  - {file}")
    else:
        print("\n✗ No files were downloaded.")
        print("Please check:")
        print("1. The website is accessible")
        print("2. The download links are visible")
        print("3. The screenshots in the state folder for debugging")
        return
    
    # Wait for files to be completely written
    time.sleep(3)
    
    # Process all data
    process_all_mississippi_data()
    
    print(f"\n{'='*60}")
    print(f'{STATE_NAME} processing completed!')
    print(f"{'='*60}")

if __name__ == "__main__":
    main()