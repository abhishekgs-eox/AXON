import os
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from fuzzywuzzy import fuzz
import re

# Base configurations
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Texas"
STATE_ABBR = "TX"

INPUT_PATH = os.path.join(BASE_PATH, "states", STATE_NAME, "Input")
OUTPUT_PATH = os.path.join(BASE_PATH, "states", STATE_NAME, "Output")
REQUIRED_PATH = os.path.join(BASE_PATH, "states", STATE_NAME, "Required")
LUST_INPUT_PATH = os.path.join(BASE_PATH, "L-UST_Data")

for folder in [INPUT_PATH, OUTPUT_PATH, REQUIRED_PATH, LUST_INPUT_PATH]:
    os.makedirs(folder, exist_ok=True)

# URLs
UST_URL = "https://www.tceq.texas.gov/assets/public/admin/data/docs/pst_ust.txt"
AST_URL = "https://www.tceq.texas.gov/assets/public/admin/data/docs/pst_ast.txt"
FACILITY_URL = "https://www.tceq.texas.gov/assets/public/admin/data/docs/pst_fac.txt"

def download_file(url, filepath):
    try:
        print(f"Downloading from: {url}")
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Saved to: {filepath}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def read_fixed_file(filepath, colspecs):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = []
            for line_num, line in enumerate(f, 1):
                if line.strip():  # Skip empty lines
                    row = {}
                    for col, start, end in colspecs:
                        try:
                            # Convert to 0-based indexing
                            value = line[start-1:end].strip() if start > 0 else line[start:end].strip()
                            row[col] = value if value else ''
                        except IndexError:
                            row[col] = ''
                    data.append(row)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return pd.DataFrame()

# Updated column specifications based on official Texas PST Data Specifications
FACILITY_COLUMNS = [
    ('facility_id_pk', 1, 8),           # FACILITY ID (Primary Key)
    ('additional_id', 9, 23),           # ADDITIONAL ID (Foreign Key)
    ('facility_id', 24, 29),            # Facility ID (also called facility number or AI)
    ('facility_name', 30, 89),          # Facility Name
    ('facility_type', 90, 119),         # Facility Type
    ('facility_begin_date', 120, 129),  # Facility Begin Date
    ('facility_status', 130, 159),      # Facility Status
    ('facility_exempt_status', 160, 160), # Facility Exempt Status
    ('records_off_site', 161, 161),     # Records Off-Site
    ('ust_financial_assurance_required', 162, 162), # UST Financial Assurance Required
    ('num_active_usts', 163, 166),      # Number of Active USTs
    ('num_active_asts', 167, 170),      # Number of Active ASTs
    ('site_address', 171, 220),         # Site Address (delivery)
    ('city', 221, 250),                 # Site Address (city name)
    ('state_short', 251, 252),          # Site Address (state code)
    ('zip', 253, 257),                  # Site Address (zip code)
    ('zip_extension', 258, 261),        # Site Address (zip code extension)
    ('site_location_description', 262, 517), # Site Location Description
    ('site_nearest_city', 518, 552),    # Site Location (nearest city name)
    ('county', 553, 587),               # Site Location (county name)
    ('tceq_region', 588, 589),          # Site Location (TCEQ region)
    ('location_zip', 590, 594),         # Site Location (location zip)
    ('facility_contact_first_name', 595, 609), # Facility Contact First Name
    ('facility_contact_last_name', 625, 652),  # Facility Contact Last Name
    ('facility_contact_organization', 713, 812), # Facility Contact Organization Name
    ('facility_contact_phone_area', 954, 956), # Facility Contact Phone Area Code
    ('facility_contact_phone', 957, 963),      # Facility Contact Phone Number
    ('facility_contact_email', 984, 1033),     # Facility Contact Email Address
]

