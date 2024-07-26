"""
Module: tsrm_api.py
Authors:
- Najee Stubbs {nistubbs@uark.edu}, University of Arkansas, Mechanical Engineering Dept.
- Tyler Kuper {tdkuper@uark.edu}, University of Arkansas, Computer Science Dept. 
Date: July 24, 2024

Description:
tsrm_api.py gives the user an interface for managing the thermal stack reliability simulations. This module
has functionalities to read JSON template files, extract parameters, and modify those template for use in
the parapower simulation using ParaPowerPythonAPI and ReliabilityCalc.
"""

import os
import json
import argparse
from typing import Dict, Optional, Tuple, Any
from src.communication.parapower_python_api import ParaPowerPythonApi
from src.reliability.reliability_calc import ReliabilityCalc
from src.utils.data_handler_util import DataHandler

class TSRMApi:
    """
    A class to interface with the thermal stack reliability simulations.

    Attributes:
        ppa (ParaPowerPythonApi): Instance of the ParaPowerPythonApi class.
        rel (ReliabilityCalc): Instance of the ReliabilityCalc class.
        data_handler (DataHandler): Instance of the DataHandler class.
    """
    def __init__(self) -> None:
        """
        Initializes the TSRMApi class with instances of ParaPowerPythonApi, ReliabilityCalc, and DataHandler.
        """
        self.ppa = ParaPowerPythonApi()
        self.rel = ReliabilityCalc()
        self.data_handler = DataHandler()

    def __run_sim_with_modified_template(self, therm_mech_input_data: str) -> Optional[str]:
        """
        Runs the simulation and performs reliability calculations using
        the modified thermal stack template generated

        Args:
            therm_mech_input_data (string): JSON string of the generated input data

        Returns:
            string: JSON string of the reliability calculations output
        """
        
        try:
            # Run the MATLAB Simulation
            sim_output_data = self.ppa.run_matlab_sim(therm_mech_input_data)
            
            # Perform reliability calculations using the output path from the simulation
            reliability_output_data = self.rel.generate_calculation(sim_output_data)
            
            return reliability_output_data
        except Exception as e:
            print(f"An error occurred during simulation: {e}")
            return None

    def gen_and_run_sim(self, user_file_path: Optional[str] = None, *params: Any) -> Optional[str]:
        """
        Generates customized input file using either a user-provided JSON file or
        manually input parameters and runs the simulation with the new input file.

        Args:
            user_file_path (string, optional): Path of the user-provided JSON file. Defaults to None.
            *params (Any): Variables for cooling type, processor type, heat transfer coefficient,
                           ambient temperature, processor temperature, and initial temperature

        Returns:
            string: JSON string of the reliability calculations output
        """
        if user_file_path:
            with open(user_file_path, 'r', encoding='utf-8') as json_file:
                input_data = json.load(json_file)
            if input_data["type"] == "advanced":
                return self.__run_sim_with_modified_template(json.dumps(input_data))
            elif input_data["type"] == "basic":
                params = self.data_handler.extract_parameters(user_file_path)
        therm_mech_input_data = self.data_handler.modify_thermal_stack_template(*params)
        return self.__run_sim_with_modified_template(therm_mech_input_data)
    
    def stop_simulation(self) -> bool:
        """
        Stops the matlab simulation by terminating the subprocess.

        Returns:
            bool: True if the simulation was successfully stopped, False otherwise.
        """
        return self.ppa.stop_matlab_sim()

#---------------------------Use software from the commandline with JSON file / Use without GUI---------------------------#
"""
Run tsrm_api.py from the command line using:
    > python -m src.communication.tsrm_api libs/gui_json_template/json_option_input_template.json

Note: This requires you to be inside the TSRM_V1 directory first.
"""

def main(json_file_path: str) -> None:
    # Normalize the file path to ensure compatibility with the OS
    json_file_path = os.path.normpath(json_file_path)
    
    api = TSRMApi()
    result = api.gen_and_run_sim(user_file_path=json_file_path)
    
    if result:
        print(f"Simulation completed successfully. Reliability calculations output: {result}")
    else:
        print("Simulation failed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run thermal stack reliability simulation using a JSON file.')
    parser.add_argument('json_file_path', type=str, help='Path to the JSON file')
    
    args = parser.parse_args()
    
    main(args.json_file_path)