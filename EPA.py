from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os
from datetime import datetime
import numpy as np

# Base Configuration
BASE_PATH = r"D:\Axon python scripts\Output"
URL = "https://epa.maps.arcgis.com/apps/webappviewer/index.html?id=b03763d3f2754461adf86f121345d7bc"

# List of states to process
STATES_TO_PROCESS = [
    "Arkansas", "California", "Missouri", "Iowa", "Kansas", "Louisiana",
    "Maryland", "Nevada", "New Hampshire", "New Mexico", "North Carolina",
    "Oklahoma", "Oregon", "Utah"
]

# State abbreviations mapping
STATE_ABBR_MAP = {
    "Arkansas": "AR", "California": "CA", "Missouri": "MO", "Iowa": "IA",
    "Kansas": "KS", "Louisiana": "LA", "Maryland": "MD", "Nevada": "NV",
    "New Hampshire": "NH", "New Mexico": "NM", "North Carolina": "NC",
    "Oklahoma": "OK", "Oregon": "OR", "Utah": "UT"
}

def setup_folder_structure(state_name):
    """Create all necessary folders for the state"""
    STATE_PATH = os.path.join(BASE_PATH, "states", state_name)
    folders = [
        BASE_PATH,
        os.path.join(BASE_PATH, "states"),
        STATE_PATH,
        os.path.join(STATE_PATH, "Input"),
        os.path.join(STATE_PATH, "Output"),
        os.path.join(STATE_PATH, "Required"),
        os.path.join(BASE_PATH, "L-UST_Data")
    ]
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    return STATE_PATH

