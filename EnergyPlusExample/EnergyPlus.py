import os
from pathlib import Path
import sys
import logging
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd


# We specify the path to the EnergyPlus installation directory
ENERGYPLUS_INSTALL_PATH = "../EnergyPlus"
# Add the path to the pyenergyplus directory to sys.path
sys.path.append(ENERGYPLUS_INSTALL_PATH)
from pyenergyplus.api import EnergyPlusAPI

# Set up logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# EnergyPlus and HELICS configuration paths
ENERGYPLUS_CONFIG_PATH = "EnergyPlusConfig.json"

# Add the EnergyPlus API directory to sys.path
sys.path.append(ENERGYPLUS_INSTALL_PATH)

# Initialize EnergyPlus API and create a new state
api = EnergyPlusAPI()
state = api.state_manager.new_state()

# Paths for EnergyPlus input and output
output_dir = "./Output"
Path(output_dir).mkdir(parents=True, exist_ok=True)
idf_path = os.path.join("1ZoneDataCenterCRAC_wApproachTemp_mod.idf")
epw_path = os.path.join(
    ENERGYPLUS_INSTALL_PATH,
    "WeatherData",
    "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw",
)

import helics as h

# Function to create and configure HELICS federate
def create_helics_federate(config_path):
    federate = h.helicsCreateValueFederateFromConfig(config_path)
    h.helicsFederateEnterExecutingMode(federate)
    return federate


# Function to clean up HELICS federate
def destroy_federate(federate):
    h.helicsFederateFinalize(federate)
    h.helicsFederateFree(federate)
    h.helicsCloseLibrary()


# Main co-simulation loop
def main():
    federate = create_helics_federate(ENERGYPLUS_CONFIG_PATH)

    # Diagnostics to confirm JSON config correctly added the required publications, and subscriptions.
    sub_count = h.helicsFederateGetInputCount(federate)
    pub_count = h.helicsFederateGetPublicationCount(federate)

    subid = {}
    for i in range(0, sub_count):
        subid[i] = h.helicsFederateGetInputByIndex(federate, i)
        sub_name = h.helicsSubscriptionGetTarget(subid[i])
        logger.debug(f"\tRegistered subscription---> {sub_name}")

    pubid = {}
    for i in range(0, pub_count):
        pubid[i] = h.helicsFederateGetPublicationByIndex(federate, i)
        pub_name = h.helicsPublicationGetName(pubid[i])
        logger.debug(f"\tRegistered publication---> {pubid[i]} as {pub_name}")

    # Set total number of timesteps and time interval
    number_of_days = 365
    total_hours = 24 * number_of_days
    time_interval_seconds = 60 * 10  # TODO: get this from IDF timestep?

    # Initialize a dictionary to store the results
    temp_dict = {"time": [], "whole_building_energy": []}

    # This callback checks if the warmup is complete
    warmup_done = False
    warmup_count = 0

    def warmup_complete_callback(state):
        print("Warmup complete!")
        nonlocal warmup_count
        warmup_count = warmup_count + 1
        if warmup_count > 2:
            nonlocal warmup_done
            warmup_done = True

    # This callback is called at each timestep, and sets the T_delta in EnergyPlus
    def timestep_callback(state):
        if warmup_done:
            logger.debug(f"Entered timestep callback at time {api.exchange.current_sim_time(state)}")
            currenttime = h.helicsFederateGetCurrentTime(federate)
            # What is the current time? Why does helicsFederateGetCurrentTime have a federate argument?
            if api.exchange.current_sim_time(state) < total_hours:
                grantedtime = h.helicsFederateRequestTime(
                    federate, currenttime + time_interval_seconds
                )
                # Does this block until the time is granted?
                print(f"\tGranted time interval: {grantedtime-currenttime}")
                currenttime = h.helicsFederateGetCurrentTime(federate)

            # Set the T_delta in EnergyPlus
            T_del_supp_handle = api.exchange.get_actuator_handle(
                state,
                "Schedule:Constant",
                "Schedule Value",
                "Supply Temperature Difference Schedule Mod",
            )
            T_del_ret_handle = api.exchange.get_actuator_handle(
                state,
                "Schedule:Constant",
                "Schedule Value",
                "Return Temperature Difference Schedule Mod",
            )
            # logger.debug(f"\tGot T_del_supp_handle {T_del_supp_handle}")
            # logger.debug(f"\tGot T_del_ret_handle {T_del_ret_handle}")

            T_delta_supply = 2
            T_delta_return = -1
            if h.helicsInputIsUpdated(subid[0]):
                T_delta_supply = h.helicsInputGetDouble((subid[0]))
            if h.helicsInputIsUpdated(subid[1]):
                T_delta_return = h.helicsInputGetDouble((subid[1]))
            logger.debug(
                f"\tReceived T_delta: {T_delta_supply} at time {currenttime}. Got handle {T_del_supp_handle}"
            )
            # logger.debug(
            #     f"\tReceived T_delta: {T_delta_return} at time {currenttime}. Got handle {T_del_ret_handle}"
            # )
            api.exchange.set_actuator_value(state, T_del_supp_handle, T_delta_supply)
            api.exchange.set_actuator_value(state, T_del_ret_handle, T_delta_return)

            whole_building_energy_handle = api.exchange.get_variable_handle(
                state,
                "Facility Total Building Electricity Demand Rate",
                "Whole Building",
            )
            whole_building_energy = round(
                api.exchange.get_variable_value(state, whole_building_energy_handle), 4
            )
            print(
                f"\tCurrent time: {currenttime}, current sim time : {api.exchange.current_sim_time(state)}, whole_building_energy: {whole_building_energy}"
            )
            h.helicsPublicationPublishDouble(pubid[0], whole_building_energy)
            temp_dict["time"].append(api.exchange.current_sim_time(state))
            temp_dict["whole_building_energy"].append(whole_building_energy)

    # Register callbacks
    api.runtime.callback_after_new_environment_warmup_complete(
        state, warmup_complete_callback
    )
    api.runtime.callback_end_zone_timestep_after_zone_reporting(
        state, timestep_callback
    )

    # Run EnergyPlus
    exit_code = api.runtime.run_energyplus(
        state,
        [
            "-d",
            output_dir,
            "-w",
            epw_path,
            idf_path,
        ],
    )
    print(f"EnergyPlus exited with code: {exit_code}")

    # Create a Pandas dataframe from the dictionary
    df = pd.DataFrame(temp_dict)

    # Convert timestamp to month# Apply the function and extract the month in one line
    baseline = datetime(2023, 1, 1)  # arbitrary  starting point
    df["month"] = df["time"].apply(lambda h: (baseline + timedelta(hours=h)).month)

    # Plot the results
    plt.figure(figsize=(10, 5))
    plt.plot(df["time"], df["whole_building_energy"])
    plt.title("Facility Total Building Electricity Demand Rate")
    plt.xlabel("Time (hours)")
    plt.ylabel("Electricity Demand Rate (W)")
    plt.legend(loc="lower right", title="Constant Supply Temperature Difference")
    plt.savefig("whole_building_energy.png")

    # Cleanup
    destroy_federate(federate)


if __name__ == "__main__":
    main()
