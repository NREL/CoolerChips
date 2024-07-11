"""
Module: reliability_calc.py
Authors:
- Najee Stubbs {nistubbs@uark.edu}, University of Arkansas, Mechanical Engineering Dept.
- Tyler Kuper {tdkuper@uark.edu}, University of Arkansas, Computer Science Dept. 
Date: July 10, 2024

Description:
reliability_calc.py calculates the reliability of various componenets based on temperature data extracted
from ParaPower simulation results and builds an output path for the reliability calculation results.
"""

import json
from libs.reliability_lib import (
    processor_calc,
    tim_calc,
    solder_calc,
    heatspreader_calc,
    heatsink_calc
)
from src.utils.simData_util import SimData

class ReliabilityCalc:
    # Map keywords to their respective functions
    keyword_to_function = {
        "GPU": processor_calc.calculate_reliability,
        "CPU": processor_calc.calculate_reliability,
        "TIM": tim_calc.calculate_reliability,
        "Solder": solder_calc.calculate_reliability,
        "HeatSpreader": heatspreader_calc.calculate_reliability,
        "HeatSink": heatsink_calc.calculate_reliability
    }

    def __init__(self):
        self.simdata = SimData()

    def __extract_data(self, parapower_results_data):
        """
        Extracts features and temperatures from the parapower data for
        reliability calculations

        Args:
            parapower_results_data (string): JSON string of the parapower results

        Returns:
            list: Extracted data that contains features and temperature values
        """
        input_data = json.loads(parapower_results_data)
        
        extracted_data = []
        for data_item in input_data:
            feature = data_item['feature']
            temp_value = data_item['temperature'][1]
            extracted_data.append((feature, temp_value))
        
        return extracted_data

    def __calc_reliability(self, extracted_data):
        """
        Calculates reliability based on extracted temperature features. Maps
        features to their respective reliability calculation functions and 
        computes the results.

        Args:
            extracted_data (list): List of tuples containing feature names and temperature values

        Returns:
            Dictionary: Dictionary containing features and their reliability results
        """  
        reliability_results = {}
        for feature, temperature in extracted_data:
            calc_function = None
            for keyword, func in self.keyword_to_function.items():
                if keyword in feature:
                    # Set function based on feature
                    calc_function = func
                    break
            
            if calc_function:
                # Call the reliability calculation function
                calc_result = calc_function(feature, temperature)
                reliability_results[feature] = calc_result
            else:
                # Skip the features that don't match anything
                pass
                #print(f"Feature '{feature}' was skipped because it did not match any known categories.")
        return reliability_results

    def __build_output_json(self, calc_results):
        """
        Builds the output JSON structure from the reliability calculation results.

        Args:
            calc_results (Dictionary): Dictionary of reliability calculation results

        Returns:
            list: list containing contents of the output json file
        """
        output_json = []
        for feature, calc_result in calc_results.items():  # feature not used but needed for loop
            output_json.append(calc_result)
        return output_json

    def generate_calculation(self, parapower_results_data):
        """
        Main function for extracting features, performing calculations and 
        saving results.

        Args:
            parapower_results_data (string): JSON string of the parapower results

        Returns:
            string: JSON string of the reliability calculation results
        """

        # Extract data based on the parapower results 
        extracted_data = self.__extract_data(parapower_results_data)

        # Calculate reliability based on the extracted data
        calc_results = self.__calc_reliability(extracted_data)

        # Construct the output JSON structure
        output_json_data = self.__build_output_json(calc_results)

        # Output results to an in-memory JSON string
        output_data = json.dumps(output_json_data, indent=4)

        return output_data