def download_state_data(page, state_name, download_path):
    """Download data for a specific state"""
    try:
        print(f"\n--- Processing {state_name} ---")
        
        # Click on Options in the attribute table
        print("Looking for Options button...")
        options_selectors = [
            'div[title="Options"]',
            'span:has-text("Options")',
            '.jimu-widget-attributetable-options',
            '//div[@title="Options"]',
            'div.jimu-btn[title="Options"]'
        ]
        
        options_clicked = False
        for selector in options_selectors:
            try:
                if selector.startswith('//'):
                    element = page.locator(f'xpath={selector}')
                else:
                    element = page.locator(selector).first
                
                if element.is_visible():
                    element.click()
                    print("✓ Clicked Options")
                    options_clicked = True
                    time.sleep(2)
                    break
            except:
                continue
        
        if not options_clicked:
            print("✗ Could not find Options button")
            return False
        
        # Click on Filter
        print("Looking for Filter option...")
        filter_selectors = [
            'div[title="Filter"]',
            'td:has-text("Filter")',
            '//div[contains(text(), "Filter")]',
            '//td[contains(text(), "Filter")]',
            '.jimu-popup-menu-item:has-text("Filter")'
        ]
        
        filter_clicked = False
        for selector in filter_selectors:
            try:
                if selector.startswith('//'):
                    element = page.locator(f'xpath={selector}')
                else:
                    element = page.locator(selector).first
                
                if element.is_visible():
                    element.click()
                    print("✓ Clicked Filter")
                    filter_clicked = True
                    time.sleep(3)
                    break
            except:
                continue
        
        if not filter_clicked:
            print("✗ Could not find Filter option")
            return False
        
        # Click "Add expression" button in the filter dialog
        print("Looking for 'Add expression' button...")
        add_expr_selectors = [
            'a:has-text("Add expression")',
            'span:has-text("Add expression")',
            'div:has-text("Add expression")',
            '//a[contains(text(), "Add expression")]',
            '.jimu-link:has-text("Add expression")',
            'a.jimu-link[data-dojo-attach-point="btnAddExpr"]'
        ]
        
        add_expr_clicked = False
        for selector in add_expr_selectors:
            try:
                if selector.startswith('//'):
                    element = page.locator(f'xpath={selector}')
                else:
                    element = page.locator(selector).first
                
                if element.is_visible():
                    element.click()
                    print("✓ Clicked 'Add expression'")
                    add_expr_clicked = True
                    time.sleep(2)
                    break
            except:
                continue
        
        if not add_expr_clicked:
            print("✗ Could not find 'Add expression' button")
            return False
        
        # Now set up the filter expression
        print(f"Setting up filter for {state_name}...")
        
        # Step 1: Select "State (String)" from the first dropdown
        print("Selecting 'State (String)' from field dropdown...")
        
        # First, click on the dropdown to open it
        try:
            # Find the first dropdown (field selector)
            first_dropdown = page.locator('td.dijitReset.dijitStretch.dijitButtonContents').first
            first_dropdown.click()
            time.sleep(1)
            
            # Now click on "State (String)" option
            state_option = page.locator('td:has-text("State (String)")').first
            if state_option.is_visible():
                state_option.click()
                print("✓ Selected 'State (String)'")
                time.sleep(1)
            else:
                # Try alternative selector
                state_option = page.locator('div:has-text("State (String)")').first
                state_option.click()
                print("✓ Selected 'State (String)'")
                time.sleep(1)
        except:
            # Fallback: try using select element directly
            try:
                select_element = page.locator('select').first
                select_element.select_option(label="State (String)")
                print("✓ Selected 'State (String)' using select")
                time.sleep(1)
            except Exception as e:
                print(f"Error selecting State field: {e}")
                return False
        
        # Step 2: The operator "is" should already be selected, but verify
        # Usually the second dropdown defaults to "is"
        
        # Step 3: Enter the state name in the VALUE field (third field)
        print(f"Entering state name: {state_name}")
        
        try:
            # Find all input fields and select the appropriate one
            # The value field is typically the third input or the last visible input
            input_fields = page.locator('input[type="text"]').all()
            
            # Try to find the value input field (usually after the operator dropdown)
            value_input = None
            for i, field in enumerate(input_fields):
                if field.is_visible() and field.is_enabled():
                    # Check if this is likely the value field
                    # It should be empty and editable
                    try:
                        field_value = field.get_attribute('value')
                        field_readonly = field.get_attribute('readonly')
                        
                        # The value field should be empty and not readonly
                        if (not field_value or field_value == '') and not field_readonly:
                            value_input = field
                            break
                    except:
                        continue
            
            if not value_input:
                # Fallback: try the last visible input
                for field in reversed(input_fields):
                    if field.is_visible() and field.is_enabled():
                        value_input = field
                        break
            
            if value_input:
                value_input.click()
                value_input.fill(state_name)
                print(f"✓ Entered state name: {state_name}")
                time.sleep(1)
            else:
                print("✗ Could not find value input field")
                return False
                
        except Exception as e:
            print(f"Error entering state name: {e}")
            # Try alternative approach
            try:
                # Sometimes the value field has a specific class
                value_input = page.locator('.dijitInputInner').last
                value_input.click()
                value_input.fill(state_name)
                print(f"✓ Entered state name: {state_name} (alternative method)")
                time.sleep(1)
            except:
                return False
        
        # Click OK to apply the filter
        print("Applying filter...")
        ok_button = page.locator('div.jimu-btn:has-text("OK")').first
        if ok_button.is_visible():
            ok_button.click()
            print("✓ Clicked OK to apply filter")
            time.sleep(5)  # Wait for data to filter
        else:
            print("✗ Could not find OK button")
            return False
        
        # Click Options again to export
        print("Opening Options menu for export...")
        for selector in options_selectors:
            try:
                if selector.startswith('//'):
                    element = page.locator(f'xpath={selector}')
                else:
                    element = page.locator(selector).first
                
                if element.is_visible():
                    element.click()
                    time.sleep(2)
                    break
            except:
                continue
        
        # Click Export to CSV
        print("Looking for Export to CSV option...")
        export_selectors = [
            'div[title="Export to CSV"]',
            'td:has-text("Export to CSV")',
            '//div[contains(text(), "Export to CSV")]',
            '//td[contains(text(), "Export to CSV")]',
            '.jimu-popup-menu-item:has-text("Export to CSV")'
        ]
        
        export_clicked = False
        for selector in export_selectors:
            try:
                if selector.startswith('//'):
                    element = page.locator(f'xpath={selector}')
                else:
                    element = page.locator(selector).first
                
                if element.is_visible():
                    # Prepare for download
                    with page.expect_download(timeout=60000) as download_info:
                        element.click()
                        print("✓ Clicked Export to CSV")
                        time.sleep(2)
                        
                        # Handle confirmation popup
                        confirm_ok = page.locator('button:has-text("OK")').first
                        if confirm_ok.is_visible():
                            confirm_ok.click()
                            print("✓ Confirmed export")
                    
                    download = download_info.value
                    filename = f"{state_name}_EPA_UST_Data.csv"
                    file_path = os.path.join(download_path, filename)
                    download.save_as(file_path)
                    print(f"✓ Downloaded: {filename}")
                    export_clicked = True
                    break
            except Exception as e:
                print(f"Export error: {e}")
                continue
        
        # Clear the filter for next state
        print("Clearing filter for next state...")
        # Click Options again
        for selector in options_selectors:
            try:
                if selector.startswith('//'):
                    element = page.locator(f'xpath={selector}')
                else:
                    element = page.locator(selector).first
                
                if element.is_visible():
                    element.click()
                    time.sleep(2)
                    break
            except:
                continue
        
        # Click Filter again
        for selector in filter_selectors:
            try:
                if selector.startswith('//'):
                    element = page.locator(f'xpath={selector}')
                else:
                    element = page.locator(selector).first
                
                if element.is_visible():
                    element.click()
                    time.sleep(2)
                    break
            except:
                continue
        
        # Try to clear or remove the filter
        try:
            # Look for the X button to remove the filter
            remove_filter = page.locator('div.filter-item div.close').first
            if remove_filter.is_visible():
                remove_filter.click()
                time.sleep(1)
                print("✓ Removed filter")
            
            # Click OK or Cancel to close filter dialog
            ok_or_cancel = page.locator('div.jimu-btn:has-text("OK"), div.jimu-btn:has-text("Cancel")').first
            if ok_or_cancel.is_visible():
                ok_or_cancel.click()
                time.sleep(2)
        except:
            pass
        
        return export_clicked
        
    except Exception as e:
        print(f"Error processing {state_name}: {e}")
        import traceback
        traceback.print_exc()
        return False
    
