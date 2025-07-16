import requests
import pandas as pd
import time
import os
from datetime import datetime
import numpy as np

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
LUST_PATH = os.path.join(BASE_PATH, "L-UST_Data")
OUTPUT_PATH = os.path.join(LUST_PATH, "Output")

# Create directories explicitly
os.makedirs(OUTPUT_PATH, exist_ok=True)

# EPA API URL clearly set
LUST_URL = "https://services.arcgis.com/cJ9YHowT8TU7DUyn/arcgis/rest/services/UST_Finder_Feature_Layer_2/FeatureServer/1/query"

# Explicit column mapping
LUST_COLUMN_MAPPING = {
    'Facility_ID': 'facility_id',
    'LUST_ID': 'lust_id',
    'Name': 'site_name',
    'Address': 'site_address',
    'City': 'city',
    'County': 'county',
    'Zip_Code': 'zip',
    'State': 'state',
    'Latitude': 'latitude',
    'Longitude': 'longitude',
    'Reported_Date': 'reported_date',
    'Status': 'status',
    'Substance': 'substance',
    'Population_within_1500ft': 'population_within_1500ft',
    'DomesticWells_within_1500ft': 'domestic_wells_within_1500ft',
    'LandUse': 'land_use',
    'Within_SPA': 'within_spa',
    'SPA_PWS_FacilityID': 'spa_pws_facility_id',
    'Within_WHPA': 'within_whpa',
    'WHPA_PWS_FacilityID': 'whpa_pws_facility_id',
    'Within_100yr_Floodplain': 'within_100yr_floodplain',
    'Tribe': 'tribe',
    'EPA_Region': 'epa_region',
    'NFA_Letter_1': 'nfa_letter_1',
    'NFA_Letter_2': 'nfa_letter_2',
    'NFA_Letter_3': 'nfa_letter_3',
    'NFA_Letter_4': 'nfa_letter_4',
    'Closed_With_Residual_Contaminat': 'closed_with_residual_contamination'
}

def fetch_epa_lust_data():
    print("="*60)
    print("EPA LUST DATA FETCHER")
    print("="*60)

    batch_size, offset, all_records = 2000, 0, []
    while True:
        params = {
            'where': '1=1', 'outFields': '*', 'f': 'json',
            'resultRecordCount': batch_size, 'resultOffset': offset
        }
        try:
            response = requests.get(LUST_URL, params=params)
            response.raise_for_status()
            data = response.json()
            features = data.get('features', [])
            if not features: break
            records = [f['attributes'] for f in features]
            all_records.extend(records)
            print(f"✓ Fetched {len(records)} records at offset {offset}")
            offset += batch_size
            time.sleep(0.2)
        except Exception as e:
            print(f"✗ Error fetching at offset {offset}: {e}")
            break

    print(f"\n✓ Total LUST records fetched: {len(all_records)}")
    return all_records

def process_lust_data(records):
    print("\nProcessing LUST data...")

    df = pd.DataFrame(records)
    rename_dict = {k:v for k,v in LUST_COLUMN_MAPPING.items() if k in df.columns}
    df.rename(columns=rename_dict, inplace=True)

    # Convert dates explicitly
    if 'reported_date'in df.columns:
        df['reported_date']=pd.to_datetime(df['reported_date'], unit='ms', errors='coerce')

    # Status analysis explicitly
    if 'status'in df.columns:
        df['status']=df['status'].astype(str)
        df['is_active']=df['status'].str.contains('Active|Open|Ongoing',case=False,na=False)

    if 'zip'in df.columns:
        df['zip']=df['zip'].astype(str).str[:5]

    # Add metadata explicitly
    df['data_source']='EPA_LUST'
    df['fetch_date']=datetime.now()

    if 'reported_date'in df.columns:
        df['days_since_reported']=(datetime.now()-df['reported_date']).dt.days

    if all(x in df.columns for x in ['state','facility_id','lust_id']):
        df=df.sort_values(['state','facility_id','lust_id'])

    # ✅ Explicit Illegal Character Removal (IMPORTANT FIX) ✅
    def remove_illegal_chars(text):
        if pd.isna(text):
            return text
        return ''.join(c for c in str(text) if c.isprintable() and ord(c)>=32)
    for col in df.select_dtypes(include=['object']).columns:
        df[col]=df[col].apply(remove_illegal_chars)

    print(f"✓ Processed {len(df)} LUST records")
    return df

def save_lust_data(df):
    timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")

    raw_path=os.path.join(OUTPUT_PATH,f"EPA_LUST_Data_Raw_{timestamp}.csv")
    df.to_csv(raw_path,index=False)
    print(f"\n✓ Raw data saved: {raw_path}")

    excel_path=os.path.join(OUTPUT_PATH,f"EPA_LUST_Data_Formatted_{timestamp}.xlsx")

    cols=[c for c in [
        'state','facility_id','lust_id','site_name','site_address',
        'city','county','zip','latitude','longitude','status','is_active',
        'reported_date','days_since_reported','substance','population_within_1500ft',
        'domestic_wells_within_1500ft','land_use','within_spa','spa_pws_facility_id',
        'within_whpa','whpa_pws_facility_id','within_100yr_floodplain','tribe',
        'epa_region','closed_with_residual_contamination','nfa_letter_1','nfa_letter_2',
        'nfa_letter_3','nfa_letter_4','data_source','fetch_date'
    ]if c in df.columns]

    with pd.ExcelWriter(excel_path,engine="openpyxl") as writer:
        df[cols].to_excel(writer,sheet_name='LUST_Data',index=False)

        summary=pd.DataFrame({
            'Metric':["Total LUST Sites","Total States","Active LUST Sites"],
            'Count':[len(df),df['state'].nunique(),df['is_active'].sum()]
        })
        summary.to_excel(writer,sheet_name='Summary',index=False)

    print(f"✓ Formatted data saved: {excel_path}")

    final_combined_path=os.path.join(OUTPUT_PATH,f"EPA_LUST_Data_Final_{timestamp}.xlsx")
    df[cols].to_excel(final_combined_path,index=False)
    print(f"✓ Final combined excel saved: {final_combined_path}")

    return final_combined_path

def create_lust_summary():
    summary_file=os.path.join(OUTPUT_PATH,f"LUST_Data_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(summary_file,'w') as f:
        f.write("EPA LUST DATA FETCH SUMMARY\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write("="*60+"\n\nData Source: EPA LUST API\n")
        f.write(f"Output Directory: {OUTPUT_PATH}\n")
    print(f"✓ Summary created: {summary_file}")

def main():
    try:
        records=fetch_epa_lust_data()
        if not records:
            print("\n✗ No data fetched!")
            return
        df=process_lust_data(records)
        save_lust_data(df)
        create_lust_summary()
        print("\n"+"="*60+"\nLUST DATA FETCH COMPLETE!\n"+"="*60)
        print(f"Total LUST Sites: {len(df)}")
        print(f"States covered: {df['state'].nunique() if 'state'in df.columns else'unknown'}")
    except Exception as e:
        print("\n✗ Main Error:",e)
        import traceback
        traceback.print_exc()

if __name__=="__main__":
    main()