import json
import os
import pandas as pd
from elasticsearch import Elasticsearch

# Elasticsearch credentials
ES_HOST = "13.52.224.89"
ES_PORT = 9200
ES_USER = "elastic"
ES_PASS = "Acce$$ElastiC7747/"
ES_INDEX = "eos_axon_tankstorage_index"

# Paths
response_json_path = r"D:\Axon python scripts\Documentation\History data scripts\response_history.json"
output_excel_path = r"D:\Axon python scripts\Documentation\History data scripts\output_history.xlsx"

# Initialize Elasticsearch client
es = Elasticsearch(
    host=ES_HOST,
    port=ES_PORT,
    http_auth=(ES_USER, ES_PASS),
    scheme="http"
)

# Your aggregation query (same as your existing code)
aggs_query = {
  "size": 0,
  "aggs": {
    "states": {
      "terms": {
        "field": "state.keyword",
        "size": 50
      },
      "aggs": {
        "facility_count": { "cardinality": { "field": "facility_id.keyword" }},
        "tank_count": { "cardinality": { "field": "tank_id.keyword" }},
        "city_count": { "cardinality": { "field": "city.keyword" }},
        "zip_count": { "cardinality": { "field": "zip.keyword" }},
        "ust_or_ast_count": { "cardinality": { "field": "ust_or_ast.keyword" }},
        "tank_install_years": { "cardinality": { "field": "tank_install_year_only.keyword" }},
        "tank_size_stats": { "stats": { "field": "tank_size__gallons_" }},
        "size_range_terms": { "terms": { "field": "size_range.keyword", "size": 10 }},
        "tank_construction_terms": { "terms": { "field": "tank_construction.keyword", "size": 10 }},
        "piping_construction_terms": { "terms": { "field": "piping_construction.keyword", "size": 10 }},
        "secondary_containment_terms": { "terms": { "field": "secondary_containment__ast_.keyword", "size": 5 }},
        "content_description_terms": { "terms": { "field": "content_description.keyword", "size": 10 }},
        "facility_name_count": { "cardinality": { "field": "facility_name.keyword" }},
        "tank_status_terms": { "terms": { "field": "tank_status.keyword", "size": 10 }},
        "lust_terms": { "terms": { "field": "lust.keyword", "size": 10 }},
        "tank_construction_rating_terms": { "terms": { "field": "tank_construction_rating.keyword", "size": 10 }},
        "county_count": { "cardinality": { "field": "county.keyword" }},
        "lust_status_terms": { "terms": { "field": "lust_status.keyword", "size": 10 }},
        "last_synch_date_min": { "min": { "field": "last_synch_date" }},
        "last_synch_date_max": { "max": { "field": "last_synch_date" }}
      }
    }
  }
}

# Execute query
response = es.search(index=ES_INDEX, body=aggs_query)

# Save JSON response
with open(response_json_path, "w", encoding="utf-8") as f:
    json.dump(response, f, ensure_ascii=False, indent=2)

print(f"Response saved to {response_json_path}")

# Load the response JSON
with open(response_json_path, "r", encoding="utf-8") as f:
    es_data = json.load(f)

# Prepare your data rows
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
        'Top Size Range': (state.get('size_range_terms', {}).get('buckets', [{}])[0].get('key', '') 
                           if state.get('size_range_terms', {}).get('buckets') else ''),
        'Top Size Range Count': (state.get('size_range_terms', {}).get('buckets', [{}])[0].get('doc_count', '') 
                                     if state.get('size_range_terms', {}).get('buckets') else ''),
        'Top Tank Status': (state.get('tank_status_terms', {}).get('buckets', [{}])[0].get('key', '') 
                            if state.get('tank_status_terms', {}).get('buckets') else ''),
        'Top Tank Status Count': (state.get('tank_status_terms', {}).get('buckets', [{}])[0].get('doc_count', '') 
                                      if state.get('tank_status_terms', {}).get('buckets') else ''),
        'Top Construction': (state.get('tank_construction_terms', {}).get('buckets', [{}])[0].get('key', '') 
                             if state.get('tank_construction_terms', {}).get('buckets') else ''),
        'Top Construction Count': (state.get('tank_construction_terms', {}).get('buckets', [{}])[0].get('doc_count', '') 
                                       if state.get('tank_construction_terms', {}).get('buckets') else ''),
        'Top Content': (state.get('content_description_terms', {}).get('buckets', [{}])[0].get('key', '') 
                        if state.get('content_description_terms', {}).get('buckets') else ''),
        'Top Content Count': (state.get('content_description_terms', {}).get('buckets', [{}])[0].get('doc_count', '') 
                              if state.get('content_description_terms', {}).get('buckets') else ''),
        'Top Piping Construction': (state.get('piping_construction_terms', {}).get('buckets', [{}])[0].get('key', '') 
                                    if state.get('piping_construction_terms', {}).get('buckets') else ''),
        'Top Piping Const Count': (state.get('piping_construction_terms', {}).get('buckets', [{}])[0].get('doc_count', '') 
                                       if state.get('piping_construction_terms', {}).get('buckets') else ''),
        'Top Lust Term': (state.get('lust_terms', {}).get('buckets', [{}])[0].get('key', '') 
                          if state.get('lust_terms', {}).get('buckets') else ''),
        'Top Lust Count': (state.get('lust_terms', {}).get('buckets', [{}])[0].get('doc_count', '') 
                            if state.get('lust_terms', {}).get('buckets') else ''),
        'County Count': state.get('county_count', {}).get('value', ''),
        'Last Sync Min': state.get('last_synch_date_min', {}).get('value_as_string', ''),
        'Last Sync Max': state.get('last_synch_date_max', {}).get('value_as_string', ''),
    }
    rows.append(row)

# Save to Excel
df = pd.DataFrame(rows)
os.makedirs(os.path.dirname(output_excel_path), exist_ok=True)
df.to_excel(output_excel_path, index=False)
print(f"Output saved to {output_excel_path}")