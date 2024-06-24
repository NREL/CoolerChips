def process_file_interest(self, file_path, output_box):
    with open(file_path, 'r') as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    chiller_table = soup.find('b', text='Chiller:Electric:EIR').find_next('table')
    if chiller_table:
        capacity_value = self.extract_value_from_table(chiller_table,
                                                       'Design Size Reference Capacity [W]')
        output_box.insert(tk.END,
                          "Design Size Reference Capacity [W]: " + capacity_value + "\n")

        # Store values in both input_reference and input_interest dictionaries
        self.input_interest["Design Size Reference Capacity [W]: "] = capacity_value

    else:
        output_box.insert(tk.END, "Chiller table not found in the HTML content.\n")

    # Find the airloopHVAC table
    airloopHVAC_table = soup.find('b', text='AirLoopHVAC').find_next('table')
    if airloopHVAC_table:
        flow_rate_value = self.extract_value_from_table(airloopHVAC_table,
                                                        'Adjusted Cooling Design Air Flow Rate [m3/s]')
        output_box.insert(tk.END,
                          "Adjusted Cooling Design Air Flow Rate [m3/s]: " + flow_rate_value + "\n")

        # Store values in both input_reference and input_interest dictionaries
        self.input_interest[
            "Adjusted Cooling Design Air Flow Rate [m3/s]: "] = flow_rate_value
    else:
        output_box.insert(tk.END, "AirLoopHVAC table not found in the HTML content.\n")

    # Find the CoolingTower:VariableSpeed table
    cooling_tower_table = soup.find('b', text='CoolingTower:VariableSpeed').find_next(
        'table')
    if cooling_tower_table:
        capacity_value = self.extract_value_from_table(cooling_tower_table,
                                                       'Nominal Capacity [W]')
        output_box.insert(tk.END, "Nominal Capacity [W]: " + capacity_value + "\n")

        # Store values in both input_reference and input_interest dictionaries
        self.input_interest["Nominal Capacity [W]: "] = capacity_value

    else:
        output_box.insert(tk.END,
                          "CoolingTower:VariableSpeed table not found in the HTML content.\n")

    # Find the Pump cost
    pump_table = soup.find('b', text='Pump:VariableSpeed').find_next('table')
    if pump_table:
        flow_rate_value = self.extract_value_from_table(pump_table,
                                                        'Design Flow Rate [m3/s]')
        output_box.insert(tk.END, "Design Flow Rate [m3/s]: " + flow_rate_value + "\n")
        power_consumption_value = self.extract_value_from_table(pump_table,
                                                                'Design Power Consumption [W]')
        output_box.insert(tk.END,
                          "Design Power Consumption [W]: " + power_consumption_value + "\n")

        # Store values in both input_reference and input_interest dictionaries
        self.input_interest["Design Flow Rate [m3/s]: "] = flow_rate_value
        self.input_interest["Design Power Consumption [W]: "] = power_consumption_value
    else:
        output_box.insert(tk.END,
                          "Pump:VariableSpeed table not found in the HTML content.\n")

    # Find the PlantLoop table
    plantloop_table = soup.find('b', text='PlantLoop').find_next('table')
    if plantloop_table:
        volume_value = self.extract_value_from_table(plantloop_table,
                                                     'Plant Loop Volume [m3]')
        output_box.insert(tk.END, "Plant Loop Volume [m3]: " + volume_value + "\n")

        # Store values in both input_reference and input_interest dictionaries
        self.input_interest["Plant Loop Volume [m3]: "] = volume_value
    else:
        output_box.insert(tk.END, "PlantLoop table not found in the HTML content.\n")



