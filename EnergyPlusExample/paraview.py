import numpy as np
import pandas as pd
import h5py
from scipy.interpolate import interp1d
import subprocess

# Read modes and coefficients from CSV files outside the function
Modes = pd.read_csv('/app/ThermalModel_datacenter/Modes.csv')
modes = Modes.to_numpy()

Coeff = pd.read_csv('/app/ThermalModel_datacenter/coeff.csv')
coeff = Coeff.to_numpy()

# Define the velocity range for which the coefficients are known
lower_vel_limit = 6
upper_vel_limit = 15
vel = np.arange(lower_vel_limit, upper_vel_limit+1)

# Example usage (ensure paths are correctly specified):
solution_path = "/app/ThermalModel_datacenter/solution_PythonPOD_Solid_new.cgns"  # Update with the actual path to your solution file
paraview_path = "/Paraview/bin/paraview"  # Ensure this matches your ParaView installation path

def predict_temperature(new_velocity):
    # Interpolate coefficients for each POD mode.
    interp_funcs = [interp1d(vel, coeff[i, :], kind='linear') for i in range(coeff.shape[0])]
    
    # Predict coefficients for the new velocity.
    new_coeff = np.array([f(new_velocity) for f in interp_funcs])
    
    # Calculate the predicted temperature field.
    T_pred = sum(new_coeff[i] * modes[:, i] for i in range(coeff.shape[0]))
    
    # Update the temperature data in the solution file.
    try:
        with h5py.File(solution_path, 'r+') as f:
            temperature_path = 'Base/Zone/FlowSolution.N:1/Temperature/ data'  # Corrected the path format
            if temperature_path in f:
                f[temperature_path][:] = T_pred
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
        raise RuntimeError(f"Failed to launch ParaView: {e}")


if __name__ == '__main__':
 

    # Call the function with an example new velocity
    predict_temperature(new_velocity=10)