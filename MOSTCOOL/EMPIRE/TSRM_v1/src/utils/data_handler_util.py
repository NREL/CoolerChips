"""
Module: data_handler_util.py
Authors:
- Najee Stubbs {nistubbs@uark.edu}, University of Arkansas, Mechanical Engineering Dept.
- Tyler Kuper {tdkuper@uark.edu}, University of Arkansas, Computer Science Dept. 
Date: July 24, 2024

Description:
Provides utility functions to handle data for thermal stack simulations, including 
reading JSON template files, extracting parameters, and modifying templates for simulations.
""" 

import os
import json
import logging
from typing import Any, Optional, Tuple, Dict

# Type alias for readability
Params = Optional[Tuple[str, str, int, int, int, int]]
DynamicFileMapping = Tuple[Dict[Tuple[str, str], str], str]

class DataHandler: 
	"""
	A class to handle data for thermal stack simulations, including reading JSON template files, 
    extracting parameters, and modifying templates for simulations.
	"""
	def get_dynamic_file_mapping(self) -> DynamicFileMapping:
		"""
        Reads JSON template files and maps cooling and processor types. Scans
        a directory for JSON files and creates a mapping based on file naming
        conventions.

        Returns:
            Dictionary: File mapping for cooling and processor types
            			string: Path directory to the input template json file
        """
		base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
		template_dir = os.path.normpath(os.path.join(base_directory, "libs", "thermal-stack-config"))
        
		file_mapping = {}
		for filename in os.listdir(template_dir):
			if filename.endswith(".json"):
				parts = filename.split('_')
				if len(parts) >= 2:  # Assuming the format is like "CoolingType_ProcessorType.json"
					cooling_type = parts[0]
					processor_type = '_'.join(parts[1:]).replace(".json", "")
					file_mapping[(cooling_type, processor_type)] = filename
        
		return file_mapping, template_dir
	
	def modify_thermal_stack_template(
		self, 
		cooling_type: str, 
		processor_type: str, 
		heat_transfer_coef: int, 
		ambient_temp: int, 
		proc_temp: int, 
		initial_temp: int
	) -> str:
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
            string: Modified input JSON string
        """
		
		file_mapping, template_dir = self.get_dynamic_file_mapping()
		
		template_path = os.path.normpath(os.path.join(template_dir, file_mapping[(cooling_type, processor_type)]))

		with open(template_path, 'r', encoding='utf-8') as json_file:
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

        # Return the modified input data as JSON string
		return json.dumps(input_data)
	
	def extract_parameters(self, user_file_path: str) -> Params:
		"""
        Extracts parameters from a user-provided JSON file for use in simulations.

        Args:
            user_file_path (string): Path of the user-provided JSON file

        Returns:
            Params: Extracted parameters as a tuple containing cooling type, processor type, 
                    heat transfer coefficient, ambient temperature, processor temperature, and initial temperature.
        """
		if user_file_path:
			with open(user_file_path, 'r', encoding='utf-8') as json_file:
				input_data = json.load(json_file)
                # Extract values from JSON and set them in the GUI variables
				return (
					input_data["cooling_type"], 
					input_data["processor_type"], 
					input_data["heat_transfer_coef"], 
					input_data["ambient_temp"], 
					input_data["proc_temp"], 
					input_data["initial_temp"]
				)
		else:
			return None
		
	def type_checker(self) -> None:
		"""
        Placeholder function for type checking. To be implemented as needed.
        """
		return