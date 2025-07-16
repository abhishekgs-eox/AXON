import os
import time
import shutil
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright

# Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "North Dakota"
STATE_ABBR = "ND"
URL = "https://deq.nd.gov/FOIA/UST-LUST-DataExport/UST-Tank-Download.aspx"
STATE_PATH = os.path.join(BASE_PATH, "states", STATE_NAME)
INPUT_PATH = os.path.join(STATE_PATH, "Input")
OUTPUT_PATH = os.path.join(STATE_PATH, "Output")
REQUIRED_PATH = os.path.join(STATE_PATH, "Required")
FINAL_ELASTIC_PATH = r'D:\Axon python scripts\Elastic\Final Outputs'

for folder in [INPUT_PATH, OUTPUT_PATH, REQUIRED_PATH, FINAL_ELASTIC_PATH]:
    os.makedirs(folder, exist_ok=True)

def setup_folder_structure():
    log_path = os.path.join(STATE_PATH, "logs")
    os.makedirs(log_path, exist_ok=True)
    return os.path.join(log_path, f"{STATE_NAME}_log_{datetime.now():%Y%m%d_%H%M%S}.log")

def download_north_dakota_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, downloads_path=INPUT_PATH)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.goto(URL, wait_until='networkidle', timeout=120000)
        time.sleep(5)

        selector = 'text="Export UST tank data to excel"'

        with page.expect_download(timeout=120000) as download_info:
            page.click(selector)
            print("Clicked Export, waiting...")
        download = download_info.value
        filename = f"{STATE_NAME}_UST_Tank_Data.xlsx"
        download.save_as(os.path.join(INPUT_PATH, filename))
        print(f"Downloaded file: {filename}")
        browser.close()

def read_file(filepath):
    try:
        return pd.read_excel(filepath)
    except:
        try:
            return pd.read_csv(filepath)
        except Exception as e:
            print(f"Error: {e}")
    return None

def safe_str(val):
    return '' if pd.isna(val) else str(val).strip()

def safe_int(val):
    try:
        return int(float(val))
    except:
        return 0

def determine_size_range(size):
    if size <=5000: return '0-5000'
    if size <=10000: return '5001-10000'
    if size <=15000: return '10001-15000'
    if size <=20000: return '15001-20000'
    return '20000+'

def process_north_dakota_data():
    files = [f for f in os.listdir(INPUT_PATH) if f.endswith(('xls', 'xlsx', 'csv'))]
    if not files: print("No input file found."); return
    df_raw = read_file(os.path.join(INPUT_PATH, files[0]))
    if df_raw is None: print("Failed to read file"); return
    
    processed_rows = []
    for _, r in df_raw.iterrows():
        row = {
            'state': STATE_ABBR,
            'state_name': STATE_NAME,
            'facility_id': safe_str(r.get('FacilityID')),
            'facility_name': safe_str(r.get('facName')),
            'tank_id': safe_str(r.get('tnkNumber')),
            'tank_location': f"{safe_str(r.get('facAddress'))} {safe_str(r.get('facAddress2'))}".strip(),
            'city': safe_str(r.get('facCity')),
            'zip': safe_str(r.get('facZip'))[:5],
            'county': safe_str(r.get('facCounty')),
            'ust_or_ast': 'AST' if safe_str(r.get('tnkAST')).upper() == 'TRUE' else 'UST',
            'year_installed': pd.to_datetime(r.get('tnkDateInstalled'), errors='coerce').strftime('%Y/%m/%d') if pd.notna(r.get('tnkDateInstalled')) else '',
            'tank_install_year_only': pd.to_datetime(r.get('tnkDateInstalled'), errors='coerce').year if pd.notna(r.get('tnkDateInstalled')) else '',
            'tank_size__gallons_': safe_int(r.get('tnkTotalCapacity')),
            'size_range': determine_size_range(safe_int(r.get('tnkTotalCapacity'))),
            'tank_construction': safe_str(r.get('tnkMaterial')),
            'piping_construction': safe_str(r.get('tcoPipeMaterial')),
            'tank_construction_rating': '',
            'secondary_containment__ast_': 'Yes' if safe_str(r.get('tnkInterstitialDoubleWalled')).upper()=='TRUE' or safe_str(r.get('tnkInterstitialSecondContain')).upper()=='TRUE' else '',
            'content_description': safe_str(r.get('tcoSubstance')),
            'tank_tightness': 'Yes' if safe_str(r.get('tcoTightnessTesting')).upper()=='TRUE' else 'No',
            'tank_status': safe_str(r.get('tnkStatus')),
            'lust': 'No',
            'lust_status': '',
            'last_synch_date': datetime.now().strftime('%Y/%m/%d')
        }
        processed_rows.append(row)
    
    df_processed = pd.DataFrame(processed_rows)
    output_file = os.path.join(OUTPUT_PATH, f"{STATE_NAME}_Formatted.xlsx")
    df_processed.to_excel(output_file, index=False)
    print(f"Saved: {output_file}")
    
    final_path = os.path.join(FINAL_ELASTIC_PATH, f"{STATE_NAME}_Final_Formatted.xlsx")
    shutil.copy(output_file, final_path)
    print(f"Copied to Final Outputs: {final_path}")

def main():
    print("="*70,"\nNorth Dakota UST Data Download & Processing\n","="*70)
    setup_folder_structure()
    download_north_dakota_data()
    process_north_dakota_data()
    print("\nCompleted Successfully!\n","="*70)

if __name__ == "__main__":
    main()