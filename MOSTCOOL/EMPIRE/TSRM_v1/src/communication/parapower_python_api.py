"""
Module: parapower_python_api.py
Authors:
- Najee Stubbs {nistubbs@uark.edu}, University of Arkansas, Mechanical Engineering Dept.
- Tyler Kuper {tdkuper@uark.edu}, University of Arkansas, Computer Science Dept.
Date: June 20, 2024

Description:
This module provides an interface to run ParaPower simulations using a compiled MATLAB executable.
It utilizes the SimData utility to generate output paths for simulation results. The `run_matlab_sim` 
function initializes the MATLAB engine and executes the simulation based on the provided input JSON file, 
returning the path to the resulting output file.
"""

import os
import subprocess
from src.utils.simData_util import SimData

class ParaPowerPythonApi:
    def __init__(self):
        self.simdata = SimData()
        self.process = None

    def run_matlab_sim(self, input_file_path):
        """
        Runs the ParaPower simulation using the compiled MATLAB executable and returns the output
        file path.

        Args:
            input_file_path (str): Path of the input JSON file for the simulation

        Returns:
            str: Path of the output results JSON file 
        """
        # Generate output file path
        output_file_path = self.simdata.create_output_path("TSRM_v1", "therm_mech_results", "ParaPowerResults")
        
        try:
            # Find the base directory for the TSRM_v1 project
            base_dir = self.simdata.find_base_dir('TSRM_v1')
            
            # Path to the directory containing the compiled MATLAB executable
            compiled_dir = os.path.join(base_dir, "src", "therm_mech", "TSRM_ParaPower")
            
            # Path to the compiled MATLAB executable
            matlab_executable = os.path.join(compiled_dir, "parapower_matlab_api.exe")

            # Call the compiled MATLAB executable
            subprocess.run([matlab_executable, input_file_path, output_file_path, compiled_dir], check=True)
        
        except subprocess.CalledProcessError as e:
            print(f"Simulation was stopped. Error: {e}")
        
        return output_file_path

def main():
    parapower = ParaPowerPythonApi()
    input_file_path = os.path.join(parapower.simdata.find_base_dir('TSRM_v1'), "libs", "thermal-stack-config", "AirCooled_NVIDIA_H100_GPU.json")
    parapower.run_matlab_sim(input_file_path)

if __name__ == "__main__":
    main()