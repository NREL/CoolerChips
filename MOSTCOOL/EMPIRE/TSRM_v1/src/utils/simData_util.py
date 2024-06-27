"""
Module: simdata_util.py
Authors:
- Najee Stubbs {nistubbs@uark.edu}, University of Arkansas, Mechanical Engineering Dept.
- Tyler Kuper {tdkuper@uark.edu}, University of Arkansas, Computer Science Dept. 
Date: June 20, 2024

Description:
simData_util.py provides utility function for managing simulation data paths. The module finds the
base directory for the app and can create input and output paths.
""" 

# utility.py
import os
from datetime import datetime

class SimData:
    def find_base_dir(self, target_dir):
        """
        Finds the base directory up to a specified target directory. Traverses
        the directory hierarchy to locate the target directory.

        Args:
            target_dir (string): Name of the target directory to find.

        Raises:
            FileNotFoundError: If target directory is not foudn in the path
            hierarchy

        Returns:
            string: Path of the base directory
        """
        script_directory = os.path.dirname(os.path.abspath(__file__))
        # Traverse up to find the target directory
        while True:
            if target_dir in os.listdir(script_directory):
                break
            parent_directory = os.path.dirname(script_directory)
            if parent_directory == script_directory:  # reached the root directory
                raise FileNotFoundError(f"'{target_dir}' directory not found in the path hierarchy.")
            script_directory = parent_directory
        return os.path.join(script_directory, target_dir)

    def create_input_path(self, target_dir, input_type, prefix):
        """
        Creates a path for the input JSON file of the simulation, including a 
        timestamp.

        Args:
            target_dir (string): Name of the target directory
            input_type (string): Type of input (e.g. therm_mech_inputs)
            prefix (string): Prefix for the input file name.

        Returns:
            string: Path of generated input JSON file
        """
        base_directory = self.find_base_dir(target_dir)
        results_dir = os.path.join(base_directory, "simData", "inputs", input_type)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_file_name = f"{prefix}_{timestamp}.json"
        return os.path.join(results_dir, input_file_name)

    def create_output_path(self, target_dir, output_type, prefix):
        """
        Creates a path for the output JSON file of the simulation, including a
        timestamp.

        Args:
            target_dir (string): Name of the target directory
            output_type (string): Type of output (e.g. therm_mech_results)
            prefix (string): Prefix for the output file name

        Returns:
            string: Path of the generated output JSON file
        """
        base_directory = self.find_base_dir(target_dir)
        results_dir = os.path.join(base_directory, "simData", "results", output_type)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_name = f"{prefix}_{timestamp}.json"
        return os.path.join(results_dir, output_file_name)