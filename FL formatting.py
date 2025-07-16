import os
import pandas as pd
import numpy as np
from datetime import datetime
from fuzzywuzzy import fuzz
import re

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Florida"
STATE_ABBR = "FL"

# Dynamic paths based on state
STATE_PATH = os.path.join(BASE_PATH, "states", STATE_NAME)
INPUT_PATH = os.path.join(STATE_PATH, "Input")
OUTPUT_PATH = os.path.join(STATE_PATH, "Output")
REQUIRED_PATH = os.path.join(STATE_PATH, "Required")

# Ensure output folders exist
for folder in [OUTPUT_PATH, REQUIRED_PATH]:
    os.makedirs(folder, exist_ok=True)

# Florida County Code to Name Mapping
FLORIDA_COUNTY_MAPPING = {
    1: "ALACHUA", 2: "BAKER", 3: "BAY", 4: "BRADFORD", 5: "BREVARD", 6: "BROWARD",
    7: "CALHOUN", 8: "CHARLOTTE", 9: "CITRUS", 10: "CLAY", 11: "COLLIER", 12: "COLUMBIA",
    13: "MIAMI-DADE", 14: "DESOTO", 15: "DIXIE", 16: "DUVAL", 17: "ESCAMBIA", 18: "FLAGLER",
    19: "FRANKLIN", 20: "GADSDEN", 21: "GILCHRIST", 22: "GLADES", 23: "GULF", 24: "HAMILTON",
    25: "HARDEE", 26: "HENDRY", 27: "HERNANDO", 28: "HIGHLANDS", 29: "HILLSBOROUGH", 30: "HOLMES",
    31: "INDIAN RIVER", 32: "JACKSON", 33: "JEFFERSON", 34: "LAFAYETTE", 35: "LAKE", 36: "LEE",
    37: "LEON", 38: "LEVY", 39: "LIBERTY", 40: "MADISON", 41: "MANATEE", 42: "MARION",
    43: "MARTIN", 44: "MONROE", 45: "NASSAU", 46: "OKALOOSA", 47: "OKEECHOBEE", 48: "ORANGE",
    49: "OSCEOLA", 50: "PALM BEACH", 51: "PASCO", 52: "PINELLAS", 53: "POLK", 54: "PUTNAM",
    55: "SANTA ROSA", 56: "SARASOTA", 57: "SEMINOLE", 58: "ST. JOHNS", 59: "ST. LUCIE",
    60: "SUMTER", 61: "SUWANNEE", 62: "TAYLOR", 63: "UNION", 64: "VOLUSIA", 65: "WAKULLA",
    66: "WALTON", 67: "WASHINGTON"
}

# Florida Tank Status Mapping
FLORIDA_TANK_STATUS_MAPPING = {
    'A': 'ACTIVE',
    'B': 'TEMPORARILY OUT OF SERVICE',
    'C': 'CLOSED',
    'D': 'DECOMMISSIONED',
    'E': 'EMPTY',
    'F': 'FILLED',
    'I': 'INACTIVE',
    'O': 'OUT OF SERVICE',
    'P': 'PERMANENT CLOSURE',
    'R': 'REMOVED',
    'S': 'SUSPENDED',
    'T': 'TESTING',
    'U': 'UNKNOWN'
}

def detect_file_format(file_path):
    """Detect the actual format of the file"""
    try:
        with open(file_path, 'rb') as f:
            first_bytes = f.read(512)
        
        if b'<html' in first_bytes.lower() or b'<table' in first_bytes.lower():
            return 'html'
        elif first_bytes.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
            return 'xls'
        elif first_bytes.startswith(b'PK\x03\x04'):
            return 'xlsx'
        else:
            return 'html'  # Default to HTML for Florida files
    except Exception as e:
        print(f"Error detecting file format: {e}")
        return 'html'

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

def find_address_match(fl_address, fl_state, lust_df):
    """Find matching address in LUST data"""
    if pd.isna(fl_address) or fl_address == '':
        return None
    
    fl_address_norm = normalize_address(fl_address)
    fl_state_norm = str(fl_state).upper().strip()
    
    state_lust = lust_df[lust_df['state'].str.upper() == fl_state_norm]
    
    if len(state_lust) == 0:
        return None
    
    # Try exact match first
    for _, lust_row in state_lust.iterrows():
        lust_address_norm = normalize_address(lust_row['site_address'])
        if fl_address_norm == lust_address_norm:
            return lust_row['status']
    
    # Try fuzzy matching
    best_match_score = 0
    best_match_status = None
    
    for _, lust_row in state_lust.iterrows():
        lust_address_norm = normalize_address(lust_row['site_address'])
        
        similarity = fuzz.ratio(fl_address_norm, lust_address_norm)
        partial_similarity = fuzz.partial_ratio(fl_address_norm, lust_address_norm)
        score = max(similarity, partial_similarity)
        
        if score > 85 and score > best_match_score:
            best_match_score = score
            best_match_status = lust_row['status']
    
    return best_match_status

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

