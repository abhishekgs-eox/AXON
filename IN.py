import nest_asyncio
nest_asyncio.apply()

from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime
import shutil

# Base paths explicitly
BASE_PATH = r"D:\Axon python scripts\Output"
STATE_NAME = "Indiana"
STATE_ABBR = "IN"
URL = "https://www.in.gov/idem/tanks/resources/data-and-reports/"

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
    return os.path.join(log_path, f"{STATE_NAME}_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

def download_indiana_data():
    downloaded_files, retries = [], 3

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, downloads_path=INPUT_PATH)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        for attempt in range(1, retries+1):
            print(f"\nAttempt {attempt} to download IDEM data explicitly")
            
            try:
                page.goto(URL, wait_until='load', timeout=180000)
                time.sleep(5)

                # Explicit UST download
                print("Downloading UST file explicitly clearly...")
                with page.expect_download(timeout=180000) as dl_ust:
                    page.click('a[href*="records_branch_report_ust.xlsx"]')
                ust_file = dl_ust.value
                ust_filename = f"{STATE_NAME}_UST_Report.xlsx"
                ust_file.save_as(os.path.join(INPUT_PATH, ust_filename))
                downloaded_files.append(ust_filename)
                print(f"UST downloaded clearly: {ust_filename}")

                time.sleep(5)

                # Explicit LUST download
                print("Downloading LUST file explicitly clearly...")
                with page.expect_download(timeout=180000) as dl_lust:
                    page.click('a[href*="records_branch_report_lust.xlsx"]')
                lust_file = dl_lust.value
                lust_filename = f"{STATE_NAME}_LUST_Report.xlsx"
                lust_file.save_as(os.path.join(INPUT_PATH, lust_filename))
                downloaded_files.append(lust_filename)
                print(f"LUST downloaded clearly: {lust_filename}")

                break  

            except Exception as ex:
                print(f"Attempt {attempt} explicitly failed clearly: {ex}")
                if attempt==retries:
                    screenshot=os.path.join(STATE_PATH,"indiana_final_debug.png")
                    page.screenshot(path=screenshot,full_page=True)
                    print(f"Explicit screenshot saved for debugging: {screenshot}")
                else:
                    print("Retrying explicitly in 10 seconds...")
                    time.sleep(10)
        browser.close()
    return downloaded_files

def process_indiana_ust_data():
    ust_path=os.path.join(INPUT_PATH,f"{STATE_NAME}_UST_Report.xlsx")
    df=pd.read_excel(ust_path)

    processed=[]
    for _,r in df.iterrows():
        processed.append({
            "state":STATE_NAME,
            "state_name":STATE_ABBR,
            "facility_id":str(r.get('FID','')).strip(),
            "tank_id":str(r.get('TANK #','')).strip(),
            "facility_name":str(r.get('NAME','')).strip(),
            "tank_location":str(r.get('ADDRESS','')).strip(),
            "city":str(r.get('CITY','')).strip(),
            "zip":str(r.get('ZIP CODE',''))[:5].strip(),
            "county":str(r.get('COUNTY','')).strip(),
            "ust_or_ast":"UST",
            "year_installed":pd.to_datetime(r.get('INSTALL DATE'),errors='coerce').strftime('%Y/%m/%d') if pd.notna(r.get('INSTALL DATE')) else '',
            "tank_install_year_only":pd.to_datetime(r.get('INSTALL DATE'),errors='coerce').year if pd.notna(r.get('INSTALL DATE')) else '',
            "tank_size__gallons_":int(r.get('TANK CAPACITY',0)),
            "size_range":"<5000" if r.get('TANK CAPACITY',0)<5000 else ">5000",
            "tank_construction":"",
            "piping_construction":"",
            "secondary_containment__ast_":"",
            "content_description":str(r.get('SUBSTANCE','')).strip(),
            "tank_tightness":"",
            "tank_status":str(r.get('TANK STATUS','')).strip(),
            "tank_construction_rating":"",
            "lust":"No",
            "lust_status":"",
            "last_synch_date":datetime.now().strftime('%Y/%m/%d'),
        })

    formatted_df=pd.DataFrame(processed)
    output_file=os.path.join(OUTPUT_PATH,f"{STATE_NAME}_Formatted.xlsx")
    formatted_df.to_excel(output_file,index=False)
    print(f"Formatted Excel explicitly saved to: {output_file}")
    return formatted_df

def process_all_indiana_data():
    formatted_df=process_indiana_ust_data()

    final_output = os.path.join(OUTPUT_PATH, f'{STATE_NAME}_Final_Formatted.xlsx')
    formatted_df.to_excel(final_output,index=False)
    shutil.copy(final_output,FINAL_ELASTIC_PATH)
    print(f"\n✅ Explicitly copied FINAL data to: {FINAL_ELASTIC_PATH}")

def main():
    print(f"{'='*65}\nStarting Indiana UST/LUST Data Explicit Download & Processing...\n{'='*65}")
    setup_folder_structure()
    files=download_indiana_data()

    if files:
        print(f"\nExplicitly downloaded files clearly: {files}")
        process_all_indiana_data()
    else:
        print("Downloads explicitly failed. Check debugging screenshots clearly.")

    print(f"{'='*65}\nExplicitly Completed Complete Indiana Script!\n{'='*65}")

if __name__=="__main__":
    main()