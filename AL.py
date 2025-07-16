from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
import shutil
from datetime import datetime
import numpy as np
from fuzzywuzzy import fuzz
import re

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Alabama"
STATE_ABBR = "AL"
URL = "https://adem.alabama.gov/programs/land/ustcompliancemain.cnt"

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

def download_files_with_playwright():
    """Download files using Playwright"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
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
        time.sleep(2)
        
        download_links = [
            "UST Owners",
            "UST Facilities", 
            "USTs"
        ]
        
        downloaded_files = []
        
        for link_text in download_links:
            try:
                print(f"Looking for '{link_text}' link...")
                
                selectors = [
                    f'a:has-text("{link_text}")',
                    f'a:text-is("{link_text}")',
                    f'text="{link_text}"',
                    f'a >> text={link_text}',
                ]
                
                link_found = False
                
                for selector in selectors:
                    try:
                        if page.locator(selector).count() > 0:
                            print(f"Found '{link_text}' link, clicking...")
                            
                            with page.expect_download() as download_info:
                                page.click(selector, timeout=10000)
                            
                            download = download_info.value
                            suggested_filename = download.suggested_filename
                            
                            final_path = os.path.join(DOWNLOAD_PATH, suggested_filename)
                            download.save_as(final_path)
                            
                            downloaded_files.append({
                                'link_text': link_text,
                                'filename': suggested_filename
                            })
                            print(f"✓ Downloaded: {suggested_filename} from '{link_text}'")
                            link_found = True
                            
                            time.sleep(2)
                            break
                            
                    except Exception as e:
                        continue
                
                if not link_found:
                    print(f"✗ Could not find or click '{link_text}' link")
                    
            except Exception as e:
                print(f"Error processing '{link_text}': {str(e)}")
        
        browser.close()
        
        return downloaded_files

def wait_for_files_to_settle():
    """Ensure all files are completely written"""
    time.sleep(3)
    file_sizes = {}
    
    for file in os.listdir(DOWNLOAD_PATH):
        file_path = os.path.join(DOWNLOAD_PATH, file)
        if os.path.isfile(file_path):
            file_sizes[file] = os.path.getsize(file_path)
    
    time.sleep(2)
    
    for file in os.listdir(DOWNLOAD_PATH):
        file_path = os.path.join(DOWNLOAD_PATH, file)
        if os.path.isfile(file_path):
            new_size = os.path.getsize(file_path)
            if file in file_sizes and file_sizes[file] != new_size:
                print(f"File {file} still downloading...")
                time.sleep(3)

def normalize_address(address):
    """Normalize address for better matching"""
    if pd.isna(address) or address == '':
        return ''
    
    address = str(address).upper().strip()
    address = re.sub(r'[,\.\-\#]', ' ', address)
    address = re.sub(r'\s+', ' ', address)
    
    address_replacements = {
        r'\bSTREET\b': 'ST', r'\bAVENUE\b': 'AVE', r'\bBOULEVARD\b': 'BLVD',
        r'\bPARKWAY\b': 'PKWY', r'\bDRIVE\b': 'DR', r'\bROAD\b': 'RD',
        r'\bLANE\b': 'LN', r'\bCOURT\b': 'CT', r'\bCIRCLE\b': 'CIR',
        r'\bNORTH\b': 'N', r'\bSOUTH\b': 'S', r'\bEAST\b': 'E', r'\bWEST\b': 'W'
    }
    
    for pattern, replacement in address_replacements.items():
        address = re.sub(pattern, replacement, address)
    
    return address.strip()

def find_address_match(al_address, al_state, lust_df):
    """Find matching address in LUST data"""
    if pd.isna(al_address) or al_address == '':
        return None
    
    al_address_norm = normalize_address(al_address)
    al_state_norm = str(al_state).upper().strip()
    
    state_lust = lust_df[lust_df['state'].str.upper() == al_state_norm]
    
    if len(state_lust) == 0:
        return None
    
    # Try exact match first
    for _, lust_row in state_lust.iterrows():
        lust_address_norm = normalize_address(lust_row['site_address'])
        if al_address_norm == lust_address_norm:
            return lust_row['status']
    
    # Try fuzzy matching
    best_match_score = 0
    best_match_status = None
    
    for _, lust_row in state_lust.iterrows():
        lust_address_norm = normalize_address(lust_row['site_address'])
        
        similarity = fuzz.ratio(al_address_norm, lust_address_norm)
        partial_similarity = fuzz.partial_ratio(al_address_norm, lust_address_norm)
        score = max(similarity, partial_similarity)
        
        if score > 85 and score > best_match_score:
            best_match_score = score
            best_match_status = lust_row['status']
    
    return best_match_status

def get_size_range(gallons):
    """Categorize tank size into ranges"""
    if pd.isna(gallons) or gallons <= 0:
        return ''
    elif gallons <= 5000:
        return '0-5000'
    elif gallons <= 10000:
        return '5001-10000'
    elif gallons <= 15000:
        return '10001-15000'
    elif gallons <= 20000:
        return '15001-20000'
    else:
        return '20000+'

def get_tank_construction_rating(construction):
    """Get tank construction rating based on construction type"""
    if pd.isna(construction) or construction == '':
        return ''
    
    construction_str = str(construction).upper()
    
    if any(term in construction_str for term in ['FIBERGLASS', 'FRP', 'DOUBLE WALL', 'COMPOSITE', 
                                                  'CATHODIC', 'PROTECTED', 'STAINLESS']):
        return 'A'
    elif 'STEEL' in construction_str and not any(term in construction_str for term in ['BARE', 'CATHODIC']):
        return 'B'
    elif 'BARE STEEL' in construction_str or construction_str == 'STEEL':
        return 'C'
    else:
        return ''

def extract_tank_size(tank_details):
    """Extract tank size from various possible columns"""
    size_columns = ['Tank Size', 'Size', 'Capacity', 'Volume', 'Gallons']
    
    for col in size_columns:
        if col in tank_details.index and pd.notna(tank_details.get(col)):
            try:
                size_value = tank_details.get(col)
                if isinstance(size_value, str):
                    size_match = re.search(r'(\d+(?:\.\d+)?)', size_value)
                    if size_match:
                        return float(size_match.group(1))
                else:
                    return float(size_value)
            except:
                continue
    
    return 0

def parse_year_from_date(date_value):
    """Extract year from date value"""
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
        
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            return year_match.group(0)
        
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

def normalize_permit_number(permit_num):
    """Normalize permit number for better matching"""
    if pd.isna(permit_num) or permit_num == '':
        return ''
    
    permit_str = str(permit_num).strip()
    
    # Remove common prefixes/suffixes
    permit_str = permit_str.replace('PERMIT-', '').replace('PERM-', '')
    
    # Return both original and normalized versions for matching
    return permit_str

def find_facility_info(permit_number, facilities_dict):
    """Find facility info using multiple matching strategies"""
    if not permit_number:
        return {}
    
    # Strategy 1: Direct match
    if permit_number in facilities_dict:
        return facilities_dict[permit_number]
    
    # Strategy 2: Normalized match
    norm_permit = normalize_permit_number(permit_number)
    if norm_permit in facilities_dict:
        return facilities_dict[norm_permit]
    
    # Strategy 3: Check if permit number is part of facility keys
    for key in facilities_dict.keys():
        if permit_number in key or key in permit_number:
            return facilities_dict[key]
    
    # Strategy 4: Check if it's a tank ID and extract facility part
    if '-' in permit_number:
        # Try different ways to extract facility ID
        parts = permit_number.split('-')
        
        # Try first part
        if parts[0] in facilities_dict:
            return facilities_dict[parts[0]]
        
        # Try first two parts
        if len(parts) >= 2:
            facility_id = '-'.join(parts[:2])
            if facility_id in facilities_dict:
                return facilities_dict[facility_id]
    
    return {}

def process_data():
    """Process the downloaded data"""
    print(f"\n=== Starting data processing for {STATE_NAME} ===\n")
    
    # Check what files were downloaded
    print("Files in Input folder:")
    for file in os.listdir(INPUT_PATH):
        print(f"  - {file}")
    
    # Map expected file types to possible filenames
    file_mappings = {
        'facilities': ['UST_Site', 'UST_Facilities', 'UST Facilities', 'USTFacilities', 'Facilities'],
        'tanks': ['UST_UTanks', 'UST_Tanks', 'USTs', 'UST', 'Tanks', 'UTanks']
    }
    
    found_files = {}
    
    # Find downloaded files
    for file in os.listdir(INPUT_PATH):
        if file.endswith('.xlsx') or file.endswith('.xls'):
            file_lower = file.lower()
            for file_type, patterns in file_mappings.items():
                for pattern in patterns:
                    if pattern.lower().replace('_', '').replace(' ', '') in file_lower.replace('_', '').replace(' ', ''):
                        found_files[file_type] = os.path.join(INPUT_PATH, file)
                        print(f"Identified {file} as {file_type} file")
                        break
    
    # Process Facilities file to create lookup dictionary
    facilities_dict = {}
    permit_number_variations = {}
    
    if 'facilities' in found_files:
        try:
            print(f"\nProcessing Facilities file: {os.path.basename(found_files['facilities'])}")
            df_facilities = pd.read_excel(found_files['facilities'])
            print(f"Facilities file columns: {list(df_facilities.columns)}")
            print(f"Facilities file shape: {df_facilities.shape}")
            
            # Show first few rows to understand structure
            print("\nFirst 3 rows of facilities data:")
            print(df_facilities.head(3).to_string())
            
            # Find the correct column for facility/permit identification
            id_column = None
            possible_id_columns = ['Number', 'Permit Number', 'Facility ID', 'ID', 'Site Number']
            
            for col in possible_id_columns:
                if col in df_facilities.columns:
                    id_column = col
                    break
            
            if id_column:
                print(f"\nUsing '{id_column}' as facility identifier")
                
                # Show sample of IDs
                sample_ids = df_facilities[id_column].head(10).tolist()
                print(f"Sample facility IDs: {sample_ids}")
                
                # Create lookup dictionary
                for _, row in df_facilities.iterrows():
                    facility_id = safe_string(row.get(id_column, ''))
                    
                    if facility_id:
                        facility_info = {
                            'facility_name': safe_string(row.get('Name', '')),
                            'tank_location': safe_string(row.get('Address Street', row.get('Address', ''))),
                            'city': safe_string(row.get('Address City', row.get('City', ''))),
                            'zip': safe_string(row.get('Address PostalCode', row.get('Zip', ''))),
                            'county': safe_string(row.get('County', '')),
                            'latitude': safe_string(row.get('Latitude', '')),
                            'longitude': safe_string(row.get('Longitude', '')),
                            'district': safe_string(row.get('District', '')),
                            'ownership': safe_string(row.get('Ownership', '')),
                            'site_types': safe_string(row.get('Site Types', '')),
                            'status': safe_string(row.get('Status', '')),
                            'entity_category': safe_string(row.get('Entity Category', ''))
                        }
                        
                        # Store with original key
                        facilities_dict[facility_id] = facility_info
                        
                        # Store with normalized key
                        norm_id = normalize_permit_number(facility_id)
                        if norm_id != facility_id:
                            facilities_dict[norm_id] = facility_info
                
                print(f"Created lookup dictionary with {len(facilities_dict)} entries")
                
                # Show sample of what we have
                print("\nSample facility entries:")
                for i, (key, info) in enumerate(list(facilities_dict.items())[:3]):
                    print(f"  {key}: {info['facility_name'][:50]}... at {info['tank_location'][:50]}...")
                    
            else:
                print("Could not find facility ID column in facilities file")
                
        except Exception as e:
            print(f"Error processing Facilities file: {e}")
            import traceback
            traceback.print_exc()
    
    # Process Tanks file
    if 'tanks' in found_files:
        try:
            print(f"\nProcessing Tanks file: {os.path.basename(found_files['tanks'])}")
            df_tanks = pd.read_excel(found_files['tanks'])
            print(f"Tanks file columns: {list(df_tanks.columns)}")
            print(f"Tanks file shape: {df_tanks.shape}")
            
            # Show first few rows
            print("\nFirst 3 rows of tanks data:")
            print(df_tanks.head(3).to_string())
            
            # Find permit number column
            permit_number_col = None
            possible_permit_cols = ['Permit Number', 'PermitNumber', 'Facility Number', 'Site Number']
            
            for col in possible_permit_cols:
                if col in df_tanks.columns:
                    permit_number_col = col
                    break
            
            if not permit_number_col:
                print("ERROR: Could not find permit number column in tanks file!")
                print("Available columns:", list(df_tanks.columns))
                return
            
            print(f"\nUsing '{permit_number_col}' as permit number column")
            
            # Show sample permit numbers
            sample_permits = df_tanks[permit_number_col].head(10).tolist()
            print(f"Sample permit numbers from tanks: {sample_permits}")
            
            # Create the standardized dataframe
            standardized_data = []
            facility_matches = 0
            no_matches = []
            
            for _, tank_row in df_tanks.iterrows():
                # Get permit number (this becomes our facility_id)
                permit_number = safe_string(tank_row.get(permit_number_col, ''))
                
                # Get facility information from lookup dictionary
                facility_info = find_facility_info(permit_number, facilities_dict)
                
                if facility_info:
                    facility_matches += 1
                else:
                    no_matches.append(permit_number)
                
                # Get tank ID
                tank_id_full = safe_string(tank_row.get('Tank Identification Number', ''))
                
                # Process tank status
                tank_status = safe_string(tank_row.get('Tank Status', ''))
                
                # Process substance/content
                substance = safe_string(tank_row.get('Substance Stored', ''))
                petroleum_product = safe_string(tank_row.get('Petroleum Product', ''))
                content = petroleum_product if petroleum_product and petroleum_product != 'nan' else substance
                
                # Process construction materials
                tank_construction = safe_string(tank_row.get('Tank Construction Material', ''))
                pipe_construction = safe_string(tank_row.get('Pipe Construction Material', ''))
                
                # Process dates
                install_date = tank_row.get('Install Date', '')
                
                # Create standardized record
                record = {
                    'state': STATE_NAME,
                    'state_name': STATE_ABBR,
                    'facility_id': permit_number,
                    'tank_id': tank_id_full,
                    'tank_location': facility_info.get('tank_location', ''),
                    'city': facility_info.get('city', ''),
                    'zip': facility_info.get('zip', '')[:5] if facility_info.get('zip') else '',
                    'ust_or_ast': 'UST',
                    'year_installed': format_date_for_output(install_date),
                    'tank_install_year_only': parse_year_from_date(install_date),
                    'tank_size__gallons_': int(extract_tank_size(tank_row)),
                    'size_range': '',
                    'tank_construction': tank_construction if tank_construction != 'nan' else '',
                    'piping_construction': pipe_construction if pipe_construction != 'nan' else '',
                    'secondary_containment__ast_': '',
                    'content_description': content if content != 'nan' else '',
                    'tank_tightness': '',
                    'facility_name': facility_info.get('facility_name', ''),
                    'lust': 'No',
                    'tank_construction_rating': '',
                    'county': facility_info.get('county', ''),
                    'tank_status': tank_status if tank_status != 'nan' else '',
                    'lust_status': '',
                    'last_synch_date': datetime.now().strftime('%Y/%m/%d')
                }
                
                # Process tank size and range
                record['size_range'] = get_size_range(record['tank_size__gallons_'])
                
                # Add tank construction rating
                record['tank_construction_rating'] = get_tank_construction_rating(record['tank_construction'])
                
                standardized_data.append(record)
            
            print(f"\nMatching Results:")
            print(f"  Total tanks: {len(standardized_data)}")
            print(f"  Facility matches found: {facility_matches}")
            print(f"  No matches: {len(no_matches)}")
            
            # Show sample of unmatched permit numbers
            if no_matches:
                print(f"\nSample of unmatched permit numbers: {no_matches[:10]}")
                
                # Try to find patterns
                print("\nTrying to find matching patterns...")
                for permit in no_matches[:5]:
                    print(f"  Looking for matches for '{permit}':")
                    for key in list(facilities_dict.keys())[:10]:
                        if permit in key or key in permit:
                            print(f"    Potential match: '{key}'")
                            break
            
            # Create final dataframe
            final_df = pd.DataFrame(standardized_data)
            
            # Ensure all columns are present and in correct order
            for col in COLUMN_ORDER:
                if col not in final_df.columns:
                    final_df[col] = ''
            
            final_df = final_df[COLUMN_ORDER]
            
            # Process EPA LUST data
            print("\n=== Processing EPA LUST Data ===")
            try:
                epa_lust_path = os.path.join(BASE_PATH, "L-UST_Data", "Output", "EPA_LUST_Data_Raw_20250715_120457.csv")
                
                if os.path.exists(epa_lust_path):
                    print(f"Reading EPA LUST data...")
                    epa_lust_df = pd.read_csv(epa_lust_path)
                    
                    al_lust = epa_lust_df[epa_lust_df['state'].str.upper() == STATE_ABBR.upper()]
                    
                    if len(al_lust) > 0:
                        print(f"Found {len(al_lust)} LUST records for {STATE_NAME}")
                        
                        al_lust.to_csv(os.path.join(REQUIRED_PATH, f'{STATE_NAME}_EPA_LustData.csv'), index=False)
                        
                        matches_found = 0
                        total_records = len(final_df)
                        
                        for index, row in final_df.iterrows():
                            if index % 1000 == 0:
                                print(f"  Processed {index}/{total_records} records...")
                            
                            lust_status = find_address_match(row['tank_location'], row['state_name'], al_lust)
                            
                            if lust_status:
                                final_df.at[index, 'lust'] = 'Yes'
                                final_df.at[index, 'lust_status'] = lust_status
                                matches_found += 1
                        
                        print(f'✓ Found {matches_found} LUST matches')
                        
                    else:
                        print(f'No LUST records found for {STATE_NAME}')
                        
                else:
                    print(f'EPA LUST data file not found')
                    
            except Exception as e:
                print(f'Error processing EPA LUST data: {e}')
            
            # Save the final formatted data
            final_output_xlsx = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
            final_output_csv = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.csv')
            
            final_df.to_excel(final_output_xlsx, index=False)
            final_df.to_csv(final_output_csv, index=False)
            
            print(f"\n✓ Saved final formatted data to: {final_output_xlsx}")
            print(f"✓ Saved CSV version to: {final_output_csv}")
            
            # Print summary
            print("\n=== Data Summary ===")
            print(f"Total tanks: {len(final_df)}")
            print(f"Total facilities (unique permit numbers): {final_df['facility_id'].nunique()}")
            print(f"Records with facility data: {len(final_df[final_df['facility_name'] != ''])}")
            print(f"Records with location data: {len(final_df[final_df['tank_location'] != ''])}")
            print(f"Records with city data: {len(final_df[final_df['city'] != ''])}")
            print(f"Records with zip data: {len(final_df[final_df['zip'] != ''])}")
            print(f"Records with county data: {len(final_df[final_df['county'] != ''])}")
            print(f"Unique counties: {final_df['county'].nunique()}")
            print(f"UST tanks: {(final_df['ust_or_ast'] == 'UST').sum()}")
            print(f"AST tanks: {(final_df['ust_or_ast'] == 'AST').sum()}")
            print(f"LUST sites: {(final_df['lust'] == 'Yes').sum()}")
            
            # Show county breakdown
            if final_df['county'].nunique() > 0:
                print(f"\nRecords by county (top 10):")
                county_counts = final_df['county'].value_
                counts().head(10)
                for county, count in county_counts.items():
                    if county:
                        print(f"  {county}: {count}")
            
            # Show tank status breakdown
            if 'tank_status' in final_df.columns:
                print("\nTank Status Distribution:")
                status_counts = final_df['tank_status'].value_counts().head(10)
                for status, count in status_counts.items():
                    if status:
                        print(f"  {status}: {count}")
            
            # Show content types
            if 'content_description' in final_df.columns:
                print("\nContent Types (top 10):")
                content_counts = final_df['content_description'].value_counts().head(10)
                for content, count in content_counts.items():
                    if content:
                        print(f"  {content}: {count}")
            
            # Show sample of successfully matched data
            print(f"\nSample of successfully matched data:")
            matched_data = final_df[final_df['facility_name'] != '']
            if len(matched_data) > 0:
                sample_df = matched_data[['facility_id', 'tank_id', 'facility_name', 'tank_location', 'city', 'county']].head(5)
                print(sample_df.to_string())
            else:
                print("No successfully matched records found")
            
            # Show sample of unmatched data
            print(f"\nSample of unmatched data:")
            unmatched_data = final_df[final_df['facility_name'] == '']
            if len(unmatched_data) > 0:
                sample_unmatched = unmatched_data[['facility_id', 'tank_id', 'facility_name', 'tank_location', 'city', 'county']].head(5)
                print(sample_unmatched.to_string())
            else:
                print("All records were successfully matched")
                
        except Exception as e:
            print(f"Error processing Tanks file: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ {STATE_NAME} processing completed!")

def main():
    """Main function to orchestrate the entire process"""
    print(f"Starting {STATE_NAME} data download and processing...")
    print(f"Base path: {BASE_PATH}")
    
    # Setup folder structure
    log_file = setup_folder_structure()
    print(f"Log file: {log_file}")
    
    # Optional: Clear input folder
    clear_input_folder()
    
    # Download files
    print(f"\n=== Downloading files for {STATE_NAME} ===\n")
    downloaded_files = download_files_with_playwright()
    
    if downloaded_files:
        print(f"\nSuccessfully downloaded {len(downloaded_files)} files:")
        for file_info in downloaded_files:
            print(f"  - '{file_info['link_text']}' → {file_info['filename']}")
    else:
        print("\nNo files were downloaded. Please check the website structure.")
        return
    
    # Wait for files to be completely written
    wait_for_files_to_settle()
    
    # Process the data
    process_data()

if __name__ == "__main__":
    main()