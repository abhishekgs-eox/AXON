import pandas as pd
import os

# ==== File paths directly specified ====
current_file = r'D:\Axon python scripts\Documentation\Current data scripts\output_current.xlsx'
previous_file = r'D:\Axon python scripts\Documentation\History data scripts\output_history.xlsx'
output_file = r'D:\Axon python scripts\Documentation\diff_analysis.xlsx'

# ==== Load both DataFrames ====
df_current = pd.read_excel(current_file)
df_previous = pd.read_excel(previous_file)

# ==== Normalize 'State' columns: remove spaces and set to title case ====
df_current['State'] = df_current['State'].astype(str).str.strip().str.title()
df_previous['State'] = df_previous['State'].astype(str).str.strip().str.title()

# ==== Make sure 'State' column exists in both ====
assert 'State' in df_current.columns and 'State' in df_previous.columns, "Column 'State' required in both files"

# ==== Merge on 'State' (outer join keeps all states) ====
df_merged = pd.merge(
    df_current, df_previous, on='State',
    suffixes=('_Current', '_Previous'),
    how='outer', validate='one_to_one'
)

# ==== Calculate Differences for numeric columns ====
num_fields = [
    'Facility Count', 'Tank Count', 'City Count', 'Zip Count', 'UST/AST Types', 'Install Years',
    'Tank Size Min', 'Tank Size Max', 'Tank Size Avg',
    'Top Size Range Count', 'Top Tank Status Count', 'Top Construction Count', 'Top Content Count',
    'Top Piping Const Count', 'County Count', 'Top Lust Count'  # for LUST count
]

for field in num_fields:
    c_col = field + '_Current'
    p_col = field + '_Previous'
    diff_col = field + '_Diff'
    if c_col in df_merged.columns and p_col in df_merged.columns:
        # Convert to numeric
        df_merged[c_col] = pd.to_numeric(df_merged[c_col], errors='coerce')
        df_merged[p_col] = pd.to_numeric(df_merged[p_col], errors='coerce')
        df_merged[diff_col] = df_merged[c_col] - df_merged[p_col]

# ==== Check for changes in key text fields ====
text_fields = [
    'Top Size Range', 'Top Tank Status', 'Top Construction', 'Top Content',
    'Top Piping Construction', 'Top Lust Term'   # added for LUST term
]
for field in text_fields:
    c_col = field + '_Current'
    p_col = field + '_Previous'
    diff_col = field + '_Changed'
    if c_col in df_merged.columns and p_col in df_merged.columns:
        df_merged[diff_col] = df_merged[c_col] != df_merged[p_col]

# ==== Save the output ====
df_merged.to_excel(output_file, index=False)
print(f"Differential analysis saved to {output_file}")