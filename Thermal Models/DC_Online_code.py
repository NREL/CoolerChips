import numpy as np
import pandas as pd
import os
import h5py
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats.qmc import LatinHypercube
import pandas as pd
from scipy.linalg import svd
from glob import glob
import os
from scipy.interpolate import Rbf
from sklearn.preprocessing import MinMaxScaler
from scipy.interpolate import RBFInterpolator
from scipy.stats.qmc import LatinHypercube
from scipy.interpolate import interp1d
import subprocess

import numpy as np
import pandas as pd
import os
import h5py
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats.qmc import LatinHypercube
import pandas as pd
from scipy.linalg import svd
from glob import glob
import os
from scipy.interpolate import Rbf
from sklearn.preprocessing import MinMaxScaler
from scipy.interpolate import RBFInterpolator
from scipy.stats.qmc import LatinHypercube
from scipy.interpolate import interp1d
import subprocess

# This fucntion "build_and_scale_rbf_models" has to be run once to run the online_prediction function multiple time inside Helics
def build_and_scale_rbf_models(training_parameters, training_coefficients, kernel_function='multiquadric'):
    """
    Build RBF models for each coefficient dimension with parameter and coefficient scaling.

    Parameters:
    - training_parameters: 2D array of parameters used for training.
    - training_coefficients: 2D array of coefficients corresponding to the training parameters.
    - kernel_function: String specifying the kernel function for the RBF models.

    Returns:
    - rbf_models: List of RBF model objects for each coefficient dimension.
    - param_scaler: Fitted scaler for parameters.
    - coeff_scaler: Fitted scaler for coefficients.
    """
    # Initialize and fit scalers
    param_scaler = MinMaxScaler().fit(training_parameters)
    coeff_scaler = MinMaxScaler().fit(training_coefficients)
    
    # Scale training data
    scaled_training_params = param_scaler.transform(training_parameters)
    scaled_training_coeffs = coeff_scaler.transform(training_coefficients)

    # Build RBF models with scaled data
    rbf_models = []
    for i in range(scaled_training_coeffs.shape[1]):
        rbf_model = Rbf(*[scaled_training_params[:, j] for j in range(scaled_training_params.shape[1])],
                        scaled_training_coeffs[:, i],
                        function=kernel_function)
        rbf_models.append(rbf_model)

    return rbf_models, param_scaler, coeff_scaler

# Main function to be passed to Helics
def online_prediction_with_CGNS(tot_vol_flow_rate_crah, rack_flow_rate1, rack_heat_load1, rack_flow_rate2, rack_heat_load2, supply_temperature, rbf_models, param_scaler, coeff_scaler, pod_modes,solution_path, paraview_path):
    
    ##### velocity range: 5 to 15 m/s
    # Assumption for hardcoded velcoity is all the servers are the same in the data center and all pull air into the server at the same inlet velocity   

    ### CPU_Load_fraction range: 0.5 to 1 (Total CPU load being 600 W per server at 100% load fraction)
    
    ### inlet_server_temperature: This does not have any range, can input any value.
    """
    Predict the system state for new velocity, heat load fraction, and inlet_server_temperature using the 
    Reduced Order Model developed in the offline stage. Adjust the predicted temperature state 
    based on the deviation from the assumed inlet temperature of 30°C.

    Parameters:
    - velocity: New velocity value for which to predict the system state.
    - heat_load_fraction: New heat load fraction value for which to predict the system state.
    - inlet_server_temperature: inlet temperature from the assumed 30°C. This should be in °C
    - rbf_models: List of pre-built RBF model objects for predicting each coefficient dimension.
    - param_scaler: Scaler object used for parameter normalization, obtained from the offline stage.
    - coeff_scaler: Scaler object used for coefficients normalization, obtained from the offline stage.
    - pod_modes: 2D array of POD modes obtained from the offline stage.

    Returns:
    - adjusted_predicted_state: 2D array of the predicted system state for the new parameters,
                                adjusted for the inlet temperature deviation.
    """
    # Create a 2D array from the input parameters
# Create a 2D array from the input parameters
    new_parameters = np.array([[tot_vol_flow_rate_crah, rack_flow_rate1, rack_heat_load1, rack_flow_rate2, rack_heat_load2]])
    
    # Normalize the new parameters using the parameter scaler
    normalized_new_params = param_scaler.transform(new_parameters)
    
    # Use the RBF models to predict the normalized coefficients for the new parameters
    predicted_normalized_coeffs = np.array([
        model(*normalized_new_params.T) for model in rbf_models
    ]).T  # Transpose to ensure correct shape
    
    # Invert the normalization of the coefficients
    predicted_coeffs = coeff_scaler.inverse_transform(predicted_normalized_coeffs)
    
    # Reconstruct the system state using the predicted coefficients and POD modes
    #The predicted state is in K
    predicted_state = np.dot(pod_modes, predicted_coeffs.T) 
    adjusted_predicted_state = predicted_state - (12-supply_temperature)-273.15 #Adjusting and converting to °C
    predicted_state_flat = adjusted_predicted_state.flatten()
    # The above adjustment only works when constant fluid properites are assumed i.e., the fluid temperature change will not significanlty affect its properties.
         # Update the temperature data in the solution file.
    try:
        with h5py.File(solution_path, 'r+') as f:
            temperature_path = 'Base/Zone/FlowSolution.N:1/Temperature/ data'  # Corrected the path format
            if temperature_path in f:
                f[temperature_path][:] = predicted_state_flat
            else:
                raise KeyError(f"Path {temperature_path} not found in the file.")
    except Exception as e:
        print(f"Failed to update temperature data: {e}")
        return
    
    # Launch ParaView to view the updated file.
    try:
        command = [paraview_path, solution_path]
        subprocess.Popen(command)
    except Exception as e:
        print(f"Failed to launch ParaView: {e}")


#----------------------------------Need to be excuted only once---------------------------
modes = np.loadtxt('modes.csv', delimiter=',')
coefficients = np.loadtxt('coefficients.csv', delimiter=',')
parameter_array=np.loadtxt('parameter_array.csv', delimiter=',')
# calling this function once to load everything that is needed to excute the rest of the code
rbf_models, param_scaler, coeff_scaler = build_and_scale_rbf_models(parameter_array, coefficients, kernel_function='multiquadric')
#-----------------------------------------------------------------------------------------

#Prediction and opening paraview block
# Example usage:
# In the case of air temperature close to the server being 30°C (Assuming a supply temperature of 20°C and supply approach temperture difference of 10°C)
# Example usage:
solution_path = r"cgns_DC.cgns"  # Update with the actual path to your solution file
paraview_path = r"C:\Program Files\ParaView 5.12.0\bin\paraview.exe"  # Ensure this matches your ParaView installation path

tot_vol_flow_rate_crah=10000 #in cfm
rack_flow_rate1=500 # 200cfm to 500cfm.
rack_flow_rate2=500# 200cfm to 500cfm.
rack_heat_load1=3000 # 500W-3000W.
rack_heat_load2=3000# 500W-3000W.
supply_temperature=12 #in °C

# Call the function with an example new velocity
online_prediction_with_CGNS(tot_vol_flow_rate_crah, rack_flow_rate1, rack_flow_rate2, rack_heat_load1, rack_heat_load2, supply_temperature, rbf_models, param_scaler, coeff_scaler, modes,solution_path, paraview_path)