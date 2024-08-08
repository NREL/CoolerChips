import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from scipy.interpolate import Rbf
import h5py

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
    param_scaler = MinMaxScaler().fit(training_parameters)
    coeff_scaler = MinMaxScaler().fit(training_coefficients)
    
    scaled_training_params = param_scaler.transform(training_parameters)
    scaled_training_coeffs = coeff_scaler.transform(training_coefficients)

    rbf_models = []
    for i in range(scaled_training_coeffs.shape[1]):
        rbf_model = Rbf(*[scaled_training_params[:, j] for j in range(scaled_training_params.shape[1])],
                        scaled_training_coeffs[:, i],
                        function=kernel_function)
        rbf_models.append(rbf_model)

    return rbf_models, param_scaler, coeff_scaler

def online_prediction_DC_ROM(tot_vol_flow_rate_crah, rack_flow_rate1, rack_heat_load1, rack_flow_rate2, 
                                        rack_heat_load2, supply_temperature, rbf_models, param_scaler, 
                                        coeff_scaler, pod_modes):
    """
    Predict the system state for new total volume flow rate, rack flow rates, rack heat loads, and supply temperature.

    Parameters:
    - tot_vol_flow_rate_crah: Total volume flow rate for CRAH units. (Range: 10000 CFM to 20000 CFM)
    - rack_flow_rate1: Flow rate for the first row of racks. (Range: 800 CFM to 2000 CFM)
    - rack_heat_load1: Heat load for the first row of racks. (Range: 2000 W to 12000 W)
    - rack_flow_rate2: Flow rate for the second row of racks. (Range: 800 CFM to 2000 CFM)
    - rack_heat_load2: Heat load for the second row of racks. (Range: 2000 W to 12000 W)
    - supply_temperature: Supply temperature from the assumed 12°C. This should be in °C.
    - rbf_models: List of pre-built RBF model objects for predicting each coefficient dimension.
    - param_scaler: Scaler object used for parameter normalization, obtained from the offline stage.
    - coeff_scaler: Scaler object used for coefficients normalization, obtained from the offline stage.
    - pod_modes: 2D array of POD modes obtained from the offline stage.

    Returns:
    - predicted_state: Adjusted predicted temperature state based on the deviation from the assumed supply temperature of 12°C.
    """
    bounds = {
        "tot_vol_flow_rate_crah": (10000, 20000),
        "rack_flow_rate1": (800, 2000),
        "rack_heat_load1": (2000, 12000),
        "rack_flow_rate2": (800, 2000),
        "rack_heat_load2": (2000, 12000),
        "supply_temperature": (0,100)  # Adjust based on realistic supply temperature range
    }

    parameters = {
        "tot_vol_flow_rate_crah": tot_vol_flow_rate_crah,
        "rack_flow_rate1": rack_flow_rate1,
        "rack_heat_load1": rack_heat_load1,
        "rack_flow_rate2": rack_flow_rate2,
        "rack_heat_load2": rack_heat_load2,
        "supply_temperature": supply_temperature
    }

    for param, value in parameters.items():
        if not bounds[param][0] <= value <= bounds[param][1]:
            print(f"Warning: {param} value {value} is out of bounds. Expected range: {bounds[param]}")

    new_parameters = np.array([[tot_vol_flow_rate_crah, rack_flow_rate1, rack_heat_load1, rack_flow_rate2, rack_heat_load2]])
    normalized_new_params = param_scaler.transform(new_parameters)
    predicted_normalized_coeffs = np.array([model(*normalized_new_params.T) for model in rbf_models]).T
    predicted_coeffs = coeff_scaler.inverse_transform(predicted_normalized_coeffs)
    predicted_state = np.dot(pod_modes, predicted_coeffs.T)
    adjusted_predicted_state = predicted_state - (12 - supply_temperature) - 273.15  
    predicted_state = adjusted_predicted_state.flatten()
    return predicted_state


def update_temperature_data_cgns(solution_path, predicted_state_flat):
    """
    Updates the temperature data in a CGNS file with the provided predicted values
    whihc can be used for visualiztion in paraview web/ paraview
    Args:
        solution_path (str): Path to the CGNS file.
        predicted_state_flat (np.array): Flattened array of predicted temperature values.

    Raises:
        KeyError: If the temperature data path is not found in the CGNS file.
        Exception: If any other error occurs during the file operation.
    """
    try:
        with h5py.File(solution_path, 'r+') as f:
            temperature_path = 'Base/Zone/FlowSolution.N:1/Temperature/ data'  # Corrected the path format
            if temperature_path in f:
                f[temperature_path][:] = predicted_state_flat
                print(f"Temperature data successfully updated in {solution_path}.")
            else:
                raise KeyError(f"Path {temperature_path} not found in the file.")
    except Exception as e:
        print(f"Failed to update temperature data: {e}")