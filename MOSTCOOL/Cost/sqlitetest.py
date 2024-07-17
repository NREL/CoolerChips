import sqlite3
import os

# Define the table lookup structure with ComponentSizes table and relevant lookup texts and descriptions
table_lookup = {
    "chiller": {
        "table": "ComponentSizes",
        "lookup_text": 'Chiller:Electric:EIR',
        "field_name": 'CompType',
        "description": 'Design Size Reference Chilled Water Flow Rate',
        "description_field": 'Description',
        "value": ''
    },
    "airloopHVAC": {
        "table": "ComponentSizes",
        "lookup_text": 'AirLoopHVAC',
        "field_name": 'CompType',
        "description": 'Sum of Air Terminal Maximum Heating Flow Rates',
        "description_field": 'Description',
        "value": ''
    },
    "coolingTower": {
        "table": "ComponentSizes",
        "lookup_text": 'CoolingTower:VariableSpeed',
        "field_name": 'CompType',
        "description": 'Design Water Flow Rate',
        "description_field": 'Description',
        "value": ''
    },
    "pump_flow": {
        "table": "ComponentSizes",
        "lookup_text": 'Pump:VariableSpeed',
        "field_name": 'CompType',
        "description": 'Design Flow Rate',
        "description_field": 'Description',
        "value": ''
    },
    "pump_power": {
        "table": "ComponentSizes",
        "lookup_text": 'Pump:VariableSpeed',
        "field_name": 'CompType',
        "description": 'Design Power Consumption',
        "description_field": 'Description',
        "value": ''
    },
    "plantLoop": {
        "table": "ComponentSizes",
        "lookup_text": 'PlantLoop',
        "field_name": 'CompType',
        "description": 'Maximum Loop Flow Rate',
        "description_field": 'Description',
        "value": ''
    }
}

def list_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(table[0])
        cursor.execute(f"PRAGMA table_info({table[0]});")
        columns = cursor.fetchall()
        print("Columns in", table[0], ":")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")

def extract_value_from_db(cursor, key):
    try:
        table = table_lookup[key]["table"]
        lookup_text = table_lookup[key]["lookup_text"]
        field_name = table_lookup[key]["field_name"]
        description = table_lookup[key]["description"]
        description_field = table_lookup[key]["description_field"]
        
        print(f"Processing key: {key}, lookup_text: {lookup_text}, field_name: {field_name}, description: {description}, description_field: {description_field}, table: {table}")
        
        # Perform the query to search for the lookup text and description in the specified fields
        cursor.execute(f"SELECT * FROM {table} WHERE {field_name} = ? AND {description_field} = ?", (lookup_text, description))
        rows = cursor.fetchall()
        
        if rows:
            for row in rows:
                print(f"Matching row for {key}: {row}")
                # Extract the value from the appropriate field
                value_index = [description[0] for description in cursor.description].index('Value')
                value = row[value_index]
                print(f"Found value for {key}: {value}")
                table_lookup[key]["value"] = value
                return value
        else:
            print(f"No matching rows found for {key} in table {table}.")
        return None
    except Exception as e:
        print(f"Error extracting value for {key}: {e}")
        return None

def process_sqlite_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        list_tables(cursor)  # List tables and their structures
        
        for key in table_lookup:
            value = extract_value_from_db(cursor, key)
            if value is not None:
                print(f"Found value for {key}: {value}")
            else:
                print(f"No value found for {key}")

        return {key: table_lookup[key]['value'] for key in table_lookup}
    except Exception as e:
        print(f"Error processing SQLite file: {e}")
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    file_path = r'C:\Users\edwar\Downloads\EnergyPlusOutputs_to_Edward\Output\eplusout.sql'
    
    # Check if the file path exists
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
    else:
        # Check if the file is an SQLite database
        with open(file_path, 'rb') as f:
            header = f.read(16)
            if header.startswith(b'SQLite format 3'):
                print("Detected SQLite database file")
                result = process_sqlite_db(file_path)
            else:
                print("Detected SQL script file. This should not happen with the correct .sql file being an SQLite database.")

        print("Result:", result)
