import requests
import csv
import math
import os
from datetime import datetime
from zipfile import ZipFile
import shutil
import logging
from sftp_upload_pysftp_1 import upload_to_sftp

# Logging configuration (change path as needed)
logging.basicConfig(filename='data_export.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Elasticsearch bulk API endpoint
endpoint = "http://13.52.224.89:9200"
# Elasticsearch username and password
username = "elastic"
password = "Acce$$ElastiC7747/"
# Elasticsearch index name
index_name = "eos_axon_tankstorage_index"

# Get unique states
agg_query = {
    "size": 0,
    "aggs": {
        "unique_state": {
            "terms": {
                "field": "state_name.keyword",
                "size": 10000  # Adjust size as necessary to include all unique values
            }
        }
    }
}

try:
    response = requests.get(f"{endpoint}/{index_name}/_search", json=agg_query, auth=(username, password))
except:
    logging.error(f"Failed to retrieve unique states: {response}")
    exit(1)
    
if response.status_code != 200:
    logging.error(f"Failed to retrieve unique states. Status code: {response.status_code}, Response: {response.text}")

states = [bucket['key'] for bucket in response.json()["aggregations"]["unique_state"]["buckets"]]

# Function to get total records for a state
def get_total_records(state):
    count_query = {
        "query": {
            "term": {
                "state_name.keyword": state
            }
        }
    }
    count_response = requests.get(f"{endpoint}/{index_name}/_count", json=count_query, auth=(username, password))
    return count_response.json()['count']

# Create directory for CSV files
output_dir = "output_csvs"
zip_dir = 'zip_files'
os.makedirs(output_dir, exist_ok=True)
os.makedirs(zip_dir, exist_ok=True)

# Iterate over each state
for state in states:
    total_records = get_total_records(state)
    logging.info(f"Processing state: {state}, Total records: {total_records}")

    # Initialize variables for batch processing
    size = 10000
    sort_val = None
    headers = None
    csv_file = os.path.join(output_dir, f"{state}.csv")
    
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = None
        
        for i in range(math.ceil(total_records / size)):
            query = {
                "size": size,
                "query": {
                    "term": {
                        "state_name.keyword": state
                    }
                },
                "sort": [{"id": "asc"}]
            }
            if sort_val:
                query["search_after"] = [sort_val]
                
            response = requests.get(f"{endpoint}/{index_name}/_search", json=query, auth=(username, password))
            
            if response.status_code != 200:
                logging.error(f"Failed to retrieve data for state {state}. Status code: {response.status_code}, Response: {response.text}")
            
            state_data = response.json()["hits"]["hits"]
            
            if state_data:
                if not headers:
                    headers = list(state_data[0]["_source"].keys())
                    writer = csv.DictWriter(file, fieldnames=headers)
                    writer.writeheader()
                
                for hit in state_data:
                    writer.writerow(hit["_source"])
                
                sort_val = state_data[-1]["sort"][0]
            else:
                break

# Create a ZIP file with all CSVs
zip_file_name = f"axon_tank_details_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
with ZipFile(zip_file_name, 'w') as zipf:
    for root, _, files in os.walk(output_dir):
        for file in files:
            zipf.write(os.path.join(root, file), arcname=file)
            
shutil.move(zip_file_name, zip_dir)

logging.info(f"Tank data exported and zipped in file: {zip_file_name}")

upload_to_sftp('zip_files','EOX_axon_tankstorage',zip_file_name)
logging.info(f"Uploaded to FTP: {zip_file_name}")
