import pandas as pd
import json
import os
import logging
from tqdm import tqdm
from datetime import datetime

# ======= CONFIGURATION =======
BATCH_SIZE = 5000
INPUT_DIR = r"D:\Axon python scripts\Output\CO\states\Colorado\Output"
LOG_FOLDER = r"D:\Axon python scripts\Elastic\logs"

STATIC_FIELDS = {
    "org_id": 26,
    "account_id": 26
}

excel_columns = [
    "state", "state_name", "facility_id", "tank_id", "tank_location", "city", "zip", "ust_or_ast",
    "year_installed", "tank_install_year_only", "tank_size__gallons_", "size_range", "tank_construction",
    "piping_construction", "secondary_containment__ast_", "content_description", "tank_tightness",
    "facility_name", "lust", "tank_construction_rating", "county", "tank_status", "lust_status", "last_synch_date"
]

os.makedirs(LOG_FOLDER, exist_ok=True)
log_file = os.path.join(LOG_FOLDER, "excel_to_json.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def clean_year_installed(val, doc_id):
    original = val
    if not val or pd.isna(val) or str(val).strip() == "":
        return ""
    for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y.%m.%d", "%Y"):
        try:
            dt = datetime.strptime(str(val).strip(), fmt)
            return dt.strftime("%Y/%m/%d")
        except Exception:
            continue
    if str(val).strip().isdigit() and len(str(val).strip()) == 4:
        return f"{val}/01/01"
    logging.warning(f"[ROW id={doc_id}] Could not parse year_installed value '{original}', leaving as is.")
    return str(val)

def clean_year_only(val, ref_full_date, doc_id):
    original = val
    if val and str(val).strip().isdigit() and len(str(val).strip()) == 4:
        return str(val).strip()
    try:
        if ref_full_date and isinstance(ref_full_date, str) and len(ref_full_date) >= 4:
            year = datetime.strptime(ref_full_date, "%Y/%m/%d").year
            return str(year)
    except Exception:
        pass
    if original:
        logging.warning(f"[ROW id={doc_id}] Could not parse tank_install_year_only value '{original}', leaving empty.")
    return ""

def build_doc(row, doc_id):
    doc = STATIC_FIELDS.copy()
    for col in excel_columns:
        doc[col] = row.get(col, "")
    cleaned_year_inst = clean_year_installed(row.get("year_installed", ""), doc_id)
    doc["year_installed"] = cleaned_year_inst
    doc["tank_install_year_only"] = clean_year_only(row.get("tank_install_year_only", ""), cleaned_year_inst, doc_id)
    doc['id'] = doc_id
    return doc, cleaned_year_inst

def iso8601(val):
    try:
        if val and len(val) == 10:
            dt = datetime.strptime(val, "%Y/%m/%d")
            return dt.strftime("%Y-%m-%dT00:00:00.000Z")
    except Exception:
        pass
    return None

def excel_to_json_batches(file_path, export_folder, start_id):
    df = pd.read_excel(file_path, dtype=str).fillna('')
    total_docs = len(df)
    file_name = os.path.basename(file_path)
    logging.info(f"Processing file '{file_name}' with {total_docs} records starting id={start_id}")
    batch_number = 1
    for batch_start in tqdm(range(0, total_docs, BATCH_SIZE), desc=f"Exporting {file_name}"):
        batch_df = df.iloc[batch_start:batch_start+BATCH_SIZE]
        json_batch = []
        for idx, (_, row) in enumerate(batch_df.iterrows()):
            doc_id = start_id + batch_start + idx
            _source, year_inst = build_doc(row, doc_id)
            # Build output JSON object as per requirements
            out = {
                "_index": "eos_axon_tankstorage_index",
                "_type": "_doc",
                "_id": str(doc_id),
                "_version": 1,
                "_score": 0,
                "_source": _source,
                "fields": {}
            }
            iso_val = iso8601(year_inst)
            if iso_val:
                out["fields"]["year_installed"] = [iso_val]
            else:
                out["fields"] = {}
            json_batch.append(out)
        export_file = os.path.join(export_folder, f'{file_name}_batch_{batch_number}.json')
        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(json_batch, f, indent=4)
        logging.info(f"Exported batch {batch_number} to '{export_file}'")
        batch_number += 1

if __name__ == "__main__":
    print("----- Excel to JSON Export Begin -----")
    start_id = 1
    files = [f for f in os.listdir(INPUT_DIR)
             if f.lower().endswith('.xlsx') and not f.startswith('~$')]
    for file in files:
        file_path = os.path.join(INPUT_DIR, file)
        export_folder = os.path.join(INPUT_DIR, "json_exports")
        os.makedirs(export_folder, exist_ok=True)
        excel_to_json_batches(file_path, export_folder, start_id)
        with pd.ExcelFile(file_path) as xls:
            n_rows = pd.read_excel(xls, dtype=str).shape[0]
        start_id += n_rows
    print("----- Finished! JSON exported to corresponding folders. -----")
    print(f"See log file (date corrections, warnings): {log_file}")