
IDF_PATH = "1ZoneDataCenterCRAC_wApproachTemp_mod.idf"
CONFIG_PATH = "EnergyPlusConfig.json"
OUTPUT_DIR = "./Output"
EPW_PATH = "./EnergyPlus/WeatherData/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw"

ACTUATORS = [{"component_type": "Schedule:Constant",
              "control_type": "Schedule Value",
              "actuator_key": "Supply Temperature Difference Schedule Mod",
              "actuator_unit": "C"
    },
             {"component_type": "Schedule:Constant",
              "control_type": "Schedule Value",
              "actuator_key": "Return Temperature Difference Schedule Mod",
              "actuator_unit": "C"
    }]


SENSORS = [{"variable_name": "Facility Total Building Electricity Demand Rate",
            "variable_key": "Whole Building",
            "variable_unit": "J"}]