table_lookup = {
    "chiller": {
        "lookup_text": 'Chiller:Electric:EIR',
        "field_name": 'Design Size Reference Capacity [W]',
        "dictionary_key": 'Design Size Reference Capacity [W]:'
    },
    "airloopHVAC": {
        "lookup_text": 'AirLoopHVAC',
        "field_name": 'Adjusted Cooling Design Air Flow Rate [m3/s]',
        "dictionary_key": 'Adjusted Cooling Design Air Flow Rate [m3/s]:'
    },
    "coolingTower": {
        "lookup_text": 'CoolingTower:VariableSpeed',
        "field_name": 'Nominal Capacity [W]',
        "dictionary_key": 'Nominal Capacity [W]:'
    },
    "pump_flow": {
        "lookup_text": 'Pump:VariableSpeed',
        "field_name": 'Design Flow Rate [m3/s]',
        "dictionary_key": 'Design Flow Rate [m3/s]:'
    },
    "pump_power": {
        "lookup_text": 'Pump:VariableSpeed',
        "field_name": 'Design Power Consumption [W]',
        "dictionary_key": 'Design Power Consumption [W]:'
    },
    "plantLoop": {
        "lookup_text": 'PlantLoop',
        "field_name": 'Plant Loop Volume [m3]',
        "dictionary_key": 'Plant Loop Volume [m3]:'
    }
}

def process_file_interest(self, file_path, output_box):

    # put in initialization or config file
    self.table_lookup = {
        "chiller": {
            "lookup_text": 'Chiller:Electric:EIR',
            "field_name": 'Design Size Reference Capacity [W]',
            "dictionary_key": 'Design Size Reference Capacity [W]:'
        },
        "airloopHVAC": {
            "lookup_text": 'AirLoopHVAC',
            "field_name": 'Adjusted Cooling Design Air Flow Rate [m3/s]',
            "dictionary_key": 'Adjusted Cooling Design Air Flow Rate [m3/s]:'
        },
        "coolingTower": {
            "lookup_text": 'CoolingTower:VariableSpeed',
            "field_name": 'Nominal Capacity [W]',
            "dictionary_key": 'Nominal Capacity [W]:'
        },
        "pump_flow": {
            "lookup_text": 'Pump:VariableSpeed',
            "field_name": 'Design Flow Rate [m3/s]',
            "dictionary_key": 'Design Flow Rate [m3/s]:'
        },
        "pump_power": {
            "lookup_text": 'Pump:VariableSpeed',
            "field_name": 'Design Power Consumption [W]',
            "dictionary_key": 'Design Power Consumption [W]:'
        },
        "plantLoop": {
            "lookup_text": 'PlantLoop',
            "field_name": 'Plant Loop Volume [m3]',
            "dictionary_key": 'Plant Loop Volume [m3]:'
        }
    }

    def extract_and_store_value(soup, table_key, output_box):

        lookup_info = table_lookup[table_key]
        table = soup.find('b', text=lookup_info["lookup_text"]).find_next('table')

        if table:
            value = self.extract_value_from_table(table, lookup_info["field_name"])
            output_box.insert(tk.END, f"{lookup_info['dictionary_key']} {value}\n")
            self.input_interest[lookup_info["dictionary_key"]] = value
        else:
            output_box.insert(tk.END, f"{table_key} table not found in the HTML content.\n")

    with open(file_path, 'r') as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Process each table
    extract_and_store_value(soup, 'chiller', output_box)
    extract_and_store_value(soup, 'airloopHVAC', output_box)
    extract_and_store_value(soup, 'coolingTower', output_box)
    extract_and_store_value(soup, 'pump_flow', output_box)
    extract_and_store_value(soup, 'pump_power', output_box)
    extract_and_store_value(soup, 'plantLoop', output_box)

def duct_calculator(self, volume_value):
    # Convert capacity_value to string if it's an integer
    if isinstance(volume_value, int):
        volume_value = str(volume_value)
    cost_factor = float(self.variables["CEPCI Number"])
    estimate_duct_size = 4  # sq ft
    duct_cost = (700 / estimate_duct_size) * float(volume_value) * cost_factor

    return duct_cost


import pydantic
class DuctConfig(pydantic.BaseModel):
    estimate_duct_size: int
    undocumented_number: int

class ModelConfig(pydantic.BaseModel):
    duct: DuctConfig
    chiller: ChillerConfig


def duct_calculator(self, volume_value):
    # Convert capacity_value to string if it's an integer
    if isinstance(volume_value, int):
        volume_value = str(volume_value)
    cost_factor = float(self.variables["CEPCI Number"])
    estimate_duct_size = ModelConfig.duct.estimate_duct_size
    undocumented_number = ModelConfig.duct.undocumented_number
    duct_cost = (undocumented_number / estimate_duct_size) * float(volume_value) * cost_factor

    return duct_cost