UST_COLUMNS = [
    ('ust_id_pk', 1, 8),                # UST ID (Primary Key)
    ('facility_id_fk', 9, 16),          # FACILITY ID (Foreign Key)
    ('facility_id', 17, 22),            # Facility ID
    ('tank_id', 23, 32),                # Tank ID
    ('num_compartments', 33, 34),       # Number of Compartments
    ('tank_install_date', 35, 44),      # Tank Installation Date
    ('tank_registration_date', 45, 54), # Tank Registration Date
    ('tank_capacity', 55, 62),          # Tank Capacity (in gallons)
    ('tank_status', 63, 92),            # Tank Status (current)
    ('tank_status_begin_date', 93, 102), # Tank Status Begin Date
    ('empty_flag', 103, 103),           # Empty (Y = Empty, N = Not Empty)
    ('tank_regulatory_status', 104, 133), # Tank Regulatory Status
    ('tank_internal_protection_date', 134, 143), # Tank Internal Protection Date
    ('tank_design_single_wall', 144, 144), # Tank Design (Single Wall)
    ('tank_design_double_wall', 145, 145), # Tank Design (Double Wall)
    ('piping_design_single_wall', 146, 146), # Piping Design (Single Wall)
    ('piping_design_double_wall', 147, 147), # Piping Design (Double Wall)
    ('piping_type', 154, 154),          # Type of Piping (P=Pressurized, S=Suction, G=Gravity)
    ('tank_material_steel', 155, 155),  # Tank Material (Steel)
    ('tank_material_frp', 156, 156),    # Tank Material (FRP)
    ('tank_material_composite', 157, 157), # Tank Material (Composite)
    ('tank_material_concrete', 158, 158), # Tank Material (Concrete)
    ('tank_material_jacketed', 159, 159), # Tank Material (Jacketed)
    ('tank_material_coated', 160, 160), # Tank Material (Coated)
    ('piping_material_steel', 161, 161), # Piping Material (Steel)
    ('piping_material_frp', 162, 162),  # Piping Material (FRP)
    ('piping_material_concrete', 163, 163), # Piping Material (Concrete)
    ('piping_material_jacketed', 164, 164), # Piping Material (Jacketed)
    ('piping_material_nonmetallic_flexible', 165, 165), # Piping Material (Nonmetallic flexible)
    ('tank_corrosion_protection_compliance', 185, 185), # Tank Corrosion Protection Compliance
    ('piping_corrosion_protection_compliance', 186, 186), # Piping Corrosion Protection Compliance
    ('tank_corrosion_protection_variance', 187, 187), # Tank Corrosion Protection Variance
    ('piping_corrosion_protection_variance', 188, 188), # Piping Corrosion Protection Variance
    ('technical_compliance_flag', 190, 190), # Technical Compliance Flag
    ('tank_tested_flag', 191, 191),     # Tank Tested Flag
    ('installation_signature_date', 192, 201), # Installation Signature Date
]

AST_COLUMNS = [
    ('ast_id_pk', 1, 8),                # AST ID (Primary Key)
    ('facility_id_fk', 9, 16),          # FACILITY ID (Foreign Key)
    ('facility_id', 17, 22),            # Facility ID
    ('tank_id', 23, 32),                # Tank ID
    ('multiple_compartment_flag', 33, 33), # Multiple Compartment Flag
    ('tank_install_date', 34, 43),      # Tank Installation Date
    ('tank_registration_date', 44, 53), # Tank Registration Date
    ('tank_status', 54, 83),            # Tank Status (current)
    ('tank_status_begin_date', 84, 93), # Tank Status Begin Date
    ('tank_regulatory_status', 94, 123), # Tank Regulatory Status
    ('tank_capacity', 124, 131),        # Tank Capacity (in gallons)
    ('substance_stored_1', 132, 161),   # Substance Stored
    ('substance_stored_2', 162, 191),   # Substance Stored
    ('substance_stored_3', 192, 221),   # Substance Stored
    ('material_construction_steel', 222, 222), # Material of Construction (Steel)
    ('material_construction_fiberglass', 223, 223), # Material of Construction (Fiberglass)
    ('material_construction_aluminum', 224, 224), # Material of Construction (Aluminum)
    ('material_construction_corrugated_metal', 225, 225), # Material of Construction (Corrugated Metal)
    ('material_construction_concrete', 226, 226), # Material of Construction (Concrete)
    ('containment_earthen_dike', 227, 227), # Containment (Earthen Dike)
    ('containment_liner', 228, 228),    # Containment (Containment Liner)
    ('containment_concrete', 229, 229), # Containment (Concrete)
    ('containment_none', 230, 230),     # Containment (None)
    ('stage_i_vapor_recovery', 231, 260), # Stage I Vapor Recovery
    ('stage_i_install_date', 261, 270), # Stage I Installation Date
]

