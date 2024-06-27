# CostModelFileProcessingV1_1.py
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

table_lookup = {
    "chiller": {
        "lookup_text": 'Chiller:Electric:EIR',
        "field_name": 'Design Size Reference Capacity [W]',
        "value": ''
    },
    "airloopHVAC": {
        "lookup_text": 'AirLoopHVAC',
        "field_name": 'Adjusted Cooling Design Air Flow Rate [m3/s]',
        "value": ''
    },
    "coolingTower": {
        "lookup_text": 'CoolingTower:VariableSpeed',
        "field_name": 'Nominal Capacity [W]',
        "value": ''
    },
    "pump_flow": {
        "lookup_text": 'Pump:VariableSpeed',
        "field_name": 'Design Flow Rate [m3/s]',
        "value": ''
    },
    "pump_power": {
        "lookup_text": 'Pump:VariableSpeed',
        "field_name": 'Design Power Consumption [W]',
        "value": ''
    },
    "plantLoop": {
        "lookup_text": 'PlantLoop',
        "field_name": 'Plant Loop Volume [m3]',
        "value": ''
    }
}

def extract_value(df, key):
    lookup_text = table_lookup[key]["lookup_text"]
    field_name = table_lookup[key]["field_name"]
    filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(lookup_text).any(), axis=1)]

    if not filtered_df.empty:
        for index, row in filtered_df.iterrows():
            if field_name in row.values:
                field_index = row[row == field_name].index[0]
                if field_index + 1 < len(row):
                    value = row.iloc[field_index + 1]
                    table_lookup[key]["value"] = value  # Update table_lookup with the found value
                    return f"{field_name}: {value}"
    return None

def process_html_content(content):
    soup = BeautifulSoup(content, 'html.parser')
    tables = soup.find_all("table")

    for table in tables:
        table_html = str(table)
        df = pd.read_html(StringIO(table_html))[0]
        for key in table_lookup:
            extract_value(df, key)

    return {key: table_lookup[key]['value'] for key in table_lookup}
