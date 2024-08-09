import numpy as np
import pandas as pd
from DC_rbf_models import build_and_scale_rbf_models, online_prediction_DC_ROM
from surface_isolation_DC import DataCenterCGNS
from dc_rom_outputs import dc_rom_outputs

#---------------------------------have to run once-----------------------------------------
# Load necessary data
modes = np.load('/app/mostcool/thermal/data_center/data/modes.npy')
coefficients = np.load('/app/mostcool/thermal/data_center/data/coefficients.npy')
parameter_array = np.load('/app/mostcool/thermal/data_center/data/parameter_array.npy')
parameter_array = np.delete(parameter_array, 1, axis=1)

# Build RBF models and scale data (to be run once)
rbf_models, param_scaler, coeff_scaler = build_and_scale_rbf_models(parameter_array, coefficients, kernel_function='multiquadric')

# Initializing surface isolation class for extracting surface temperatures
data_center = DataCenterCGNS('/app/mostcool/thermal/data_center/data/cgns_DC.cgns')
#---------------------------------have to run once-----------------------------------------

# Example usage for prediction
tot_vol_flow_rate_crah = 16772.549378917283  # in cfm
rack_flow_rate1 = 877.8471592479111  # 800cfm to 2000cfm.
rack_heat_load1 = 5605.209396433776  # 2000W-12000W.
rack_flow_rate2 = 831.1856050890956  # 800cfm to 2000cfm.
rack_heat_load2 = 3274.698032971656  # 2000W-12000W.
supply_temperature = 12  # in °C


#--------------------------Inside Helics------------------------------------------------------
# Predict the temperature state
predicted_state = online_prediction_DC_ROM(tot_vol_flow_rate_crah, rack_flow_rate1, rack_heat_load1,
                                           rack_flow_rate2, rack_heat_load2, supply_temperature,
                                           rbf_models, param_scaler, coeff_scaler, modes)


[server_inlet_temps, server_outlet_temps, avg_crah_in, avg_crah_ret,
            supply_approach_temp, return_approach_temp, server_locations]=dc_rom_outputs(predicted_state, data_center)

#checking outputs
#print(server_inlet_temps,server_outlet_temps,avg_crah_in,avg_crah_ret,supply_approach_temp,return_approach_temp,server_locations)