def normalize_address(address):
    """Normalize address for better matching"""
    if pd.isna(address) or address == '':
        return ''
    
    # Convert to uppercase and strip whitespace
    address = str(address).upper().strip()
    
    # Remove common punctuation
    address = re.sub(r'[,\.\-\#]', ' ', address)
    
    # Replace multiple spaces with single space
    address = re.sub(r'\s+', ' ', address)
    
    # Common address abbreviations standardization
    address_replacements = {
        r'\bSTREET\b': 'ST',
        r'\bAVENUE\b': 'AVE',
        r'\bBOULEVARD\b': 'BLVD',
        r'\bPARKWAY\b': 'PKWY',
        r'\bDRIVE\b': 'DR',
        r'\bROAD\b': 'RD',
        r'\bLANE\b': 'LN',
        r'\bCOURT\b': 'CT',
        r'\bCIRCLE\b': 'CIR',
        r'\bNORTH\b': 'N',
        r'\bSOUTH\b': 'S',
        r'\bEAST\b': 'E',
        r'\bWEST\b': 'W'
    }
    
    for pattern, replacement in address_replacements.items():
        address = re.sub(pattern, replacement, address)
    
    return address.strip()

def find_address_match(tx_address, tx_state, lust_df):
    """Find matching address in LUST data using multiple matching strategies"""
    if pd.isna(tx_address) or tx_address == '':
        return None
    
    # Normalize the Texas address
    tx_address_norm = normalize_address(tx_address)
    tx_state_norm = str(tx_state).upper().strip()
    
    # Filter LUST data for same state
    state_lust = lust_df[lust_df['state'].str.upper() == tx_state_norm]
    
    if len(state_lust) == 0:
        return None
    
    # Strategy 1: Exact match (after normalization)
    for _, lust_row in state_lust.iterrows():
        lust_address_norm = normalize_address(lust_row['site_address'])
        if tx_address_norm == lust_address_norm:
            return lust_row['status']
    
    # Strategy 2: Check if Texas address (truncated) is contained in LUST address
    for _, lust_row in state_lust.iterrows():
        lust_address_norm = normalize_address(lust_row['site_address'])
        if len(tx_address_norm) > 5 and tx_address_norm in lust_address_norm:
            return lust_row['status']
    
    # Strategy 3: Check if LUST address starts with Texas address (common for truncated addresses)
    for _, lust_row in state_lust.iterrows():
        lust_address_norm = normalize_address(lust_row['site_address'])
        if len(tx_address_norm) > 5 and lust_address_norm.startswith(tx_address_norm):
            return lust_row['status']
    
    # Strategy 4: Fuzzy matching for similar addresses
    best_match_score = 0
    best_match_status = None
    
    for _, lust_row in state_lust.iterrows():
        lust_address_norm = normalize_address(lust_row['site_address'])
        
        # Calculate similarity score
        similarity = fuzz.ratio(tx_address_norm, lust_address_norm)
        
        # Also check partial ratio (for truncated addresses)
        partial_similarity = fuzz.partial_ratio(tx_address_norm, lust_address_norm)
        
        # Use the higher score
        score = max(similarity, partial_similarity)
        
        # If score is high enough and better than previous best
        if score > 85 and score > best_match_score:
            best_match_score = score
            best_match_status = lust_row['status']
    
    return best_match_status

def safe_int(x):
    try:
        return int(float(str(x).replace(',', '')))
    except:
        return 0

def safe_string(x):
    try:
        return str(x).strip()
    except:
        return ''

def format_date_for_output(date_value):
    """Format date as YYYY/MM/DD"""
    if pd.isna(date_value) or date_value == '':
        return ''
    
    try:
        date_str = str(date_value).strip()
        
        # Handle MM/DD/YYYY format
        if '/' in date_str and len(date_str) == 10:
            try:
                dt = datetime.strptime(date_str, '%m/%d/%Y')
                return dt.strftime('%Y/%m/%d')
            except:
                pass
        
        # Handle other formats
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y/%m/%d')
            except:
                continue
        
        return date_str
    except:
        return ''

