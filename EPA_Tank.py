import requests
import pandas as pd
import time
import os
from datetime import datetime
import numpy as np

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output\EPA"
EPA_PATH = os.path.join(BASE_PATH, "EPA_Data")
OUTPUT_PATH = os.path.join(EPA_PATH, "Output")

# Create directories if they don't exist
os.makedirs(OUTPUT_PATH, exist_ok=True)

# EPA API Configuration
TANK_URL = "https://services.arcgis.com/cJ9YHowT8TU7DUyn/arcgis/rest/services/UST_Finder_Feature_Layer_2/FeatureServer/4/query"

# States to download (specified states only)
STATES_TO_DOWNLOAD = [
    "Arkansas", "California", "Idaho", "Illinois", "Iowa", "Kansas",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Missouri", "Montana", "Nevada", "New Hampshire", "New Mexico",
    "North Carolina", "Oklahoma", "Oregon", "Rhode Island", 
    "South Carolina", "South Dakota", "Utah", "Vermont", "Virginia"
]

# Standard column mapping to match your format
TANK_COLUMN_MAPPING = {
    'RegistryID': 'facility_id',
    'TankID': 'tank_id',
    'State': 'state',
    'TankStatus': 'tank_status',
    'TankUse': 'tank_use',
    'TankSize': 'tank_size__gallons_',
    'TankConstruction': 'tank_construction',
    'YearInstalled': 'year_installed',
    'YearClosed': 'year_closed',
    'PipingConstruction': 'piping_construction',
    'ContentsStored': 'content_description',
    'TankType': 'ust_or_ast',
    'LeakDetection': 'leak_detection',
    'OverfillProtection': 'overfill_protection',
    'SpillProtection': 'spill_protection',
    'LastInspection': 'last_inspection',
    'InspectionDue': 'inspection_due',
    'Compartments': 'compartments',
    'CertifiedInstaller': 'certified_installer',
    'SecondaryContainment': 'secondary_containment',
    'EmergencyShutoff': 'emergency_shutoff'
}

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

