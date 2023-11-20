import os
import sys
import logging
import numpy as np
import asyncio
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd


ENERGYPLUS_INSTALL_PATH = '/usr/local/EnergyPlus-9-6-0'
# Add the path to the pyenergyplus directory to sys.path
sys.path.append(ENERGYPLUS_INSTALL_PATH)
from pyenergyplus.api import EnergyPlusAPI

# Set up logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# EnergyPlus and HELICS configuration paths
ENERGYPLUS_INSTALL_PATH = '/usr/local/EnergyPlus-9-6-0'
ENERGYPLUS_CONFIG_PATH = "EnergyPlusConfig.json"

# Add the EnergyPlus API directory to sys.path
sys.path.append(ENERGYPLUS_INSTALL_PATH)

# Callback function for EnergyPlus output
def message_func(message: bytes):
    print(f'Stdout Called: {message}')

# Initialize EnergyPlus API and create a new state
api = EnergyPlusAPI()
state = api.state_manager.new_state()

# Paths for EnergyPlus input and output
output_dir = '/workspaces/CoolerChips/EnergyPlusExampleoutput'
idf_path = os.path.join('/workspaces/CoolerChips/EnergyPlusExample/1ZoneDataCenterCRAC_wApproachTemp_mod.idf')
epw_path = os.path.join(ENERGYPLUS_INSTALL_PATH, 'WeatherData', 'USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw')

# Asynchronous function to run EnergyPlus
async def run_energyplus(state):
    await asyncio.to_thread(api.runtime.run_energyplus, state, ['-d', output_dir, '-w', epw_path, '-i', 'Energy+.idd', idf_path])
    
import helics as h

baseline = datetime(2023, 1, 1)  # Replace with your baseline date


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
async def main():
    federate = create_helics_federate(ENERGYPLUS_CONFIG_PATH)
    
    sub_count = h.helicsFederateGetInputCount(federate)
    logger.debug(f"\tNumber of subscriptions: {sub_count}")
    
    pub_count = h.helicsFederateGetPublicationCount(federate)
    logger.debug(f"\tNumber of publications: {pub_count}")
    
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
    
    
    beginTime = h.helicsFederateGetCurrentTime(federate)
    print(f"Begin time: {beginTime}")  
    number_of_days = 365 
    total_timesteps = 24 * 7 * number_of_days
    time_interval = 60 * 10 # get this from IDF timestep?
    temp_dict = {'time':[], 'temperature':[]}
    
    warmup_done = False
    warmup_count = 0
    

        
    def warmup_complete_callback(state):
        print("Warmup complete!")
        nonlocal warmup_count
        warmup_count = warmup_count + 1
        if warmup_count>2:
            nonlocal warmup_done
            warmup_done = True
    
    def timestep_callback(state):
        if warmup_done:
            currenttime = h.helicsFederateGetCurrentTime(federate)
            
            # if h.helicsInputIsUpdated(sub):
            heating_setpoint = h.helicsInputGetDouble((subid[0]))
            cooling_setpoint = h.helicsInputGetDouble((subid[1]))
            # Set the setpoint in EnergyPlus
            heating_setpoint_handle = api.exchange.get_actuator_handle(state, "Schedule:Constant", "Schedule Value", "HEATING SETPOINT SCHEDULE MOD")
            cooling_setpoint_handle = api.exchange.get_actuator_handle(state, "Schedule:Constant", "Schedule Value", "Cooling Return Air Setpoint Schedule Mod")   
            api.exchange.set_actuator_value(state, heating_setpoint_handle, heating_setpoint)
            api.exchange.set_actuator_value(state, cooling_setpoint_handle, cooling_setpoint)
            logger.debug(f"Received setpoint: {heating_setpoint} at time {currenttime}. Got handle {heating_setpoint_handle}")
            logger.debug(f"Received setpoint: {cooling_setpoint} at time {currenttime}. Got handle {cooling_setpoint_handle}")
            
            temperature_handle = api.exchange.get_variable_handle(state, "Zone Air Temperature", "Main Zone")
            zone_temperature = api.exchange.get_variable_value(state, temperature_handle)
            print(f"Current time: {currenttime}, current sim time : {api.exchange.current_sim_time(state)}, outdoor temperature: {zone_temperature}") 
            h.helicsPublicationPublishDouble(pubid[0], zone_temperature)
            temp_dict['time'].append(api.exchange.current_sim_time(state))
            temp_dict['temperature'].append(zone_temperature)
            if api.exchange.current_sim_time(state) < total_timesteps:
                grantedtime = h.helicsFederateRequestTime(federate, currenttime+time_interval)
                print(f"Granted time: {grantedtime-currenttime}")
                currenttime = h.helicsFederateGetCurrentTime(federate)
        
    
    # api.runtime.callback_message(state, message_func)
    api.runtime.callback_after_new_environment_warmup_complete(state, warmup_complete_callback)
    api.runtime.callback_end_zone_timestep_after_zone_reporting(state, timestep_callback)
    energyplus_task = asyncio.create_task(run_energyplus(state))


    # Wait for EnergyPlus to finish
    await energyplus_task
    df = pd.DataFrame(temp_dict)
    # Convert timestamp to month# Apply the function and extract the month in one line
    df['month'] = df['time'].apply(lambda h: (baseline + timedelta(hours=h)).month)

    
    # Plot the results
    sns.lineplot(data=df, x="time", y="temperature")
    plt.title("Main Zone Thermostat Air Temperature")
    plt.xlabel("Time (hours)")
    plt.ylabel("Temperature (C)")
    plt.show()

    # Cleanup
    destroy_federate(federate)

if __name__ == "__main__":
    asyncio.run(main())