def parse_year_from_date(date_value):
    """Extract year from date value"""
    if pd.isna(date_value) or date_value == '':
        return ''
    
    try:
        date_str = str(date_value).strip()
        
        # If it's already a 4-digit year
        if len(date_str) == 4 and date_str.isdigit():
            return date_str
        
        # Try to parse various date formats
        for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return str(dt.year)
            except:
                continue
        
        # Extract last 4 digits if they represent a year
        if len(date_str) >= 4:
            last_four = date_str[-4:]
            if last_four.isdigit() and 1900 <= int(last_four) <= 2100:
                return last_four
        
        return ''
    except:
        return ''

def get_tank_construction(row):
    """Determine tank construction based on materials and design"""
    construction = []
    
    # Check materials
    if row.get('tank_material_steel') == 'Y':
        construction.append('Steel')
    if row.get('tank_material_frp') == 'Y':
        construction.append('FRP')
    if row.get('tank_material_composite') == 'Y':
        construction.append('Composite')
    if row.get('tank_material_concrete') == 'Y':
        construction.append('Concrete')
    if row.get('tank_material_jacketed') == 'Y':
        construction.append('Jacketed')
    if row.get('tank_material_coated') == 'Y':
        construction.append('Coated')
    
    # Check design
    if row.get('tank_design_single_wall') == 'Y':
        construction.append('Single Wall')
    if row.get('tank_design_double_wall') == 'Y':
        construction.append('Double Wall')
    
    return ', '.join(construction) if construction else ''

def get_piping_construction(row):
    """Determine piping construction based on materials and design"""
    construction = []
    
    # Check materials
    if row.get('piping_material_steel') == 'Y':
        construction.append('Steel')
    if row.get('piping_material_frp') == 'Y':
        construction.append('FRP')
    if row.get('piping_material_concrete') == 'Y':
        construction.append('Concrete')
    if row.get('piping_material_jacketed') == 'Y':
        construction.append('Jacketed')
    if row.get('piping_material_nonmetallic_flexible') == 'Y':
        construction.append('Nonmetallic Flexible')
    
    # Check design
    if row.get('piping_design_single_wall') == 'Y':
        construction.append('Single Wall')
    if row.get('piping_design_double_wall') == 'Y':
        construction.append('Double Wall')
    
    return ', '.join(construction) if construction else ''

def get_secondary_containment_ast(row):
    """Determine secondary containment for AST"""
    containment = []
    
    if row.get('containment_earthen_dike') == 'Y':
        containment.append('Earthen Dike')
    if row.get('containment_liner') == 'Y':
        containment.append('Containment Liner')
    if row.get('containment_concrete') == 'Y':
        containment.append('Concrete')
    
    if containment:
        return ', '.join(containment)
    elif row.get('containment_none') == 'Y':
        return 'None'
    else:
        return ''

def get_content_description(row):
    """Get content description for AST"""
    content = []
    
    for i in range(1, 4):
        substance = row.get(f'substance_stored_{i}', '')
        if substance and substance not in content:
            content.append(substance)
    
    return ', '.join(content) if content else ''

def get_construction_rating(row):
    """Determine construction rating based on compliance"""
    tank_compliance = row.get('tank_corrosion_protection_compliance', '')
    piping_compliance = row.get('piping_corrosion_protection_compliance', '')
    
    if tank_compliance == 'Y' and piping_compliance == 'Y':
        return 'A'
    elif tank_compliance == 'Y' or piping_compliance == 'Y':
        return 'B'
    elif tank_compliance == 'N' or piping_compliance == 'N':
        return 'C'
    else:
        return ''

