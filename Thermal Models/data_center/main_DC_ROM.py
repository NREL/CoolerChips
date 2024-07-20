import numpy as np
import pandas as pd
from DC_rbf_models import build_and_scale_rbf_models, online_prediction_DC_ROM
from surface_isolation_DC import DataCenterCGNS

# Load necessary data
modes = np.loadtxt(r'Thermal Models\data_center\data\modes.csv', delimiter=',')
coefficients = np.loadtxt(r'Thermal Models\data_center\data\coefficients.csv', delimiter=',')
parameter_array = np.loadtxt(r'Thermal Models\data_center\data\parameter_array.csv', delimiter=',')
parameter_array = np.delete(parameter_array, 1, axis=1)

# Build RBF models and scale data (to be run once)
rbf_models, param_scaler, coeff_scaler = build_and_scale_rbf_models(parameter_array, coefficients, kernel_function='multiquadric')

# Initializing surface isolation class for extracting surface temperatures
data_center = DataCenterCGNS(r'Thermal Models/data_center/data/cgns_DC.cgns')

# Example usage for prediction
tot_vol_flow_rate_crah = 16772.549378917283  # in cfm
rack_flow_rate1 = 877.8471592479111  # 800cfm to 2000cfm.
rack_heat_load1 = 5605.209396433776  # 2000W-12000W.
rack_flow_rate2 = 831.1856050890956  # 800cfm to 2000cfm.
rack_heat_load2 = 3274.698032971656  # 2000W-12000W.
supply_temperature = 12  # in °C

# Predict the temperature state
predicted_state = online_prediction_DC_ROM(tot_vol_flow_rate_crah, rack_flow_rate1, rack_heat_load1,
                                           rack_flow_rate2, rack_heat_load2, supply_temperature,
                                           rbf_models, param_scaler, coeff_scaler, modes)

# Initialize dictionaries to store temperatures and approach temperatures
server_inlet_temps = {}
server_outlet_temps = {}
supply_approach_temps = {}
return_approach_temps = {}

# Loop through each server (assuming server locations are labeled as '1_1_1', '1_1_2', ..., '2_5_4')
for i in range(1, 3):
    for j in range(1, 6):
        for k in range(1, 5):
            server_location = f'{i}_{j}_{k}'
            avg_temp_in = data_center.server_inlet(server_location, predicted_state, stat='avg')
            avg_temp_out = data_center.server_outlet(server_location, predicted_state, stat='avg')
            
            server_inlet_temps[server_location] = avg_temp_in
            server_outlet_temps[server_location] = avg_temp_out

# Compute CRAH inlet temperature as the average of three blower temperatures
avg_temp_crah_in_blower_1 = data_center.crah_inlet('1', predicted_state, stat='avg')
avg_temp_crah_in_blower_2 = data_center.crah_inlet('2', predicted_state, stat='avg')
avg_temp_crah_in_blower_3 = data_center.crah_inlet('3', predicted_state, stat='avg')
avg_temp_crah_in = (avg_temp_crah_in_blower_1 + avg_temp_crah_in_blower_2 + avg_temp_crah_in_blower_3) / 3

# Compute CRAH return temperature
avg_temp_crah_ret = data_center.crah_return(predicted_state, stat='avg')

# Calculate and store supply and return approach temperatures for each server
for server_location in server_inlet_temps:
    supply_approach_temps[server_location] = server_inlet_temps[server_location] - avg_temp_crah_in
    return_approach_temps[server_location] = server_outlet_temps[server_location] - avg_temp_crah_ret

# Print all the results
print("SERVER INLET TEMPERATURES")
print("-------------------------")
for location, temp in server_inlet_temps.items():
    print(f"Location {location}: {round(temp, 5)} [°C]")

print("\nSERVER OUTLET TEMPERATURES")
print("-------------------------")
for location, temp in server_outlet_temps.items():
    print(f"Location {location}: {round(temp, 5)} [°C]")

print("\nSUPPLY APPROACH TEMPERATURES")
print("-----------------------------")
for location, temp in supply_approach_temps.items():
    print(f"Location {location}: {round(temp, 5)} [°C]")

print("\nRETURN APPROACH TEMPERATURES")
print("-----------------------------")
for location, temp in return_approach_temps.items():
    print(f"Location {location}: {round(temp, 5)} [°C]")

print("\nCRAH INLET TEMPERATURE")
print("-----------------------------")
print(f"Average Temperature: {round(avg_temp_crah_in, 5)} [°C]")

print("\nCRAH RETURN TEMPERATURE")
print("-----------------------------")
print(f"Average Temperature: {round(avg_temp_crah_ret, 5)} [°C]")
