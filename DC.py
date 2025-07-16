import os
import shutil
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# ✅ DOWNLOAD SETTINGS ✅
download_dir = r'D:\Axon python scripts\Output'
final_output_dir = r'D:\Axon python scripts\Elastic\Final Outputs'
state_output_dir = r'D:\Axon python scripts\Output\states\DC'

# Create folders explicitly if they don't exist
os.makedirs(download_dir, exist_ok=True)
os.makedirs(final_output_dir, exist_ok=True)
os.makedirs(state_output_dir, exist_ok=True)

# Chrome options setup
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "plugins.always_open_pdf_externally": True,
    "safebrowsing.enabled": True
})

# ✅ INITIALIZE SELENIUM (Browser automation) ✅
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("https://ust-doee.dc.gov/Pages/PublicReports.aspx")
time.sleep(10)

# Enable Excel File download via click automatically
links = driver.find_elements(By.TAG_NAME, 'a')
clicked = False
for link in links:
    if "All Tanks with All Data" in link.text:
        link.find_element(By.XPATH, "./following::a[contains(text(),'Excel')]").click()
        clicked = True
        print("✅ Excel Download successfully clicked.")
        break

if not clicked:
    driver.quit()
    raise Exception("⚠️ Excel download link not clicked.")

# Waiting for the file to download clearly
time.sleep(30)
driver.quit()

# Retrieve path of recent downloaded Excel file
downloaded_file = max(
    [os.path.join(download_dir, f) for f in os.listdir(download_dir) if f.endswith('.xlsx')],
    key=os.path.getctime
)
print("✅ Downloaded Excel file path:", downloaded_file)

# ✅ Explicit header detection dynamically ✅
temp_df = pd.read_excel(downloaded_file, header=None, engine='openpyxl')
required_column = 'Facility Id'

HEADER_ROW_IDX = None
for idx, row in temp_df.iterrows():
    if required_column in row.values:
        HEADER_ROW_IDX = idx
        break

if HEADER_ROW_IDX is None:
    raise Exception("⚠️ Could not auto-detect header row!")

print("✅ Header row detected dynamically at:", HEADER_ROW_IDX)

# Load data with correct header
original_df = pd.read_excel(downloaded_file, header=HEADER_ROW_IDX, engine='openpyxl')
print("✅ Successfully loaded Excel columns:", original_df.columns.tolist())

# Mapping explicitly as requested
mapped_df = pd.DataFrame({
    'state': 'DC',
    'state_name': 'District of Columbia',
    'facility_id': original_df['Facility Id'],
    'tank_id': original_df['TANKID'],
    'tank_location': original_df['Street Address'],
    'city': 'Washington',
    'zip': original_df['Zip'],
    'ust_or_ast': original_df['AST FLG'].apply(lambda x: 'AST' if str(x).upper() == 'TRUE' else 'UST'),
    'year_installed': pd.to_datetime(original_df['INSTALLED DATE'], errors='coerce').dt.strftime('%Y/%m/%d'),
})

# More columns explicitly mapped
mapped_df['tank_install_year_only'] = pd.to_datetime(mapped_df['year_installed'], errors='coerce').dt.year
mapped_df['tank_size__gallons_'] = pd.to_numeric(original_df['TANKCAPACITY'], errors='coerce').fillna(0).astype(int)

# ✅ Explicit Custom Size Range Logic ✅
def size_range_calc(size):
    if size <= 5000:
        return "0-5000"
    elif size <= 10000:
        return "5001-10000"
    elif size <= 15000:
        return "10001-15000"
    elif size <= 20000:
        return "15001-20000"
    elif size <= 25000:
        return "20001-25000"
    elif size <= 50000:
        return "25001-50000"
    elif size <= 100000:
        return "50001-100000"
    elif size <= 200000:
        return "100001-200000"
    elif size <= 500000:
        return "200001-500000"
    else:
        return "Above 500000"

mapped_df['size_range'] = mapped_df['tank_size__gallons_'].apply(size_range_calc)

mapped_df['tank_construction'] = original_df['TANKMAT']
mapped_df['piping_construction'] = original_df['PIPEMAT']
mapped_df['secondary_containment__ast_'] = original_df['TANKSECCONTAINMENT']
mapped_df['content_description'] = original_df['SUBSTANCE']
mapped_df['tank_tightness'] = original_df['SPILLTIGHTNESSTEST DATE'].apply(lambda x: 'Yes' if pd.notnull(x) else 'No')
mapped_df['facility_name'] = original_df['Facility Name']
mapped_df['lust'] = original_df['LEAKDETECTED FLG'].apply(lambda x: 'Yes' if str(x).upper() == 'TRUE' else 'No')
mapped_df['tank_construction_rating'] = ''
mapped_df['county'] = ''
mapped_df['tank_status'] = original_df['TANKSTATUS']
mapped_df['lust_status'] = original_df['LEAKDETECTED FLG'].apply(lambda x: 'Leak Detected' if str(x).upper() == 'TRUE' else 'No Leak Detected')

# ✅ Format Synch Date explicitly ✅
mapped_df['last_synch_date'] = datetime.now().strftime('%m/%d/%Y')

# ✅ Explicitly set filename clearly ✅  
final_filename = "DC_final_formatted.xlsx"

# Save Excel explicitly to "states\DC" path explicitly asked by you:
final_output_path = os.path.join(state_output_dir, final_filename)
mapped_df.to_excel(final_output_path, index=False)
print(f"\n🎉 Clearly mapped data saved at:\n{final_output_path}")

# ✅ Explicitly copy Excel to Final path ✅
final_copy_path = os.path.join(final_output_dir, final_filename)
shutil.copy(final_output_path, final_copy_path)
print(f"🎉 Explicitly copied Excel to:\n{final_copy_path}")

# ✅ Cleaning temporary original downloaded Excel✅
os.remove(downloaded_file)
print("✅ Successfully removed temporary downloaded file.")