def download_all_states_data():
    """Download UST data for all specified states from EPA ArcGIS"""
    results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            downloads_path=os.path.join(BASE_PATH, "temp_downloads")
        )
        
        context = browser.new_context(
            accept_downloads=True,
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        try:
            print(f"Navigating to {URL}")
            page.goto(URL, wait_until='networkidle', timeout=120000)
            print("Waiting for page to fully load...")
            time.sleep(15)  # Give map time to fully load
            
            # Click on Attribute Table icon
            print("\nLooking for Attribute Table icon...")
            attr_table_selectors = [
                'div[title="Attribute Table"]',
                'img[title="Attribute Table"]',
                '//div[@title="Attribute Table"]',
                '.jimu-widget-attributetable',
                'div.jimu-widget-onscreen-icon img[src*="AttributeTable"]',
                'div.icon-node:has(img[title="Attribute Table"])'
            ]
            
            attr_table_clicked = False
            for selector in attr_table_selectors:
                try:
                    if selector.startswith('//'):
                        element = page.locator(f'xpath={selector}')
                    else:
                        element = page.locator(selector).first
                    
                    if element.is_visible():
                        element.click()
                        print("✓ Clicked Attribute Table")
                        attr_table_clicked = True
                        time.sleep(5)  # Wait for table to load
                        break
                except:
                    continue
            
            if not attr_table_clicked:
                print("✗ Could not find Attribute Table icon")
                # Take screenshot for debugging
                screenshot_path = os.path.join(BASE_PATH, "epa_debug.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Screenshot saved to: {screenshot_path}")
                return results
            
            # Process each state
            for state_name in STATES_TO_PROCESS:
                STATE_PATH = setup_folder_structure(state_name)
                DOWNLOAD_PATH = os.path.join(STATE_PATH, "Input")
                
                success = download_state_data(page, state_name, DOWNLOAD_PATH)
                results[state_name] = success
                
                # Wait between states
                time.sleep(3)
                
        except Exception as e:
            print(f"Error during download process: {e}")
            import traceback
            traceback.print_exc()
        
        browser.close()
        
    return results

def determine_size_range(tank_size):
    """Determine size range based on tank size in gallons"""
    if pd.isna(tank_size) or tank_size == '':
        return ''
    
    try:
        size = float(tank_size)
        if size <= 5000:
            return "0-5000"
        elif size <= 10000:
            return "5001-10000"
        elif size <= 15000:
            return "10001-15000"
        elif size <= 20000:
            return "15001-20000"
        else:
            return "20000+"
    except:
        return ''

def safe_string(value):
    """Safely convert value to string, handling NaN and None"""
    if pd.isna(value) or value is None:
        return ''
    return str(value).strip()

def safe_int(value):
    """Safely convert value to integer, handling NaN and None"""
    if pd.isna(value) or value is None or value == '':
        return 0
    try:
        return int(float(value))
    except:
        return 0

def process_state_data(state_name):
    """Process downloaded EPA data for a specific state"""
    STATE_PATH = os.path.join(BASE_PATH, "states", state_name)
    INPUT_PATH = os.path.join(STATE_PATH, "Input")
    OUTPUT_PATH = os.path.join(STATE_PATH, "Output")
    REQUIRED_PATH = os.path.join(STATE_PATH, "Required")
    
    csv_file = os.path.join(INPUT_PATH, f"{state_name}_EPA_UST_Data.csv")
    
    if not os.path.exists(csv_file):
        print(f"CSV file not found for {state_name}: {csv_file}")
        return None
    
    try:
        # Read CSV file
        df_raw = pd.read_csv(csv_file, low_memory=False)
        print(f"\nProcessing {state_name}: {len(df_raw)} records")
        
        # Save raw data for debugging
        debug_file = os.path.join(REQUIRED_PATH, f"{state_name}_EPA_Raw_Debug.xlsx")
        df_raw.to_excel(debug_file, index=False)
        
        processed_rows = []
        
        for idx, row in df_raw.iterrows():
            processed_row = {}
            
            # State information
            processed_row['state'] = state_name
            processed_row['state_name'] = STATE_ABBR_MAP.get(state_name, '')
            
            # Map EPA columns
            processed_row['facility_id'] = safe_string(row.get('Facility ID', ''))
            processed_row['tank_id'] = ''  # Not available in EPA data
            processed_row['tank_location'] = safe_string(row.get('Address', ''))
            processed_row['city'] = safe_string(row.get('City', ''))
            processed_row['zip'] = safe_string(row.get('Zip Code', ''))[:5]
            processed_row['county'] = safe_string(row.get('County', ''))
            
            # Tank type - all UST
            processed_row['ust_or_ast'] = 'UST'
            
            # Installation date - not available
            processed_row['year_installed'] = ''
            processed_row['tank_install_year_only'] = ''
            
            # Tank size - not available
            processed_row['tank_size__gallons_'] = 0
            processed_row['size_range'] = ''
            
            # Construction details - not available
            processed_row['tank_construction'] = ''
            processed_row['piping_construction'] = ''
            processed_row['tank_construction_rating'] = ''
            
            # Secondary containment - not available
            processed_row['secondary_containment__ast_'] = ''
            
            # Content/Product - not available
            processed_row['content_description'] = ''
            
            # Tank tightness - not available
            processed_row['tank_tightness'] = ''
            
            # Facility name
            processed_row['facility_name'] = safe_string(row.get('Name', ''))
            
            # Tank status - derive from Open/Closed USTs
            open_usts = safe_int(row.get('Open USTs', 0))
            closed_usts = safe_int(row.get('Closed USTs', 0))
            temp_out = safe_int(row.get('Temporarily Out of Service USTs', 0))
            
            if open_usts > 0:
                processed_row['tank_status'] = 'Active'
            elif temp_out > 0:
                processed_row['tank_status'] = 'Temporarily Out of Service'
            elif closed_usts > 0:
                processed_row['tank_status'] = 'Closed'
            else:
                processed_row['tank_status'] = safe_string(row.get('Facility Status', ''))
            
            # LUST information - not directly available
            processed_row['lust'] = 'No'
            processed_row['lust_status'] = ''
            
            # Last synch date
            processed_row['last_synch_date'] = datetime.now().strftime('%Y/%m/%d')
            
            # Create multiple rows based on tank counts
            total_tanks = open_usts + closed_usts + temp_out
            if total_tanks == 0:
                total_tanks = 1  # At least one record per facility
            
            for tank_num in range(1, total_tanks + 1):
                tank_row = processed_row.copy()
                tank_row['tank_id'] = str(tank_num)
                processed_rows.append(tank_row)
        
        formatted_df = pd.DataFrame(processed_rows)
        
        # Ensure all columns are in the correct order
        column_order = [
            'state', 'state_name', 'facility_id', 'tank_id', 'tank_location',
            'city', 'zip', 'ust_or_ast', 'year_installed', 'tank_install_year_only',
            'tank_size__gallons_', 'size_range', 'tank_construction', 'piping_construction',
            'secondary_containment__ast_', 'content_description', 'tank_tightness',
            'facility_name', 'lust', 'tank_construction_rating', 'county',
            'tank_status', 'lust_status', 'last_synch_date'
        ]
        
        formatted_df = formatted_df[column_order]
        
        # Save formatted data
        output_file = os.path.join(OUTPUT_PATH, f'{state_name}_EPA_Formatted.xlsx')
        formatted_df.to_excel(output_file, index=False)
        print(f"✓ Saved formatted data to: {output_file}")
        
        # Also save as CSV
        csv_output = os.path.join(OUTPUT_PATH, f'{state_name}_EPA_Formatted.csv')
        formatted_df.to_csv(csv_output, index=False)
        
        # Show summary
        print(f"  Total facilities: {df_raw['Facility ID'].nunique()}")
        print(f"  Total tank records created: {len(formatted_df)}")
        print(f"  Counties: {formatted_df['county'].nunique()}")
        
        return formatted_df
        
    except Exception as e:
        print(f"Error processing {state_name} data: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function to orchestrate the entire process"""
    print(f"{'='*60}")
    print(f"Starting EPA UST Data Download for Multiple States")
    print(f"{'='*60}")
    print(f"Base path: {BASE_PATH}")
    print(f"Target URL: {URL}")
    print(f"\nStates to process: {', '.join(STATES_TO_PROCESS)}")
    
    # Download data for all states
    print(f"\n=== Downloading data from EPA ArcGIS ===\n")
    results = download_all_states_data()
    
    # Show download results
    print(f"\n=== Download Results ===")
    successful = [state for state, success in results.items() if success]
    failed = [state for state, success in results.items() if not success]
    
    if successful:
        print(f"\n✓ Successfully downloaded data for {len(successful)} states:")
        for state in successful:
            print(f"  - {state}")
    
    if failed:
        print(f"\n✗ Failed to download data for {len(failed)} states:")
        for state in failed:
            print(f"  - {state}")
    
    # Process downloaded data
    print(f"\n=== Processing Downloaded Data ===")
    for state in successful:
        process_state_data(state)
    
    print(f"\n{'='*60}")
    print(f'EPA data processing completed!')
    print(f"{'='*60}")

if __name__ == "__main__":
    main()