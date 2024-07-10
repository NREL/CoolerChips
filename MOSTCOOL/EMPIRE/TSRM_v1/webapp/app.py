import threading
import json
import shutil
import os
import time
from PIL import Image, ImageTk
from src.communication.tsrm_api import TSRMApi
from src.utils.simData_util import SimData
import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class AppState:
    def __init__(self, base_directory, file_mapping, cooling_types, processor_types):
        self.selected_input_path = None
        self.base_directory = base_directory
        self.file_mapping = file_mapping
        self.cooling_types = cooling_types
        self.processor_types = processor_types

    @classmethod
    def set_values_from_api(cls, simdata, wrapper):
        """
        Class method setting the class variables

        Args:
            simdata (SimData): Instance of the sim data utility class
            wrapper (TSRMAPIWrapper): Instance of the api wrapper class

        Returns:
            AppState: Instance of the app state class with the newly set values
        """
        base_directory = simdata.find_base_dir("TSRM_v1")
        file_mapping, _ = wrapper.get_file_mapping()
        cooling_types = list(set([key[0] for key in file_mapping.keys()]))
        processor_types = list(set([key[1] for key in file_mapping.keys()]))
        return cls(base_directory, file_mapping, cooling_types, processor_types)
    
class TSRMApiWrapper:
    def __init__(self, api):
        self.api = api

    def get_file_mapping(self):
        """
        Calls the dynamic file mapping function in TSRM API

        Returns:
            Dictionary: File mapping for cooling and processor types
            string: Path directory to the input template json file
        """
        return self.api.get_dynamic_file_mapping()

    def run_simulation(self, user_file_path=None, *params):
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
        
    def stop_simulation(self):
        """
        Calls the TSRM API function to quit the matlab engine and stop the simulation
        """ 
        try:
            return self.api.stop_simulation()
        except Exception as e:
            print(f"Error occurred in stop_simulation: {e}")

api = TSRMApi()
wrapper = TSRMApiWrapper(api)
simdata = SimData()
state = AppState.set_values_from_api(simdata, wrapper)

stop_simulation_flag = False

@app.route("/")
def index():
    return render_template('index.html', cooling_types=state.cooling_types, processor_types=state.processor_types)

@app.route('/download_results', methods=['POST'])
def download_results():
    if request.method == 'POST':
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], "output.json")
        return send_file(filepath, as_attachment=True)

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    global stop_simulation_flag
    stop_simulation_flag = False  # Reset the flag before starting
    user_file_path = None
    if 'input_file' in request.files:
        input_file = request.files['input_file']
        if input_file.filename != '':
            filename = secure_filename(input_file.filename)
            user_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            input_file.save(user_file_path)
    logging.info("Starting simulation thread...")
    simulation_output_path = run_simulation_thread(request.form, user_file_path)
    shutil.move(simulation_output_path, os.path.join(app.config['UPLOAD_FOLDER'], "output.json"))
    simulation_output_path = os.path.join(app.config['UPLOAD_FOLDER'], "output.json")
    return jsonify({
        'status': 'Simulation started',
        'output': simulation_output_path
    })

def run_simulation_thread(form_data, user_file_path):
    global stop_simulation_flag
    countdown = 5
    simulation_output_path = None

    input_option = form_data.get('input_option')
    if input_option == 'file':
        if user_file_path:
            simulation_output_path = wrapper.run_simulation(user_file_path=user_file_path)
    else:
        try:
            simulation_output_path = wrapper.run_simulation(
                None,
                form_data['cooling_method'],
                form_data['processor_type'],
                int(form_data['heat_transfer_coefficient']),
                int(form_data['ambient_temperature']),
                int(form_data['processor_temperature']),
                int(form_data['initial_temperature'])
            )
        except KeyError as e:
            logging.error(f"Simulation failed due to missing key: {e}")
            
    while countdown > 0:
        if stop_simulation_flag:
            logging.info("Simulation stopped.")
            return None  # Simulation stopped early
        countdown -= 1
        time.sleep(1)  # Simulate work by waiting for 1 second

    if stop_simulation_flag:
        logging.info("Simulation stopped.")
        return None
    
    if simulation_output_path:
        logging.info("Simulation completed!")
    else:
        logging.info("Simulation failed.")

    return simulation_output_path

@app.route('/view_results', methods=['GET'])
def view_results():
    try:
        # Assuming the output file is named 'output.json' and located in the uploads folder
        output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.json')
        # Return the JSON file
        return send_file(output_file_path, mimetype='application/json')
    except Exception as e:
        logging.error(f"Error retrieving results: {e}")
        return jsonify({'error': 'Failed to retrieve results.'}), 500

@app.route('/stop_simulation', methods=['POST'])
def stop_simulation():
    global stop_simulation_flag 
    stop_simulation_flag = True  # Set the flag to stop the simulation
    logging.info("Simulation stop requested.")
    wrapper.stop_simulation()  # Stop the simulation via the API
    return jsonify({'status': 'Simulation stopped.'}), 200


if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host="127.0.0.1", port=8080, debug=True)