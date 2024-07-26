"""
Module: app.py
Authors:
- Najee Stubbs {nistubbs@uark.edu}, University of Arkansas, Mechanical Engineering Dept.
- Tyler Kuper {tdkuper@uark.edu}, University of Arkansas, Computer Science Dept. 
Date: July 24, 2024

Description:
This module initializes a Flask web application for interacting with the TSRM API.
It provides endpoints for uploading files, running simulations, and retrieving results.
""" 

import sys
import os
import logging
import shutil
import atexit
from typing import Any, Dict, List, Optional, Tuple, Type
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_directory)
from src.communication.tsrm_api import TSRMApi
from src.utils.data_handler_util import DataHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Type alias for readability
FileMapping = Dict[Tuple[str,str], Any]

class AppState:
    """
    Class to represent the application state.

    Attributes:
        selected_input_path (str): Path of the selected input file.
        base_directory (str): Base directory of the application.
        file_mapping (FileMapping): Mapping of file types to their details.
        cooling_types (List[str]): List of available cooling types.
        processor_types (List[str]): List of available processor types.
    """
    def __init__(self, file_mapping: FileMapping, cooling_types: List[str], processor_types: List[str]) -> None:
        """
        Initializes the AppState class with the given file mapping, cooling types, 
        and processor types.

        Args:
            file_mapping (FileMapping): 
            cooling_types (List[str]): List of available cooling types
            processor_types (List[str]): List of available processor types.
        """
        self.selected_input_path = None
        self.base_directory = os.path.dirname(__file__)
        self.file_mapping = file_mapping
        self.cooling_types = cooling_types
        self.processor_types = processor_types

    @classmethod
    def set_values_from_api(cls: Type['AppState'], wrapper: 'TSRMApiWrapper') -> 'AppState':
        """
        Class method setting the class variables

        Args:
            wrapper (TSRMAPIWrapper): Instance of the api wrapper class

        Returns:
            AppState: Instance of the app state class with the newly set values
        """
        file_mapping, _ = wrapper.get_file_mapping()
        cooling_types = list(set([key[0] for key in file_mapping.keys()]))
        processor_types = list(set([key[1] for key in file_mapping.keys()]))
        return cls(file_mapping, cooling_types, processor_types)
    
class TSRMApiWrapper:
    """
    A wrapper class for the TSRMApi to handle API interactions.

    Attributes:
        api (TSRMApi): Instance of the TSRMApi class.
    """
    def __init__(self, api: TSRMApi)-> None:
        self.api = api
        self.data_handler = DataHandler()

    def get_file_mapping(self) -> Tuple[FileMapping, str]:
        """
        Calls the dynamic file mapping function in TSRM API

        Returns:
            Dictionary: File mapping for cooling and processor types
            string: Path directory to the input template json file
        """
        return self.data_handler.get_dynamic_file_mapping()

    def run_simulation(self, user_file_path: Optional[str] = None, *params: Any) -> Optional[str]:
        """
        Calls a TSRM API function to generate and run the simulation using either
        a user-provided JSON file or manually input values.

        Args:
            input_path (string, optional): Path of the user-provided JSON file. Defaults to None.
            *params (optional): Variables for cooling type, processor type, heat transfer coefficient,
            ambient temperature, processor temperature, and initial temperature

        Returns:
            string: Path of resulting simulation output 
        """
        try:
            if user_file_path:
                return self.api.gen_and_run_sim(user_file_path)
            else:
                return self.api.gen_and_run_sim(None, *params)
        except Exception as e:
            print(f"Error occurred in run_simulation: {e}")
            return None
        
    def stop_simulation(self) -> bool:
        """
        Calls the TSRM API function to quit the matlab engine and stop the simulation
        """ 
        try:
            return self.api.stop_simulation()
        except Exception as e:
            print(f"Error occurred in stop_simulation: {e}")

api = TSRMApi()
wrapper = TSRMApiWrapper(api)
state = AppState.set_values_from_api(wrapper)

stop_simulation_flag = False

@app.route("/")
def index() -> str:
    return render_template('index.html', cooling_types=state.cooling_types, processor_types=state.processor_types)

@app.route('/download_results', methods=['POST'])
def download_results() -> Any:
    if request.method == 'POST':
        filepath = os.path.join(parent_directory, app.config['UPLOAD_FOLDER'], "output.json")
        return send_file(filepath, as_attachment=True)

@app.route('/run_simulation', methods=['POST'])
def run_simulation() -> Any:
    global stop_simulation_flag
    stop_simulation_flag = False  # Reset the flag before starting
    user_file_path = None
    if 'input-file' in request.files:
        input_file = request.files['input-file']
        if input_file.filename != '':
            filename = secure_filename(input_file.filename)
            user_file_path = os.path.join(parent_directory, app.config['UPLOAD_FOLDER'], filename)
            input_file.save(user_file_path)
    logging.info("Starting simulation thread...")
    simulation_output_data = run_simulation_thread(request.form, user_file_path)
    output_path = os.path.join(parent_directory, app.config['UPLOAD_FOLDER'], "output.json")
    with open(output_path, 'w') as file:
        file.write(simulation_output_data)
    return jsonify({
        'status': 'Simulation completed!'
    })

def run_simulation_thread(form_data: Dict[str, str], user_file_path: Optional[str]) -> Optional[str]:
    global stop_simulation_flag
    simulation_output_data = None

    input_option = form_data.get('input-option')
    if input_option == 'file':
        if user_file_path:
            simulation_output_data = wrapper.run_simulation(user_file_path=user_file_path)
    else:
        try:
            simulation_output_data = wrapper.run_simulation(
                None,
                form_data['cooling-method'],
                form_data['processor-type'],
                int(form_data['heat-transfer-coefficient']),
                int(form_data['ambient-temperature']),
                int(form_data['processor-temperature']),
                int(form_data['initial-temperature'])
            )
        except KeyError as e:
            logging.error(f"Simulation failed due to missing key: {e}")

    # Checks for stop simulation flag
    if stop_simulation_flag:
        logging.info("Simulation stopped.")
        return None
 
    if simulation_output_data:
        logging.info("Simulation completed!")
    else:
        logging.info("Simulation failed.")
    return simulation_output_data

@app.route('/view_results', methods=['GET'])
def view_results() -> Any:
    try:
        output_file_path = os.path.join(parent_directory, app.config['UPLOAD_FOLDER'], 'output.json')
        # Return the JSON file
        return send_file(output_file_path, mimetype='application/json')
    except Exception as e:
        logging.error(f"Error retrieving results: {e}")
        return jsonify({'error': 'Failed to retrieve results.'}), 500

@app.route('/stop_simulation', methods=['POST'])
def stop_simulation() -> Any:
    global stop_simulation_flag 
    stop_simulation_flag = True  # Set the flag to stop the simulation
    wrapper.stop_simulation()  # Stop the simulation via the API
    return jsonify({'status': 'Simulation stopped.'}), 200

def cleanup_upload_folder() -> None:
    upload_path = os.path.join(parent_directory, app.config['UPLOAD_FOLDER'])
    try:
        if os.path.exists(upload_path):
            shutil.rmtree(upload_path)
            logging.info(f"Deleted upload folder: {upload_path}")
    except Exception as e:
        logging.error(f"Error deleting upload folder: {e}")

atexit.register(cleanup_upload_folder)

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host="127.0.0.1", port=8080, debug=True)