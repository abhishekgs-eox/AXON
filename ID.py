from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime

BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Idaho"
STATE_ABBR = "ID"
URL = "https://www2.deq.idaho.gov/waste/ustlust/pages/PublicReports.aspx"

STATE_PATH = os.path.join(BASE_PATH, "states", STATE_NAME)
INPUT_PATH = os.path.join(STATE_PATH, "Input")
OUTPUT_PATH = os.path.join(STATE_PATH, "Output")
DOWNLOAD_PATH = INPUT_PATH

def setup_folder_structure():
    for path in [BASE_PATH, STATE_PATH, INPUT_PATH, OUTPUT_PATH]:
        os.makedirs(path, exist_ok=True)

def safe_string(value):
    return '' if pd.isna(value) else str(value).strip()

def safe_int(value):
    try:
        return int(float(value))
    except:
        return 0

def map_ust_ast(facility_type):
    ast_types = {
        'farm', 'federal military', 'marina', 'aircraft owner',
        'air taxi (airline)', 'petroleum distributor', 'utilities', 'cardlock'
    }
    return 'AST' if facility_type.strip().lower() in ast_types else 'UST'

def download_idaho_data():
    files_to_download = [
        "Active UST Facilities (Excel)",
        "Closed UST Facilities (Excel)",
        "All UST Facilities (Excel)",
        "LUST Events (Excel)"
    ]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, downloads_path=DOWNLOAD_PATH)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.goto(URL)
        page.wait_for_load_state('load')
        time.sleep(5)

        for file_text in files_to_download:
            print(f"Downloading: {file_text}")
            try:
                with page.expect_download(timeout=60000) as download_info:
                    page.click(f"text={file_text}")
                download = download_info.value
                filename = file_text.replace(" ", "_").replace("(", "").replace(")", "") + '.xlsx'
                download.save_as(os.path.join(DOWNLOAD_PATH, filename))
                print(f"Successfully downloaded: {filename}")
            except Exception as e:
                print(f"Error downloading {file_text}: {e}")
            time.sleep(2)
        browser.close()

def find_header_row(df, expected):
    for idx in range(20):
        if all(any(expected_term.lower() in str(val).lower() for val in df.iloc[idx]) for expected_term in expected):
            return idx
    return None

def process_idaho_file(file_path):
    df_initial = pd.read_excel(file_path, header=None)
    header_row = find_header_row(df_initial, ['Facility ID', 'Type', 'Facility Name', 'Street Address', 'City', 'Zip'])
    if header_row is None:
        print("Headers not detected!")
        return pd.DataFrame()

    df = pd.read_excel(file_path, header=header_row).fillna('')
    rows = []

    for _, row in df.iterrows():
        facility_type = safe_string(row.get('Type', ''))
        ust_or_ast = map_ust_ast(facility_type)
        num_tanks_col = next((col for col in df.columns if 'tanks' in col.lower()), None)
        num_tanks = safe_int(row[num_tanks_col]) if num_tanks_col else 1
        for tank_num in range(1, num_tanks + 1):
            rows.append({
                'state': STATE_ABBR, 'state_name': STATE_NAME,
                'facility_id': safe_string(row.get('Facility ID')),
                'tank_id': str(tank_num),
                'tank_location': safe_string(row.get('Street Address', '')),
                'city': safe_string(row.get('City', '')),
                'zip': safe_string(row.get('Zip', ''))[:5],
                'county': '', 'ust_or_ast': ust_or_ast,
                'year_installed': '', 'tank_install_year_only': '',
                'tank_size__gallons_': 0, 'size_range': '',
                'tank_construction': '', 'piping_construction': '',
                'secondary_containment__ast_': '', 'content_description': '',
                'tank_tightness': '', 'facility_name': safe_string(row.get('Facility Name')),
                'tank_status': 'Active' if 'active' in file_path.lower() else 'Closed' if 'closed' in file_path.lower() else 'Unknown',
                'lust': '', 'lust_status': '',
                'tank_construction_rating': '',
                'last_synch_date': datetime.now().strftime('%Y/%m/%d')
            })
    return pd.DataFrame(rows)

def process_idaho_data():
    all_data = []
    for file in os.listdir(INPUT_PATH):
        if file.endswith('.xlsx'):
            print(f"Processing {file}")
            df = process_idaho_file(os.path.join(INPUT_PATH, file))
            if not df.empty:
                all_data.append(df)
    if all_data:
        final_df = pd.concat(all_data).drop_duplicates(['facility_id', 'tank_id'])
        final_df.to_excel(os.path.join(OUTPUT_PATH, f'{STATE_NAME}_UST_AST_Processed.xlsx'), index=False)
        final_df.to_csv(os.path.join(OUTPUT_PATH, f'{STATE_NAME}_UST_AST_Processed.csv'), index=False)
        print("Data processing complete, saved outputs.")
    else:
        print("No usable data processed.")

def main():
    setup_folder_structure()
    download_idaho_data()
    process_idaho_data()

if __name__ == "__main__":
    main()