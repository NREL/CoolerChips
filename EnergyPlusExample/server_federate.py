"""Datacenter Thermal Model Federate"""

import pandas as pd
import federate
import h5py
from scipy.interpolate import interp1d
import numpy as np
import definitions
import logging


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# Read modes and coefficients from CSV files outside the function
Modes = pd.read_csv('ThermalModel_datacenter/Modes.csv')
modes = Modes.to_numpy()

Coeff = pd.read_csv('ThermalModel_datacenter/coeff.csv')
coeff = Coeff.to_numpy()

# Define the velocity range for which the coefficients are known
vel = np.arange(6, 16)
solution_path = "ThermalModel_datacenter/solution_PythonPOD_Solid.cgns"

PUBS = [
    {
        "Name": f'{actuator["component_type"]}/{actuator["control_type"]}/{actuator["actuator_key"]}',
        "Type": "double",
        "Units": actuator["actuator_unit"],
        "Global": True,
    }
    for actuator in definitions.ACTUATORS
][1:3] # only the second and third actuator is used - supply delta T and return delta T

SUBS = [
    {
        "Name": sensor["variable_key"] + "/" + sensor["variable_name"],
        "Type": "double",
        "Units": sensor["variable_unit"],
        "Global": True,
    }
    for sensor in definitions.SENSORS
]

class Server_thermal_federate:
    def __init__(self) -> None:
        self.total_time = definitions.TOTAL_SECONDS  # get this from IDF
        self.subs = [federate.Sub(name=f'{sensor["variable_key"]}/{sensor["variable_name"]}', unit=sensor["variable_unit"]) for sensor in definitions.SENSORS]
        self.pubs = [federate.Pub(name=f'{pub["Name"]}', unit=pub["Units"]) for pub in PUBS]
        self.server_federate = federate.mostcool_federate(federate_name="Server_1", subscriptions=self.subs, publications=self.pubs)
        self.server_federate.time_interval_seconds = definitions.TIMESTEP_PERIOD_SECONDS
           
    def thermal_model(self, Ts, mass_flowrate, power_level=1, num_servers=1):
        # Define constants
        dens = 1.225 #kg/m^3
        cp = 1006.43 #J/kgK

        # Adjust mass_flowrate based on power level
        base_mass_flowrate = 0.322665000000000 #kg/s
        if mass_flowrate == 0:
            mass_flowrate = base_mass_flowrate * power_level #power level in kW
        
        # Calculate pressure drop
        pressure_drop = 7.3794e+03 * mass_flowrate ** 1.9087 #Pa
        
        # Calculate temperatures and energy consumption based on power level
        if power_level == 1:
            del_T1 = 10
            del_T2 = -5
        elif power_level == 0.8:
            del_T1 = 7.5
            del_T2 = -3
        elif power_level == 0.6:
            del_T1 = 5
            del_T2 = -1.5
        else:
            # Default values if power_level is not recognized
            del_T1 = del_T2 = 0
        
        # Calculate server temperatures
        T_in_server = Ts + del_T1
        T_out_server = T_in_server + power_level * 1000 / (mass_flowrate * cp)
        
        # Calculate energy consumption by fans
        energy_consumption_per_fan = pressure_drop * mass_flowrate / dens
        energy_consumption = energy_consumption_per_fan * num_servers

        # Return the supply approach temperature, return approach temperature, and energy consumed by fans
        return del_T1, del_T2, energy_consumption
    
    def run(self):
        while self.server_federate.granted_time < self.total_time:
            self.server_federate.update_subs()
            Ts = 0
            mass_flow_rate = 0
            for sub in self.subs:
                if sub.name == "East Zone Supply Fan/Fan Air Mass Flow Rate":
                    mass_flow_rate = sub.value
                elif sub.name == "East Air Loop Outlet Node/System Node Temperature":
                    Ts = sub.value
            print(f"Mass flow rate: {mass_flow_rate}, Supply temperature: {Ts} at time {self.server_federate.granted_time}")
            supply_approach_temp, return_approach_temperature, energy_fan = self.thermal_model(Ts=Ts, mass_flowrate=mass_flow_rate)
            if supply_approach_temp is not None:
                self.pubs[0].value = supply_approach_temp
            if return_approach_temperature is not None:
                self.pubs[1].value = return_approach_temperature
            self.server_federate.update_pubs()
            self.server_federate.request_time()
        self.server_federate.destroy_federate()
    
    
thermal_model_runner = Server_thermal_federate()
thermal_model_runner.run()
    
