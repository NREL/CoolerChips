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

# PUBS = [
#     {
#         "Name": f'{actuator["component_type"]}/{actuator["control_type"]}/{actuator["actuator_key"]}',
#         "Type": "double",
#         "Units": actuator["actuator_unit"],
#         "Global": True,
#     }
#     for actuator in definitions.ACTUATORS
# ]

PUBS = [
    {
        "Name": "Server Output Temperature",
        "Type": "double",
        "Units": "K",
        "Global": True,
    }
]

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
        self.total_time = 62 * 24 * 60 * 60  # get this from IDF
        self.subs = [federate.Sub(name=f'{sensor["variable_key"]}/{sensor["variable_name"]}', unit=sensor["variable_unit"]) for sensor in definitions.SENSORS]
        self.pubs = [federate.Pub(name=f'{pub["Name"]}', unit=pub["Units"]) for pub in PUBS]
        self.server_federate = federate.mostcool_federate(federate_name="Server_1", subscriptions=self.subs, publications=self.pubs)
        self.server_federate.time_interval_seconds = definitions.TIMESTEP_PERIOD_SECONDS
        
        
        
    
    def _get_temperature(self, new_velocity):
        # Interpolate coefficients for each POD mode
        interp_funcs = [interp1d(vel, coeff[i, :], kind='linear') for i in range(coeff.shape[0])]
        
        # Predict coefficients for the new velocity
        new_coeff = np.array([f(new_velocity) for f in interp_funcs])
        
        # Calculate the predicted temperature field
        T_pred = sum(new_coeff[i] * modes[:, i] for i in range(coeff.shape[0]))
        
        # Update the temperature data in the solution file
        with h5py.File(solution_path, 'r+') as f:
            temperature_path = 'Base/Zone/FlowSolution.N:1/Temperature/ data'
            if temperature_path in f:
                f[temperature_path][:] = T_pred
            else:
                raise KeyError(f"Path {temperature_path} not found in the file.")
        
        # Extract the temperature at points of interest
        with h5py.File(solution_path, 'r') as f:
            pointlist_path = 'Base/Zone/ZoneBC/cpu-pcb-1-wall/PointList/ data'
            pointlist = f[pointlist_path][:]
            pointlist_flat = np.ravel(pointlist)
            
            # Paths to the X, Y, Z coordinates and temperature in the CGNS file
            x_path = 'Base/Zone/GridCoordinates/CoordinateX/ data'
            y_path = 'Base/Zone/GridCoordinates/CoordinateY/ data'
            z_path = 'Base/Zone/GridCoordinates/CoordinateZ/ data'
            temperature_path = 'Base/Zone/FlowSolution.N:1/Temperature/ data'
            
            # Retrieve the coordinate and temperature data
            x = f[x_path][:]
            y = f[y_path][:]
            z = f[z_path][:]
            temperature = f[temperature_path][:]
            
            # Create a DataFrame and map the temperature to the points of interest
            df_temp = pd.DataFrame({'X': x, 'Y': y, 'Z': z, 'Temperature': temperature})
            df_mapped = df_temp.iloc[pointlist_flat]
            
        # Calculate the average temperature
        average_temperature = df_mapped['Temperature'].mean()
        # print(f"The average temperature at {self.server_federate.granted_time} is: {average_temperature}")
        return average_temperature
    
    def run(self):
        while self.server_federate.granted_time < self.total_time:
            sub_values = self.server_federate.update_subs()
            # logger.debug(f"Received values: {sub_values}")
            # new_velocity = self.server_federate.get_new_velocity()
            average_temperature = self._get_temperature(new_velocity=10)
            if average_temperature is not None:
                self.pubs[0].value = average_temperature
                self.server_federate.update_pubs()
            # self.server_federate.publish_average_temperature(average_temperature)
            self.server_federate.request_time()
        self.server_federate.destroy_federate()
    
    
thermal_model_runner = Server_thermal_federate()
thermal_model_runner.run()
    
