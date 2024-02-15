import os

# Available control options
CHANGE_LIQUID_COOLING = 1
CHANGE_SUPPLY_DELTA_T = 2
CHANGE_IT_LOAD = 3
# TODO: select a control option
CONTROL_OPTION = CHANGE_IT_LOAD

if CONTROL_OPTION == CHANGE_LIQUID_COOLING:
    IDF_PATH = "2ZoneDataCenterCRAHandplant.idf"
else:
    IDF_PATH = "2ZoneDataCenterCRAHandplant_aircoolingonly.idf"

OUTPUT_DIR = "./Output"
ENERGYPLUS_INSTALL_PATH = "../EnergyPlus"
EPW_PATH = os.path.join(ENERGYPLUS_INSTALL_PATH, "WeatherData/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

TIMESTEP_PERIOD_SECONDS = 600  # 10 mins

ACTUATORS = [
    {
        "component_type": "Schedule:Compact",
        "control_type": "Schedule Value",
        "actuator_key": "Load Profile 1 Load Schedule",
        "actuator_unit": "1"
    },
    {
        "component_type": "Schedule:Constant",
        "control_type": "Schedule Value",
        "actuator_key": "Supply Temperature Difference Schedule Mod",
        "actuator_unit": "C"
    },
    {
        "component_type": "Schedule:Compact",
        "control_type": "Schedule Value",
        "actuator_key": "Data Center CPU Loading Schedule",
        "actuator_unit": "1"
    },
    {
        "component_type": "Schedule:Compact",
        "control_type": "Schedule Value",
        "actuator_key": "Load Profile 1 Flow Frac Schedule",
        "actuator_unit": "1"
    }
]

# old, for testing
# ACTUATORS = [
#     {
#         "component_type": "Schedule:Constant",
#         "control_type": "Schedule Value",
#         "actuator_key": "Supply Temperature Difference Schedule Mod",
#         "actuator_unit": "C"
#     },
#     {
#         "component_type": "Schedule:Constant",
#         "control_type": "Schedule Value",
#         "actuator_key": "Return Temperature Difference Schedule Mod",
#         "actuator_unit": "C"
#     }
# ]


SENSORS = [
    {
        "variable_name": "Facility Total HVAC Electricity Demand Rate",
        "variable_key": "Whole Building",
        "variable_unit": "W"
    },
    {
        "variable_name": "Facility Total Electricity Demand Rate",
        "variable_key": "Whole Building",
        "variable_unit": "W"
    }
]


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

