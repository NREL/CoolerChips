"""
Module: parapower_python_api.py
Authors:
- Najee Stubbs {nistubbs@uark.edu}, University of Arkansas, Mechanical Engineering Dept.
- Tyler Kuper {tdkuper@uark.edu}, University of Arkansas, Computer Science Dept.
Date: July 10, 2024

Description:
This module provides an interface to run ParaPower simulations using a compiled MATLAB executable.
It utilizes the SimData utility to generate output paths for simulation results. The `run_matlab_sim` 
function initializes the MATLAB engine and executes the simulation based on the provided input JSON file, 
returning the path to the resulting output file.
"""

import os
import subprocess
import logging
import tempfile

class ParaPowerPythonApi:
    def __init__(self):
        self.process = None

    def run_matlab_sim(self, input_data):
        
        # Find the base directory for the TSRM_v1 project
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

        # Path to the directory containing the compiled MATLAB executable
        compiled_dir = os.path.normpath(os.path.join(base_dir, "src", "therm_mech", "TSRM_ParaPower"))

        # Path to the compiled MATLAB executable
        matlab_executable = os.path.normpath(os.path.join(compiled_dir, "parapower_matlab_api.exe"))

        # Create a temporary file to hold the JSON output
        output_file = tempfile.NamedTemporaryFile(delete=False)
        output_file_path = output_file.name
        output_file.close()

        # Call the compiled MATLAB executable with the JSON strings
        logging.info("Starting subprocess...")
        command = [matlab_executable, input_data, compiled_dir, output_file_path]
        self.process = subprocess.Popen(command, stderr=subprocess.PIPE, text=True)
        _, stderr = self.process.communicate()

        logging.debug(f"MATLAB stderr: {stderr}")

        if self.process.returncode != 0:
            logging.error(f"MATLAB process failed with return code {self.process.returncode}")
            os.remove(output_file_path)
            raise subprocess.CalledProcessError(self.process.returncode, matlab_executable, stderr=stderr)

        # Read the output JSON from the temporary file
        with open(output_file_path, 'r') as file:
            output_data = file.read().strip()

        # Clean up the temporary file
        os.remove(output_file_path)

        if not output_data:
            logging.error("No JSON output received from MATLAB")
            raise ValueError("No JSON output received from MATLAB")

        #logging.info(f"Output JSON from MATLAB: {output_data}")
        return output_data

    def stop_matlab_sim(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
            logging.info("Subprocess terminated.")
            return True
        else:
            logging.warning("No subprocess to terminate")
            return False

