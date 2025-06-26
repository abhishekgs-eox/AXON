import json
import os
import pandas as pd

# Path to your Elastic result JSON
input_json_path = r"D:\Axon python scripts\Documentation\Current data scripts\response_current.json"
output_excel_path = r"D:\Axon python scripts\Documentation\Current data scripts\output_current.xlsx"

# Load JSON
with open(input_json_path, "r", encoding="utf-8") as f:
    es_data = json.load(f)

rows = []
for state in es_data['aggregations']['states']['buckets']:
    row = {
        'State': state['key'],
        'Facility Count': state.get('facility_count', {}).get('value', ''),
        'Tank Count': state.get('tank_count', {}).get('value', ''),
        'City Count': state.get('city_count', {}).get('value', ''),
        'Zip Count': state.get('zip_count', {}).get('value', ''),
        'UST/AST Types': state.get('ust_or_ast_count', {}).get('value', ''),
        'Install Years': state.get('tank_install_years', {}).get('value', ''),
        'Tank Size Min': state.get('tank_size_stats', {}).get('min', ''),
        'Tank Size Max': state.get('tank_size_stats', {}).get('max', ''),
        'Tank Size Avg': state.get('tank_size_stats', {}).get('avg', ''),
        'Top Size Range': state.get('size_range_terms', {}).get('buckets', [{}])[0].get('key', '') if state.get('size_range_terms', {}).get('buckets') else '',
        'Top Size Range Count': state.get('size_range_terms', {}).get('buckets', [{}])[0].get('doc_count', '') if state.get('size_range_terms', {}).get('buckets') else '',
        'Top Tank Status': state.get('tank_status_terms', {}).get('buckets', [{}])[0].get('key', '') if state.get('tank_status_terms', {}).get('buckets') else '',
        'Top Tank Status Count': state.get('tank_status_terms', {}).get('buckets', [{}])[0].get('doc_count', '') if state.get('tank_status_terms', {}).get('buckets') else '',
        'Top Construction': state.get('tank_construction_terms', {}).get('buckets', [{}])[0].get('key', '') if state.get('tank_construction_terms', {}).get('buckets') else '',
        'Top Construction Count': state.get('tank_construction_terms', {}).get('buckets', [{}])[0].get('doc_count', '') if state.get('tank_construction_terms', {}).get('buckets') else '',
        'Top Content': state.get('content_description_terms', {}).get('buckets', [{}])[0].get('key', '') if state.get('content_description_terms', {}).get('buckets') else '',
        'Top Content Count': state.get('content_description_terms', {}).get('buckets', [{}])[0].get('doc_count', '') if state.get('content_description_terms', {}).get('buckets') else '',
        'Top Piping Construction': state.get('piping_construction_terms', {}).get('buckets', [{}])[0].get('key', '') if state.get('piping_construction_terms', {}).get('buckets') else '',
        'Top Piping Const Count': state.get('piping_construction_terms', {}).get('buckets', [{}])[0].get('doc_count', '') if state.get('piping_construction_terms', {}).get('buckets') else '',
        'Top Lust Term': state.get('lust_terms', {}).get('buckets', [{}])[0].get('key', '') if state.get('lust_terms', {}).get('buckets') else '',
        'Top Lust Count': state.get('lust_terms', {}).get('buckets', [{}])[0].get('doc_count', '') if state.get('lust_terms', {}).get('buckets') else '',
        'County Count': state.get('county_count', {}).get('value', ''),
        'Last Sync Min': state.get('last_synch_date_min', {}).get('value_as_string', ''),
        'Last Sync Max': state.get('last_synch_date_max', {}).get('value_as_string', ''),
    }
    rows.append(row)

# Create DataFrame
df = pd.DataFrame(rows)

# Write to Excel
os.makedirs(os.path.dirname(output_excel_path), exist_ok=True)
df.to_excel(output_excel_path, index=False)
print(f"Excel file written to {output_excel_path}")