def parse_florida_date(date_str):
    """Parse Florida date format (e.g., '01-Aug-76') to datetime"""
    if pd.isna(date_str) or date_str == '':
        return None
    
    try:
        date_str = str(date_str).strip()
        
        # Skip if it's obviously not a date
        if date_str.upper() in ['NAN', 'NONE', 'NULL', '']:
            return None
        
        # Try various Florida date formats
        formats = [
            '%d-%b-%y',      # 01-Aug-76
            '%d-%B-%y',      # 01-August-76
            '%d-%b-%Y',      # 01-Aug-1976
            '%d-%B-%Y',      # 01-August-1976
            '%m-%d-%y',      # 08-01-76
            '%m-%d-%Y',      # 08-01-1976
            '%m/%d/%y',      # 08/01/76
            '%m/%d/%Y',      # 08/01/1976
            '%d/%m/%y',      # 01/08/76
            '%d/%m/%Y',      # 01/08/1976
            '%Y-%m-%d',      # 1976-08-01
            '%Y/%m/%d',      # 1976/08/01
            '%d-%m-%Y',      # 01-08-1976
            '%d-%m-%y'       # 01-08-76
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                # Handle 2-digit years
                if dt.year < 50:
                    dt = dt.replace(year=dt.year + 2000)
                elif dt.year < 100:
                    dt = dt.replace(year=dt.year + 1900)
                return dt
            except:
                continue
        
        # Try to extract date parts with regex
        # Pattern for formats like "01-Aug-76"
        month_pattern = r'(\d{1,2})[/-]([A-Za-z]{3,9})[/-](\d{2,4})'
        match = re.search(month_pattern, date_str)
        if match:
            day, month_str, year = match.groups()
            month_mapping = {
                'JAN': 1, 'JANUARY': 1, 'FEB': 2, 'FEBRUARY': 2, 'MAR': 3, 'MARCH': 3,
                'APR': 4, 'APRIL': 4, 'MAY': 5, 'JUN': 6, 'JUNE': 6, 'JUL': 7, 'JULY': 7,
                'AUG': 8, 'AUGUST': 8, 'SEP': 9, 'SEPTEMBER': 9, 'OCT': 10, 'OCTOBER': 10,
                'NOV': 11, 'NOVEMBER': 11, 'DEC': 12, 'DECEMBER': 12
            }
            
            month_num = month_mapping.get(month_str.upper())
            if month_num:
                year_int = int(year)
                if year_int < 50:
                    year_int += 2000
                elif year_int < 100:
                    year_int += 1900
                
                try:
                    return datetime(year_int, month_num, int(day))
                except:
                    pass
        
        return None
    except:
        return None

def parse_year_from_date(date_value):
    """Extract year from date"""
    if pd.isna(date_value) or date_value == '':
        return ''
    
    try:
        if hasattr(date_value, 'year'):
            return str(date_value.year)
        
        dt = parse_florida_date(date_value)
        if dt:
            return str(dt.year)
        
        return ''
    except:
        return ''

def format_date_for_output(date_value):
    """Format date as YYYY/MM/DD"""
    if pd.isna(date_value) or date_value == '':
        return ''
    
    try:
        dt = parse_florida_date(date_value)
        if dt:
            return dt.strftime('%Y/%m/%d')
        return ''
    except:
        return ''

def determine_tank_construction(row):
    """Determine tank construction based on available data"""
    # Check various possible columns for construction info
    construction_indicators = []
    
    # Check for wall type indicators
    for col in row.index:
        col_upper = str(col).upper()
        value = str(row[col]).upper() if pd.notna(row[col]) else ''
        
        # Look for wall type indicators
        if any(indicator in col_upper for indicator in ['WALL', 'CONSTRUCT', 'DESIGN', 'TYPE']):
            if 'DOUBLE' in value or 'DUAL' in value:
                construction_indicators.append('Double Wall')
            elif 'SINGLE' in value or 'MONO' in value:
                construction_indicators.append('Single Wall')
        
        # Look for material indicators that might suggest construction
        if any(indicator in col_upper for indicator in ['MATERIAL', 'LINING', 'PROTECTION']):
            if 'STEEL' in value:
                if 'DOUBLE' in value:
                    construction_indicators.append('Double Wall Steel')
                elif 'SINGLE' in value:
                    construction_indicators.append('Single Wall Steel')
                else:
                    construction_indicators.append('Steel')
            elif 'FIBERGLASS' in value or 'FRP' in value:
                construction_indicators.append('Fiberglass')
            elif 'COMPOSITE' in value:
                construction_indicators.append('Composite')
    
    # Check PLACE column for additional info
    place = str(row.get('PLACE', '')).upper()
    if 'UNDERGROUND' in place:
        if construction_indicators:
            return f"Underground {construction_indicators[0]}"
        else:
            return "Underground Single Wall"  # Default for UST
    elif 'ABOVEGROUND' in place:
        if construction_indicators:
            return f"Aboveground {construction_indicators[0]}"
        else:
            return "Aboveground Single Wall"  # Default for AST
    
    # If we found construction indicators, return the first one
    if construction_indicators:
        return construction_indicators[0]
    
    # Default based on tank type
    tank_type = str(row.get('TYPE DESC', '')).upper()
    if 'UNDERGROUND' in tank_type:
        return "Underground Single Wall"
    elif 'ABOVEGROUND' in tank_type:
        return "Aboveground Single Wall"
    
    return "Single Wall"  # Default

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

def read_file_with_multiple_methods(file_path):
    """Try multiple methods to read the file"""
    print(f"  Trying to read file...")
    
    # Method 1: Try as HTML
    try:
        tables = pd.read_html(file_path)
        if tables:
            df = tables[0]
            print(f"  ✓ Successfully read as HTML, shape: {df.shape}")
            return df
    except Exception as e:
        print(f"  HTML read failed: {e}")
    
    # Method 2: Try as Excel
    try:
        df = pd.read_excel(file_path, engine='xlrd')
        print(f"  ✓ Successfully read as Excel, shape: {df.shape}")
        return df
    except Exception as e:
        print(f"  Excel read failed: {e}")
    
    # Method 3: Try as CSV
    try:
        df = pd.read_csv(file_path)
        print(f"  ✓ Successfully read as CSV, shape: {df.shape}")
        return df
    except Exception as e:
        print(f"  CSV read failed: {e}")
    
    print("  ✗ All read methods failed")
    return None

def process_florida_county_file(file_path):
    """Process a single Florida county file"""
    try:
        print(f"Processing: {os.path.basename(file_path)}")
        
        df_raw = read_file_with_multiple_methods(file_path)
        
        if df_raw is None:
            print("  ✗ Could not read file")
            return pd.DataFrame()
        
        # Find header row
        header_row_idx = None
        for i in range(min(10, len(df_raw))):
            if 'COUNTY' in str(df_raw.iloc[i].values).upper():
                header_row_idx = i
                break
        
        if header_row_idx is not None:
            df_raw.columns = df_raw.iloc[header_row_idx]
            df_raw = df_raw.iloc[header_row_idx + 1:].reset_index(drop=True)
        
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        
        print(f"  Columns found: {list(df_raw.columns)}")
        
        if df_raw.empty:
            print("  ✗ No data rows found")
            return pd.DataFrame()
        
        # Check if INSTALL column exists
        install_col_found = 'INSTALL' in df_raw.columns
        print(f"  INSTALL column found: {install_col_found}")
        
        if install_col_found:
            # Show sample of INSTALL column data
            install_sample = df_raw['INSTALL'].head(3).tolist()
            print(f"  Sample INSTALL values: {install_sample}")
        
        processed_rows = []
        dates_processed = 0
        dates_successful = 0
        
        for idx, row in df_raw.iterrows():
            if row.isna().all():
                continue
                
            processed_row = {
                'state': STATE_NAME,
                'state_name': STATE_ABBR,
                'facility_id': safe_string(row.get('FAC ID', '')),
                'tank_id': safe_string(row.get('TKID', '')),
                'tank_location': safe_string(row.get('FAC ADDR', '')),
                'city': safe_string(row.get('FAC CITY', '')),
                'zip': safe_string(row.get('FAC ZIP', ''))[:5],
                'facility_name': safe_string(row.get('FAC NAME', ''))
            }
            
            # County mapping
            county_code = safe_string(row.get('COUNTY', ''))
            if county_code.isdigit():
                county_num = int(county_code)
                processed_row['county'] = FLORIDA_COUNTY_MAPPING.get(county_num, f"COUNTY_{county_num}")
            else:
                processed_row['county'] = county_code
            
            # Tank type determination
            place = safe_string(row.get('PLACE', ''))
            type_desc = safe_string(row.get('TYPE DESC', ''))
            
            if 'UNDERGROUND' in place.upper():
                processed_row['ust_or_ast'] = 'UST'
            elif 'ABOVEGROUND' in place.upper():
                processed_row['ust_or_ast'] = 'AST'
            elif 'underground' in type_desc.lower():
                processed_row['ust_or_ast'] = 'UST'
            elif 'aboveground' in type_desc.lower():
                processed_row['ust_or_ast'] = 'AST'
            else:
                processed_row['ust_or_ast'] = 'UST'  # Default
            
            # Installation date - FIXED
            install_date = safe_string(row.get('INSTALL', ''))
            dates_processed += 1
            
            if install_date:
                processed_row['year_installed'] = format_date_for_output(install_date)
                processed_row['tank_install_year_only'] = parse_year_from_date(install_date)
                
                if processed_row['year_installed']:
                    dates_successful += 1
            else:
                processed_row['year_installed'] = ''
                processed_row['tank_install_year_only'] = ''
            
            # Tank size
            tank_size = safe_string(row.get('CAPACITY', ''))
            processed_row['tank_size__gallons_'] = safe_int(tank_size)
            processed_row['size_range'] = determine_size_range(tank_size)
            
            # Tank construction - ENHANCED
            processed_row['tank_construction'] = determine_tank_construction(row)
            
            # Other fields
            processed_row['piping_construction'] = ''
            processed_row['tank_construction_rating'] = ''
            processed_row['secondary_containment__ast_'] = ''
            
            # Content
            content_code = safe_string(row.get('CONTENT', ''))
            content_desc = safe_string(row.get('CONTDESC', ''))
            processed_row['content_description'] = content_desc if content_desc else content_code
            
            # Tank tightness
            tvi = safe_string(row.get('TVI', ''))
            processed_row['tank_tightness'] = 'Yes' if tvi.upper() == 'TANK' else ''
            
            # Tank status
            tank_status_code = safe_string(row.get('TKSTAT', ''))
            processed_row['tank_status'] = FLORIDA_TANK_STATUS_MAPPING.get(tank_status_code, tank_status_code)
            
            # LUST info
            processed_row['lust'] = 'No'
            processed_row['lust_status'] = ''
            processed_row['last_synch_date'] = datetime.now().strftime('%Y/%m/%d')
            
            processed_rows.append(processed_row)
        
        print(f"  Date processing: {dates_successful}/{dates_processed} successful")
        
        result_df = pd.DataFrame(processed_rows)
        print(f"  ✓ Processed {len(result_df)} records")
        return result_df
        
    except Exception as e:
        print(f"  ✗ Error processing file: {e}")
        return pd.DataFrame()

def process_all_florida_data():
    """Process all Florida county files"""
    print(f"=== Starting Florida Data Processing ===\n")
    
    if not os.path.exists(INPUT_PATH):
        print(f"Error: Input folder not found at {INPUT_PATH}")
        return
    
    files = [f for f in os.listdir(INPUT_PATH) if f.endswith('.xls')]
    
    if not files:
        print("No .xls files found in input folder")
        return
    
    print(f"Found {len(files)} county files to process")
    
    all_data_frames = []
    
    for i, file in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] Processing: {file}")
        file_path = os.path.join(INPUT_PATH, file)
        county_df = process_florida_county_file(file_path)
        
        if not county_df.empty:
            all_data_frames.append(county_df)
    
    if not all_data_frames:
        print("No data frames to combine!")
        return
    
    print(f"\nCombining data from {len(all_data_frames)} county files...")
    combined_df = pd.concat(all_data_frames, ignore_index=True)
    
    # Column order (same as Texas)
    column_order = [
        'state', 'state_name', 'facility_id', 'tank_id', 'tank_location',
        'city', 'zip', 'ust_or_ast', 'year_installed', 'tank_install_year_only',
        'tank_size__gallons_', 'size_range', 'tank_construction', 'piping_construction',
        'secondary_containment__ast_', 'content_description', 'tank_tightness',
        'facility_name', 'lust', 'tank_construction_rating', 'county',
        'tank_status', 'lust_status', 'last_synch_date'
    ]
    
    combined_df = combined_df[column_order]
    
    # Save formatted data
    initial_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Formatted.xlsx')
    combined_df.to_excel(initial_output, index=False)
    print(f"✓ Saved formatted data to: {initial_output}")
    
    # Process EPA LUST data
    print("\n=== Processing EPA LUST Data ===")
    try:
        epa_lust_path = os.path.join(BASE_PATH, "L-UST_Data", "Output", "EPA_LUST_Data_Raw_20250715_120457.csv")
        
        if os.path.exists(epa_lust_path):
            print(f"Reading EPA LUST data...")
            epa_lust_df = pd.read_csv(epa_lust_path)
            
            fl_lust = epa_lust_df[epa_lust_df['state'].str.upper() == STATE_ABBR.upper()]
            
            if len(fl_lust) > 0:
                print(f"Found {len(fl_lust)} LUST records for {STATE_NAME}")
                
                fl_lust.to_csv(os.path.join(REQUIRED_PATH, f'{STATE_NAME}_EPA_LustData.csv'), index=False)
                
                matches_found = 0
                total_records = len(combined_df)
                
                for index, row in combined_df.iterrows():
                    if index % 1000 == 0:
                        print(f"  Processed {index}/{total_records} records...")
                    
                    lust_status = find_address_match(row['tank_location'], row['state_name'], fl_lust)
                    
                    if lust_status:
                        combined_df.at[index, 'lust'] = 'Yes'
                        combined_df.at[index, 'lust_status'] = lust_status
                        matches_found += 1
                
                print(f'✓ Found {matches_found} LUST matches')
                
                # Show sample matches
                if matches_found > 0:
                    print("\nSample of LUST matches:")
                    lust_matches = combined_df[combined_df['lust'] == 'Yes'].head(3)
                    for _, match in lust_matches.iterrows():
                        print(f"  Facility: {match['facility_name'][:50]}...")
                        print(f"  Address: {match['tank_location'][:50]}...")
                        print(f"  Status: {match['lust_status']}")
                        print()
                
            else:
                print(f'No LUST records found for {STATE_NAME}')
                
        else:
            print(f'EPA LUST data file not found')
            
    except Exception as e:
        print(f'Error processing EPA LUST data: {e}')
    
    # Save final data
    print("\n=== Saving Final Data ===")
    final_output_xlsx = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
    final_output_csv = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.csv')
    
    combined_df.to_excel(final_output_xlsx, index=False)
    combined_df.to_csv(final_output_csv, index=False)
    
    # Print summary
    print(f"\n=== Summary Statistics ===")
    print(f"Total records: {len(combined_df)}")
    print(f"Total counties: {combined_df['county'].nunique()}")
    print(f"Total facilities: {combined_df['facility_id'].nunique()}")
    print(f"UST tanks: {(combined_df['ust_or_ast'] == 'UST').sum()}")
    print(f"AST tanks: {(combined_df['ust_or_ast'] == 'AST').sum()}")
    print(f"LUST sites: {(combined_df['lust'] == 'Yes').sum()}")
    print(f"Records with installation dates: {len(combined_df[combined_df['year_installed'] != ''])}")
    
    # Show county breakdown
    print(f"\nRecords by county (top 10):")
    county_counts = combined_df['county'].value_counts().head(10)
    for county, count in county_counts.items():
        if county:  # Only show non-empty counties
            print(f"  {county}: {count}")
    
    # Show installation year breakdown
    year_counts = combined_df[combined_df['tank_install_year_only'] != '']['tank_install_year_only'].value_counts().head(10)
    if len(year_counts) > 0:
        print(f"\nInstallation years (top 10):")
        for year, count in year_counts.items():
            print(f"  {year}: {count}")
    
    # Show tank construction breakdown
    construction_counts = combined_df['tank_construction'].value_counts().head(10)
    if len(construction_counts) > 0:
        print(f"\nTank construction types:")
        for construction, count in construction_counts.items():
            if construction:
                print(f"  {construction}: {count}")
    
    # Show LUST status breakdown
    if (combined_df['lust'] == 'Yes').sum() > 0:
        print(f"\nLUST status breakdown:")
        lust_status_counts = combined_df[combined_df['lust'] == 'Yes']['lust_status'].value_counts()
        for status, count in lust_status_counts.items():
            print(f"  {status}: {count}")
    
    print(f"\n✅ Florida data processing completed!")
    print(f"Final Excel file: {final_output_xlsx}")
    print(f"Final CSV file: {final_output_csv}")

if __name__ == "__main__":
    print("Florida Data Processing Script")
    print("=" * 50)
    process_all_florida_data()