def process_data():
    print(f"Starting {STATE_NAME} PST data processing...")
    
    # Download files
    print("Downloading data files...")
    download_success = True
    download_success &= download_file(UST_URL, f"{INPUT_PATH}/ust.txt")
    download_success &= download_file(AST_URL, f"{INPUT_PATH}/ast.txt")
    download_success &= download_file(FACILITY_URL, f"{INPUT_PATH}/facility.txt")
    
    if not download_success:
        print("Some downloads failed. Please check the URLs and try again.")
        return
    
    # Read data files
    print("Reading data files...")
    ust_df = read_fixed_file(f"{INPUT_PATH}/ust.txt", UST_COLUMNS)
    ast_df = read_fixed_file(f"{INPUT_PATH}/ast.txt", AST_COLUMNS)
    facility_df = read_fixed_file(f"{INPUT_PATH}/facility.txt", FACILITY_COLUMNS)
    
    print(f"Read {len(ust_df)} UST records")
    print(f"Read {len(ast_df)} AST records")
    print(f"Read {len(facility_df)} facility records")
    
    if ust_df.empty and ast_df.empty:
        print("No tank data found. Exiting.")
        return
    
    # Add tank type identifiers
    ust_df['ust_or_ast'] = 'UST'
    ast_df['ust_or_ast'] = 'AST'
    
    # Combine UST and AST data
    print("Combining UST and AST data...")
    
    # Ensure both dataframes have the same columns for concatenation
    all_columns = set(ust_df.columns) | set(ast_df.columns)
    for col in all_columns:
        if col not in ust_df.columns:
            ust_df[col] = ''
        if col not in ast_df.columns:
            ast_df[col] = ''
    
    # Reorder columns to match
    common_columns = sorted(all_columns)
    ust_df = ust_df[common_columns]
    ast_df = ast_df[common_columns]
    
    # Combine dataframes
    combined_df = pd.concat([ust_df, ast_df], ignore_index=True)
    
    # Merge with facility data
    print("Merging with facility data...")
    merged_df = combined_df.merge(facility_df, on='facility_id', how='left')
    
    print(f"Merged dataset contains {len(merged_df)} records")
    
    # Create final formatted dataframe
    print("Creating final formatted dataset...")
    
    final_data = []
    
    for _, row in merged_df.iterrows():
        processed_row = {
            'state': STATE_NAME,
            'state_name': STATE_ABBR,
            'facility_id': safe_string(row['facility_id']),
            'tank_id': safe_string(row['tank_id']),
            'tank_location': safe_string(row['site_address']),
            'city': safe_string(row['city']),
            'zip': safe_string(row['zip'])[:5],
            'ust_or_ast': safe_string(row['ust_or_ast']),
            'year_installed': format_date_for_output(row.get('tank_install_date', '')),
            'tank_install_year_only': parse_year_from_date(row.get('tank_install_date', '')),
            'tank_size__gallons_': safe_int(row.get('tank_capacity', 0)),
            'size_range': '',
            'tank_construction': get_tank_construction(row),
            'piping_construction': get_piping_construction(row),
            'secondary_containment__ast_': get_secondary_containment_ast(row) if row['ust_or_ast'] == 'AST' else '',
            'content_description': get_content_description(row),
            'tank_tightness': 'Yes' if row.get('tank_tested_flag') == 'Y' else '',
            'facility_name': safe_string(row['facility_name']),
            'lust': 'No',
            'tank_construction_rating': get_construction_rating(row),
            'county': safe_string(row['county']),
            'tank_status': safe_string(row['tank_status']),
            'lust_status': '',
            'last_synch_date': datetime.now().strftime('%Y/%m/%d')
        }
        
        # Calculate size range
        tank_size = processed_row['tank_size__gallons_']
        if tank_size <= 5000:
            processed_row['size_range'] = '0-5000'
        elif tank_size <= 10000:
            processed_row['size_range'] = '5001-10000'
        elif tank_size <= 15000:
            processed_row['size_range'] = '10001-15000'
        elif tank_size <= 20000:
            processed_row['size_range'] = '15001-20000'
        else:
            processed_row['size_range'] = '20000+'
        
        final_data.append(processed_row)
    
    df_final = pd.DataFrame(final_data)
    
    # Ensure all columns are in the correct order
    column_order = [
        'state', 'state_name', 'facility_id', 'tank_id', 'tank_location',
        'city', 'zip', 'ust_or_ast', 'year_installed', 'tank_install_year_only',
        'tank_size__gallons_', 'size_range', 'tank_construction', 'piping_construction',
        'secondary_containment__ast_', 'content_description', 'tank_tightness',
        'facility_name', 'lust', 'tank_construction_rating', 'county',
        'tank_status', 'lust_status', 'last_synch_date'
    ]
    
    df_final = df_final[column_order]
    
    # Process EPA LUST data with improved address matching
    print("Processing EPA LUST data with improved address matching...")
    try:
        # Updated path to EPA LUST data
        epa_lust_path = os.path.join(BASE_PATH, "L-UST_Data", "Output", "EPA_LUST_Data_Raw_20250715_120457.csv")
        
        if os.path.exists(epa_lust_path):
            print(f"Reading EPA LUST data from: {epa_lust_path}")
            epa_lust_df = pd.read_csv(epa_lust_path)
            
            # Filter for Texas records (case insensitive)
            tx_lust = epa_lust_df[epa_lust_df['state'].str.upper() == STATE_ABBR.upper()]
            
            if len(tx_lust) > 0:
                print(f"Found {len(tx_lust)} LUST records for {STATE_NAME}")
                
                # Save Texas LUST data
                tx_lust.to_csv(os.path.join(REQUIRED_PATH, f'{STATE_NAME}_EPA_LustData.csv'), index=False)
                
                # Process address matching with improved algorithm
                print("Processing address matching (this may take a few minutes)...")
                
                matches_found = 0
                total_records = len(df_final)
                
                for index, row in df_final.iterrows():
                    if index % 1000 == 0:
                        print(f"  Processed {index}/{total_records} records...")
                    
                    # Find matching LUST record
                    lust_status = find_address_match(row['tank_location'], row['state_name'], tx_lust)
                    
                    if lust_status:
                        df_final.at[index, 'lust'] = 'Yes'
                        df_final.at[index, 'lust_status'] = lust_status
                        matches_found += 1
                
                print(f'✓ Found {matches_found} LUST matches using improved address matching')
                
                # Show some examples of matches for verification
                if matches_found > 0:
                    print("\nSample of LUST matches:")
                    lust_matches = df_final[df_final['lust'] == 'Yes'].head(5)
                    for _, match in lust_matches.iterrows():
                        print(f"  Facility: {match['facility_name'][:50]}...")
                        print(f"  TX Address: {match['tank_location'][:50]}...")
                        print(f"  Status: {match['lust_status']}")
                        
                        # Show corresponding LUST record
                        matching_lust = tx_lust[tx_lust['status'] == match['lust_status']]
                        if len(matching_lust) > 0:
                            lust_addr = matching_lust.iloc[0]['site_address']
                            print(f"  LUST Address: {lust_addr[:50]}...")
                        print()
                
            else:
                print(f'No LUST records found for {STATE_NAME} in EPA data')
                
        else:
            print(f'EPA LUST data file not found at: {epa_lust_path}')
            print('Skipping LUST processing.')
            
    except Exception as e:
        print(f'Error processing EPA LUST data: {e}')
        import traceback
        traceback.print_exc()
    
    # Save final data
    print("Saving final data...")
    final_outfile = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
    df_final.to_excel(final_outfile, index=False)
    
    # Also save as CSV
    csv_outfile = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.csv')
    df_final.to_csv(csv_outfile, index=False)
    
    print(f"Total counties: {df_final['county'].nunique()}")
    print(f"Total facilities: {df_final['facility_id'].nunique()}")
    print(f"UST tanks: {(df_final['ust_or_ast'] == 'UST').sum()}")
    print(f"AST tanks: {(df_final['ust_or_ast'] == 'AST').sum()}")
    print(f"LUST sites: {(df_final['lust'] == 'Yes').sum()}")
    
    # Show county breakdown
    print(f"\nRecords by county (top 10):")
    county_counts = df_final['county'].value_counts().head(10)
    for county, count in county_counts.items():
        print(f"  {county}: {count}")
    
    # Show LUST status breakdown
    if (df_final['lust'] == 'Yes').sum() > 0:
        print(f"\nLUST status breakdown:")
        lust_status_counts = df_final[df_final['lust'] == 'Yes']['lust_status'].value_counts()
        for status, count in lust_status_counts.items():
            print(f"  {status}: {count}")
    
    print(f"\n✅ Data processed successfully!")
    print(f"Final Excel file: {final_outfile}")
    print(f"Final CSV file: {csv_outfile}")

if __name__ == "__main__":
    process_data()