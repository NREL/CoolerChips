import json
import os
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

    def extract_data(self, parapower_results_path):
        """
        Extracts features and temperatures from the parapower data for
        reliability calculations

        Args:
            parapower_results_path (string): Path of the parapower results file

        Returns:
            list: Extracted data that contains features and temperature values
        """
        with open(parapower_results_path, 'r') as json_file:
            input_data = json.load(json_file)
        
        extracted_data = []
        for data_item in input_data:
            feature = data_item['feature']
            temp_value = data_item['temperature'][1]
            extracted_data.append((feature, temp_value))
        
        return extracted_data

    def calc_reliability(self, extracted_data):
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
                    calc_function = func
                    break
            
            if calc_function:
                # Call the reliability calculation function
                calc_result = calc_function(feature, temperature)
                reliability_results[feature] = calc_result
            else:
                # Skip the features that don't match anything
                print(f"Feature '{feature}' was skipped because it did not match any known categories.")
        return reliability_results

    def build_output_json(self, calc_results):
        """
        Builds the output JSON structure from the reliability calculation results.

        Args:
            calc_results (Dictionary): Dictionary of reliability calculation results

        Returns:
            list: list containing contents of the output json file
        """
        output_json = []
        for feature, calc_result in calc_results.items():
            output_json.append(calc_result)
        return output_json

    def generate_calculation(self, parapower_results_path):
        """
        Main function for extracting features, performing calculations and 
        saving results.

        Args:
            input_file_path (string): Path of the input JSON file

        Returns:
            string: Path of the output JSON file
        """

        simdata = SimData()
        rel_calc = ReliabilityCalc()

        # Extract data based on the parapower results 
        extracted_data = rel_calc.extract_data(parapower_results_path)

        # Calculate reliability based on the extracted data
        calc_results = rel_calc.calc_reliability(extracted_data)

        # Construct the output JSON structure
        output_json_data = rel_calc.build_output_json(calc_results)

        # Generate the output file path
        output_file_path = simdata.create_output_path("TSRM_v1", "reliability_results", "ReliabilityResults")

        # Output results to the JSON file
        with open(output_file_path, 'w') as output_file:
            json.dump(output_json_data, output_file, indent=4)

        # Print the calculation results
        for feature, calc_result in calc_results.items():
            print(f"Feature: {feature}, Calculation Result: {calc_result}")

        return output_file_path

if __name__ == "__main__":
    # For direct execution, use default input paths
    simdata = SimData()
    rel = ReliabilityCalc()
    default_parapower_results_path = os.path.join(simdata.find_base_dir('TSRM_v1'), 'path_to_parapower_results_json_file.json')
    rel.generate_calculation(default_parapower_results_path)
