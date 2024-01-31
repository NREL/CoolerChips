import os
from pathlib import Path

IDF_PATH = "1ZoneDataCenterCRAC_wApproachTemp_mod.idf"
OUTPUT_DIR = "./Output"
ENERGYPLUS_INSTALL_PATH = "../EnergyPlus"
EPW_PATH = os.path.join(ENERGYPLUS_INSTALL_PATH, "WeatherData/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")
RESOURCES_DIR = "./Resources"
GRAPHS_DIR = os.path.join(OUTPUT_DIR, "graphs")
Path(GRAPHS_DIR).mkdir(parents=True, exist_ok=True)


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


LOG_LEVEL_MAP = { # Maps the log level string to helics Integer log level
    # more info: https://docs.helics.org/en/helics2/user-guide/logging.html
    "helics_log_level_no_print": -1,
    "helics_log_level_error": 0,
    "helics_log_level_warning": 1,
    "helics_log_level_summary": 2,
    "helics_log_level_connections": 3,
    "helics_log_level_interfaces": 4,
    "helics_log_level_timing": 5,
    "helics_log_level_data": 6,
    "helics_log_level_trace": 7,    
}                 
