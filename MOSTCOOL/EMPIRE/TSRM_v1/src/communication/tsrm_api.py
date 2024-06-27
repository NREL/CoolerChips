"""
Module: tsrm_api.py
Authors:
- Najee Stubbs {nistubbs@uark.edu}, University of Arkansas, Mechanical Engineering Dept.
- Tyler Kuper {tdkuper@uark.edu}, University of Arkansas, Computer Science Dept. 
Date: June 20, 2024

Description:
tsrm_api.py gives the user an interface for managing the thermal stack reliability simulations. This module
has functionalities to read JSON template files, extract parameters, and modify those template for use in
the parapower simulation using ParaPowerPythonAPI and ReliabilityCalc.
"""

import os
import shutil
import argparse
import json
from src.utils.simData_util import SimData
from src.communication.parapower_python_api import ParaPowerPythonApi
from src.reliability.reliability_calc import ReliabilityCalc

class TSRMApi:
    def __init__(self):
        self.simdata = SimData()
        self.ppa = ParaPowerPythonApi()
        self.rel = ReliabilityCalc()

    def __extract_parameters(self, user_file_path):
        """
        Extracts parameters from a user-provided JSON file for use in
        simulations.

        Args:
            user_file_path (string): Path of the user-provided JSON file

        Returns:
            string: Extracted cooling type value
            string: Extracted processor type value
            string: Extracted heat transfer coefficient value
            string: Extracted ambient temperature value
            string: Extracted processor temperature value
            string: Extracted initial temperature value
        """
        if user_file_path:
            with open(user_file_path, 'r') as json_file:
                input_data = json.load(json_file)
                # Extract values from JSON and set them in the GUI variables
                return input_data["cooling_type"], input_data["processor_type"], input_data["heat_transfer_coef"], input_data["ambient_temp"], input_data["proc_temp"], input_data["initial_temp"]
        else:
            return None

    def __modify_thermal_stack_template(self, cooling_type, processor_type, heat_transfer_coef, ambient_temp, proc_temp, initial_temp):
        """
        Creates an input file for the simulation using provided parameters and choosing
        the appropriate thermal stack template and modifying it with the given parameters

        Args:
            cooling_type (string): Type of cooling system
            processor_type (string): Type of processor
            heat_transfer_coef (int): Heat transfer coefficient
            ambient_temp (int): Ambient temperature
            proc_temp (int): Processor temperature
            initial_temp (int): Initial temperature

        Returns:
            string: Path of the generated input file
        """
        file_mapping, template_dir = self.get_dynamic_file_mapping()
        
        template_path = os.path.join(template_dir, file_mapping[(cooling_type, processor_type)])
        
        input_file_path = self.simdata.create_input_path("TSRM_v1", "therm_mech_inputs", "parapower_config")
        shutil.copyfile(template_path, input_file_path)

        with open(input_file_path, 'r') as json_file:
            input_data = json.load(json_file)

        # Modify the input data with provided parameters
        input_data['ExternalConditions']['h_Xminus'] = heat_transfer_coef
        input_data['ExternalConditions']['h_Xplus'] = heat_transfer_coef
        input_data['ExternalConditions']['h_Yminus'] = heat_transfer_coef
        input_data['ExternalConditions']['h_Yplus'] = heat_transfer_coef
        input_data['ExternalConditions']['h_Zminus'] = heat_transfer_coef
        input_data['ExternalConditions']['h_Zplus'] = heat_transfer_coef
        input_data['ExternalConditions']['Ta_Xminus'] = ambient_temp
        input_data['ExternalConditions']['Ta_Xplus'] = ambient_temp
        input_data['ExternalConditions']['Ta_Yminus'] = ambient_temp
        input_data['ExternalConditions']['Ta_Yplus'] = ambient_temp
        input_data['ExternalConditions']['Ta_Zminus'] = ambient_temp
        input_data['ExternalConditions']['Ta_Zplus'] = ambient_temp
        input_data['ExternalConditions']['Tproc'] = proc_temp
        input_data['Params']['Tinit'] = initial_temp

        # Save the modified input data back to the file
        with open(input_file_path, 'w') as json_file:
            json.dump(input_data, json_file, indent=2)

        return input_file_path

    def __run_sim_with_modified_template(self, therm_mech_input_file_path):
        """
        Runs the simulation and performs reliability calculations using
        the modified thermal stack template generated

        Args:
            input_file_path (string): Path of the generated input file.

        Returns:
            string: Path of the reliability calculations output
        """

        try:
            # Run the MATLAB Simulation
            sim_output_path = self.ppa.run_matlab_sim(therm_mech_input_file_path)
            
            # Perform reliability calculations using the output path from the simulation
            reliability_output_path = self.rel.generate_calculation(sim_output_path)
            
            return reliability_output_path
        except Exception as e:
            print(f"An error occurred during simulation: {e}")
            return None

    def get_dynamic_file_mapping(self):
        """
        Reads JSON template files and maps cooling and processor types. Scans
        a directory for JSON files and creates a mapping based on file naming
        conventions.

        Returns:
            Dictionary: File mapping for cooling and processor types
            string: Path directory to the input template json file
        """
        base_directory = self.simdata.find_base_dir("TSRM_v1")
        template_dir = os.path.join(base_directory, "libs", "thermal-stack-config")
        
        file_mapping = {}
        for filename in os.listdir(template_dir):
            if filename.endswith(".json"):
                parts = filename.split('_')
                if len(parts) >= 2:  # Assuming the format is like "CoolingType_ProcessorType.json"
                    cooling_type = parts[0]
                    processor_type = '_'.join(parts[1:]).replace(".json", "")
                    file_mapping[(cooling_type, processor_type)] = filename
        
        return file_mapping, template_dir

    def gen_and_run_sim(self, user_file_path=None, *params):
        """
        Generates customized input file using either a user-provided JSON file or
        manually input parameters and runs the simulation with the new input file.

        Args:
            user_file_path (string, optional): Path of the user-provided JSON file. Defaults to None.
            *params (optional): Variables for cooling type, processor type, heat transfer coefficient,
            ambient temperature, processor temperature, and initial temperature

        Returns:
            string: Path of the reliability calculations output
        """
        if user_file_path:
            params = self.__extract_parameters(user_file_path)
        therm_mech_input_file_path = self.__modify_thermal_stack_template(*params)
        return self.__run_sim_with_modified_template(therm_mech_input_file_path)
    
    def stop_simulation(self):
        """
        Stops the matlab simulation by terminating the subprocess.
        """
        self.ppa.stop_matlab_sim()

#---------------------------Use software from the commandline with JSON file / Use without GUI---------------------------#
"""
Run tsrm_api.py from the command line using:
    > python -m src.communication.tsrm_api libs/gui_json_template/json_option_input_template.json

Note: This requires you to be inside the TSRM_V1 directory first.
"""

def main(json_file_path):
    # Normalize the file path to ensure compatibility with the OS
    json_file_path = os.path.normpath(json_file_path)
    
    api = TSRMApi()
    result = api.gen_and_run_sim(user_file_path=json_file_path)
    
    if result:
        print(f"Simulation completed successfully. Reliability calculations output path: {result}")
    else:
        print("Simulation failed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run thermal stack reliability simulation using a JSON file.')
    parser.add_argument('json_file_path', type=str, help='Path to the JSON file')
    
    args = parser.parse_args()
    
    main(args.json_file_path)
