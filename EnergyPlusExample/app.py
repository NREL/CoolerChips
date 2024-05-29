import os
import requests
from flask import Flask, render_template, request, jsonify
from threading import Thread
import subprocess
from time import sleep
import pandas as pd
from pathlib import Path
import plotly.express as px

app = Flask(__name__)

# Directory to save the downloaded files
DOWNLOAD_DIRECTORY = os.path.join(os.getcwd(), 'Resources')

# Ensure the directory exists
os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)

# Mapping of locations to their EPW file URLs
location_to_url = {
    "Sterling-Washington": "https://github.com/NREL/EnergyPlus/raw/develop/weather/USA_VA_Sterling-Washington.Dulles.Intl.AP.724030_TMY3.epw",
    "Phoenix-Sky Harbor": "https://github.com/NREL/EnergyPlus/raw/develop/weather/USA_AZ_Phoenix-Sky.Harbor.Intl.AP.722780_TMY3.epw",
    "Fresno": "https://github.com/NREL/EnergyPlus/raw/develop/weather/USA_CA_Fresno.Air.Terminal.723890_TMY3.epw",
    "Boulder": "https://github.com/NREL/EnergyPlus/raw/develop/weather/USA_CO_Boulder-Broomfield-Jefferson.County.AP.724699_TMY3.epw",
    "Miami": "https://raw.githubusercontent.com/NREL/EnergyPlus/develop/weather/USA_FL_Miami.Intl.AP.722020_TMY3.epw"
}

def fix_results(results):

    def fix_datetime(dt_str):
        date_part, time_part = dt_str.split()
        if time_part == '24:00:00':
            dt = pd.to_datetime(date_part, format='%m/%d') + pd.Timedelta(days=1)
            return dt.strftime(' %m/%d') + ' 00:00:00'
        else:
            return dt_str
    results['Date/Time'] = results['Date/Time'].apply(fix_datetime)
    results['Date/Time'] = pd.to_datetime(results['Date/Time'], format=' %m/%d %H:%M:%S')
    results.set_index('Date/Time', inplace=True)
    results.columns = results.columns.str.replace(r'\(TimeStep\)', '', regex=True)
    if Path("Output/time_series_data.csv").exists():
        time_series = pd.read_csv("Output/time_series_data.csv")
        time_series = time_series.drop(time_series.index[:1])
        results["Maximum CPU Temperature [C]"] = time_series["Value"].values
    else:
        print(f"Thermal model CSV output not found at Output/time_series_data.csv")
    return results

def get_epw_location(file_path):
    try:
        with open(file_path, 'r') as file:
            first_line = file.readline()
            parts = first_line.split(',')
            if parts[0] == 'LOCATION' and len(parts) > 2:
                return f"{parts[1]}, {parts[2]}"
    except Exception as e:
        print(f"Error reading EPW file: {e}")
    return None

class Simulator:
    def __init__(self, idf_path, epw_path, control_option, datacenter_location):
        self.idf = idf_path
        self.epw = epw_path
        self.control_option = control_option
        self.datacenter_location = datacenter_location

    def run(self):
        commands = [
            ["echo", "Running simulation..."],
            ["helics", "run", "--path=runner.json"],
            ["echo", "Simulation completed."]
            # Add your actual simulation commands here
        ]
        for command in commands:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
            process.wait()
            print(f"Command '{' '.join(command)}' finished with exit code {process.returncode}")
        # Simulate some processing time
        sleep(2)
        print("Simulation completed.")
        ep_results = pd.read_csv("Output/eplusout.csv")
        ep_results = ep_results.drop(ep_results.index[:1])  # Drop the initial strange values
        self.results = self.fix_results(ep_results)





@app.route("/")
def home():
    return render_template('home.html')

@app.route('/simulation')
def simulation():
    return render_template('simulation.html')

@app.route('/pre-simulation')
def pre_simulation():
    weather_epw_path = os.path.join(DOWNLOAD_DIRECTORY, "weather.epw")
    epw_location = None
    if os.path.exists(weather_epw_path):
        epw_location = get_epw_location(weather_epw_path)
    return render_template('pre-simulation.html', epw_location=epw_location)

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/get_results')
def get_results():
    try:
        # Load the simulation results
        ep_results = pd.read_csv("Output/eplusout.csv")
        ep_results = ep_results.drop(ep_results.index[:1])  # Drop the initial strange values
        results = fix_results(ep_results)
        
        # Generate the Plotly plot
        fig = px.line(results, x=results.index, y="Maximum CPU Temperature [C]", title="Simulation Results")
        
        # Serialize the Plotly figure
        fig_json = fig.to_json()
        
        return jsonify(fig_json)
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

@app.route('/post')
def post_simulation():
    return render_template('post.html')

@app.route('/download_epw', methods=['POST'])
def download_epw():
    location = request.form['location']
    epw_url = location_to_url.get(location)

    if not epw_url:
        return "Invalid location", 400

    response = requests.get(epw_url)
    if response.status_code == 200:
        file_path = os.path.join(DOWNLOAD_DIRECTORY, "weather.epw")
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return "File downloaded and saved successfully", 200
    else:
        return "Failed to download file", 500

@app.route('/start_simulation', methods=['POST'])
def start_simulation():
    try:
        # Extract parameters from the request if needed
        idf_path = request.form.get('idf_path', 'default_idf_path')
        epw_path = os.path.join(DOWNLOAD_DIRECTORY, "weather.epw")
        control_option = request.form.get('control_option', 'default_control_option')
        datacenter_location = request.form.get('datacenter_location', 'default_datacenter_location')

        # Initialize the simulator
        simulator = Simulator(idf_path, epw_path, control_option, datacenter_location)

        def run_simulator():
            simulator.run()

        # Start the simulation in a new thread
        sim_thread = Thread(target=run_simulator)
        sim_thread.start()

        return jsonify({'status': 'Simulation started'})

    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

if __name__ == "__main__":
    app.run("0.0.0.0", debug=False)