def fetch_epa_tank_data():
    """Fetch all EPA tank data for specified states"""
    print("="*60)
    print("EPA TANK DATA FETCHER")
    print("="*60)
    print(f"Output Path: {OUTPUT_PATH}")
    print(f"States to fetch: {len(STATES_TO_DOWNLOAD)}")
    print("\nFetching EPA tank data...")
    
    # Build where clause for states
    states_str = "', '".join(STATES_TO_DOWNLOAD)
    where_clause = f"State IN ('{states_str}')"
    
    # Pagination parameters
    batch_size = 2000
    offset = 0
    all_records = []
    
    while True:
        params = {
            'where': where_clause,
            'outFields': '*',
            'f': 'json',
            'resultRecordCount': batch_size,
            'resultOffset': offset
        }
        
        try:
            response = requests.get(TANK_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            features = data.get('features', [])
            if not features:
                break
            
            records = [f['attributes'] for f in features]
            all_records.extend(records)
            
            print(f"✓ Fetched {len(records)} records at offset {offset}")
            offset += batch_size
            
            # Be polite to the server
            time.sleep(0.2)
            
        except Exception as e:
            print(f"✗ Error fetching data at offset {offset}: {e}")
            break
    
    print(f"\n✓ Total tank records fetched: {len(all_records)}")
    return all_records

def process_tank_data(records):
    """Process and standardize tank data"""
    print("\nProcessing tank data...")
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Rename columns to match standard format
    rename_dict = {k: v for k, v in TANK_COLUMN_MAPPING.items() if k in df.columns}
    df = df.rename(columns=rename_dict)
    
    # Add missing standard columns
    for col in TANK_COLUMN_MAPPING.values():
        if col not in df.columns:
            df[col] = np.nan
    
    # Process tank type
    if 'ust_or_ast' in df.columns:
        df['ust_or_ast'] = df['ust_or_ast'].fillna('UST')  # Default to UST if not specified
    else:
        df['ust_or_ast'] = 'UST'  # EPA data is primarily UST
    
    # Add size range
    if 'tank_size__gallons_' in df.columns:
        df['tank_size__gallons_'] = pd.to_numeric(df['tank_size__gallons_'], errors='coerce')
        df['size_range'] = df['tank_size__gallons_'].apply(get_size_range)
    
    # Convert date fields
    date_columns = ['year_installed', 'year_closed', 'last_inspection', 'inspection_due']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Extract year only for installation
    if 'year_installed' in df.columns:
        df['tank_install_year_only'] = df['year_installed'].dt.year.astype('Int64').astype(str)
        df['tank_install_year_only'] = df['tank_install_year_only'].replace('nan', '')
    
    # Add tank construction rating
    construction_ratings = {
        'Fiberglass': 'A',
        'Steel with Cathodic Protection': 'A',
        'Double Wall': 'A',
        'Composite': 'A',
        'Steel': 'B',
        'Bare Steel': 'C',
        'Unknown': 'Unknown'
    }
    
    if 'tank_construction' in df.columns:
        df['tank_construction_rating'] = df['tank_construction'].map(construction_ratings).fillna('Unknown')
    
    # Add metadata
    df['data_source'] = 'EPA'
    df['fetch_date'] = datetime.now()
    df['county'] = ''  # EPA data might not have county
    
    # Sort by state and facility_id
    if 'state' in df.columns and 'facility_id' in df.columns:
        df = df.sort_values(['state', 'facility_id', 'tank_id'])
    
    print(f"✓ Processed {len(df)} tank records")
    return df

def save_tank_data(df):
    """Save processed tank data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save raw data
    raw_file = os.path.join(OUTPUT_PATH, f"EPA_Tank_Data_Raw_{timestamp}.csv")
    df.to_csv(raw_file, index=False)
    print(f"\n✓ Saved raw data: {raw_file}")
    
    # Save formatted Excel file
    excel_file = os.path.join(OUTPUT_PATH, f"EPA_Tank_Data_Formatted_{timestamp}.xlsx")
    
    # Select columns in your standard order
    standard_columns = [
        'state', 'facility_id', 'tank_id', 'facility_name', 'facility_address',
        'city', 'zip', 'county', 'ust_or_ast', 'tank_status', 'tank_use',
        'tank_size__gallons_', 'size_range', 'tank_construction', 'tank_construction_rating',
        'year_installed', 'tank_install_year_only', 'year_closed', 
        'piping_construction', 'content_description', 'leak_detection',
        'overfill_protection', 'spill_protection', 'secondary_containment',
        'last_inspection', 'inspection_due', 'data_source', 'fetch_date'
    ]
    
    # Only include columns that exist
    columns_to_save = [col for col in standard_columns if col in df.columns]
    df_to_save = df[columns_to_save]
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df_to_save.to_excel(writer, sheet_name='Tanks', index=False)
        
        # Add summary sheet
        summary_data = {
            'Metric': ['Total Tanks', 'Total States', 'Active Tanks', 'Closed Tanks',
                      'UST Count', 'AST Count', 'Unknown Size Count'],
            'Count': [
                len(df),
                df['state'].nunique() if 'state' in df.columns else 0,
                (df['tank_status'] == 'Active').sum() if 'tank_status' in df.columns else 0,
                (df['tank_status'] == 'Closed').sum() if 'tank_status' in df.columns else 0,
                (df['ust_or_ast'] == 'UST').sum() if 'ust_or_ast' in df.columns else 0,
                (df['ust_or_ast'] == 'AST').sum() if 'ust_or_ast' in df.columns else 0,
                (df['size_range'] == 'Unknown').sum() if 'size_range' in df.columns else 0
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Add state breakdown
        if 'state' in df.columns:
            state_summary = df.groupby('state').agg({
                'tank_id': 'count',
                'tank_status': lambda x: (x == 'Active').sum(),
                'ust_or_ast': lambda x: (x == 'UST').sum()
            }).rename(columns={
                'tank_id': 'total_tanks',
                'tank_status': 'active_tanks',
                'ust_or_ast': 'ust_count'
            })
            state_summary.to_excel(writer, sheet_name='State_Summary')
    
    print(f"✓ Saved formatted data: {excel_file}")
    
    # Save combined format (similar to your state data format)
    combined_file = os.path.join(OUTPUT_PATH, f"EPA_Tank_Data_Final_Formatted_{timestamp}.xlsx")
    df_to_save.to_excel(combined_file, index=False)
    print(f"✓ Saved final formatted data: {combined_file}")
    
    return combined_file

def create_epa_summary():
    """Create a summary report for EPA data"""
    summary_file = os.path.join(OUTPUT_PATH, f"EPA_Data_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    with open(summary_file, 'w') as f:
        f.write("EPA DATA FETCH SUMMARY\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        f.write(f"Data Source: EPA UST Finder\n")
        f.write(f"States Included: {len(STATES_TO_DOWNLOAD)}\n")
        f.write(f"Output Directory: {OUTPUT_PATH}\n")
        f.write("\nStates List:\n")
        for state in sorted(STATES_TO_DOWNLOAD):
            f.write(f"  - {state}\n")
    
    print(f"\n✓ Created summary report: {summary_file}")

def main():
    """Main function"""
    try:
        # Fetch data
        records = fetch_epa_tank_data()
        
        if not records:
            print("\n✗ No data fetched!")
            return
        
        # Process data
        df = process_tank_data(records)
        
        # Save data
        output_file = save_tank_data(df)
        
        # Create summary
        create_epa_summary()
        
        # Summary
        print("\n" + "="*60)
        print("TANK DATA FETCH COMPLETE!")
        print("="*60)
        print(f"Total tanks: {len(df)}")
        if 'state' in df.columns:
            print(f"States covered: {df['state'].nunique()}")
            
            # Show state breakdown
            state_counts = df['state'].value_counts().head(10)
            print("\nTop 10 states by tank count:")
            for state, count in state_counts.items():
                print(f"  {state}: {count:,}")
        
        print(f"\nOutput saved to: {OUTPUT_PATH}")
        
    except Exception as e:
        print(f"\n✗ Error in main process: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()