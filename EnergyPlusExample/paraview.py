import numpy as np
import pandas as pd
import h5py
from scipy.interpolate import interp1d
import subprocess

from sklearn.preprocessing import MinMaxScaler
from scipy.interpolate import Rbf

# Define the velocity range for which the coefficients are known
lower_vel_limit = 6
upper_vel_limit = 15
vel = np.arange(lower_vel_limit, upper_vel_limit+1)

# Define the CPU load fraction ranges 
lower_CPU_frac = 0.5
upper_CPU_frac = 1

#Prediction and opening paraview block
# Example usage:
# In the case of air temperature close to the server being 30°C (Assuming a supply temperature of 20°C and supply approach temperture difference of 10°C)
# Example usage:
solution_path = "/app/ThermalModel_datacenter/PythonPOD_Solid.cgns"  # Update with the actual path to your solution file
paraview_path = "/Paraview/bin/paraview"  # Ensure this matches your ParaView installation path


# This fucntion "build_and_scale_rbf_models" has to be run once to run the online_prediction function multiple time inside Helics
def build_and_scale_rbf_models(kernel_function='multiquadric'):
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
    coefficients = np.loadtxt('/app/ThermalModel_datacenter/coeff.csv', delimiter=',')
    parameter_array=np.loadtxt('/app/ThermalModel_datacenter/parameter_array.csv', delimiter=',')
    # Initialize and fit scalers
    param_scaler = MinMaxScaler().fit(parameter_array)
    coeff_scaler = MinMaxScaler().fit(coefficients)
    
    # Scale training data
    scaled_training_params = param_scaler.transform(parameter_array)
    scaled_training_coeffs = coeff_scaler.transform(coefficients)

    # Build RBF models with scaled data
    rbf_models = [
        Rbf(scaled_training_params[:, 0], scaled_training_params[:, 1], scaled_training_coeffs[:, i], function=kernel_function)
        for i in range(scaled_training_coeffs.shape[1])
    ]

    return rbf_models, param_scaler, coeff_scaler

# calling this function once to load everything that is needed to excute the rest of the code
rbf_models, param_scaler, coeff_scaler = build_and_scale_rbf_models(kernel_function='multiquadric')


# Main function to be passed to Helics
def predict_temperature(velocity, CPU_load_fraction=0.73, inlet_server_temperature=30):
    
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
    
    #----------------------------------Need to be excuted only once---------------------------
    modes = np.loadtxt('/app/ThermalModel_datacenter/modes.csv', delimiter=',')
    #-----------------------------------------------------------------------------------------
    # Create a 2D array from the input parameters
    new_parameters = np.array([[velocity, CPU_load_fraction]])
    
    # Normalize the new parameters using the parameter scaler
    normalized_new_params = param_scaler.transform(new_parameters)
    
    # Use the RBF models to predict the normalized coefficients for the new parameters
    predicted_normalized_coeffs = np.array([
        model(normalized_new_params[:, 0], normalized_new_params[:, 1]) for model in rbf_models
    ]).T  # Transpose to ensure correct shape
    
    # Invert the normalization of the coefficients
    predicted_coeffs = coeff_scaler.inverse_transform(predicted_normalized_coeffs)
    
    # Reconstruct the system state using the predicted coefficients and POD modes
    #The predicted state is in K
    predicted_state = np.dot(modes, predicted_coeffs.T) 
    adjusted_predicted_state = predicted_state - (30-inlet_server_temperature)-273.15 #Adjusting and converting to °C
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

if __name__ == '__main__':
 

    # Call the function with an example new velocity
    predict_temperature(velocity=10)