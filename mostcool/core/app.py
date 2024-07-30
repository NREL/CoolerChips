import mostcool.thermal.update_cgns as update_cgns
import mostcool.thermal.trame_ as trame_
from flask import Flask, render_template, request, jsonify
import subprocess
import definitions
import os
import requests
from threading import Thread, Lock
import pandas as pd
from pathlib import Path
import plotly.express as px
import re
from time import sleep

app = Flask(__name__, 
            template_folder="../assets/templates",
            static_folder="../assets/static")

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

# Define the max value for the progress bar
progress_max = definitions.TOTAL_SECONDS - definitions.TIMESTEP_PERIOD_SECONDS  # First time step is skipped

progress = 0
progress_lock = Lock()
server_log = '/app/mostcool/core/Server_federate.log'
pattern = re.compile(r'at time (\d+\.?\d*)')

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
            ["helics", "run", "--path=/app/mostcool/core/runner.json"],
            ["echo", "Simulation completed."]
            # Add your actual simulation commands here
        ]
        
        for i, command in enumerate(commands):
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
            process.wait()
            print(f"Command '{' '.join(command)}' finished with exit code {process.returncode}")
            # Simulate progress
            with progress_lock:
                progress_value = (i + 1) / len(commands) * 100
                global progress
                progress = progress_value
            sleep(2)  # Simulate some processing time
        print("Simulation completed.")
        ep_results = pd.read_csv("/app/Output/eplusout.csv")
        ep_results = ep_results.drop(ep_results.index[:1])  # Drop the initial strange values
        self.results = fix_results(ep_results)

@app.route("/")
def home():
    return render_template('home.html')

@app.route('/simulation')
def simulation():
    return render_template('simulation.html', total_seconds=progress_max)

@app.route('/simulation-setup')
def simulation_setup():
    return render_template('simulation-setup.html')

@app.route('/step-1')
def step_1():
    weather_epw_path = os.path.join(DOWNLOAD_DIRECTORY, "weather.epw")
    epw_location = None
    if os.path.exists(weather_epw_path):
        epw_location = get_epw_location(weather_epw_path)
    return render_template('step-1.html', epw_location=epw_location)

@app.route('/step-2')
def step_2():
    return render_template('step-2.html')

@app.route('/step-3')
def step_3():
    return render_template('step-3.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/results/building_energy')
def results_building_energy():
    return render_template('results_building_energy.html')

@app.route('/get_results')
def get_results():
    try:
        # Load the simulation results
        ep_results = pd.read_csv("/app/Output/eplusout.csv")
        ep_results = ep_results.drop(ep_results.index[:1])  # Drop the initial strange values
        results = fix_results(ep_results)
        
        # Return the columns as JSON
        return jsonify(results.columns.tolist())
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

@app.route('/get_available_variables')
def get_available_variables():
    try:
        ep_results = pd.read_csv("/app/Output/eplusout.csv")
        ep_results = ep_results.drop(ep_results.index[:1])  # Drop the initial strange values
        results = fix_results(ep_results)
        variables = results.columns.tolist()
        return jsonify({'variables': variables})
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

@app.route('/get_building_energy_results')
def get_building_energy_results():
    try:
        left_variable = request.args.get('left_variable', 'Cooling:Electricity [J]')  # Default to a specific variable
        right_variable = request.args.get('right_variable', 'Maximum CPU Temperature [C]')  # Default to a specific variable

        ep_results = pd.read_csv("/app/Output/eplusout.csv")
        ep_results = ep_results.drop(ep_results.index[:1])  # Drop the initial strange values
        results = fix_results(ep_results)
        
        if left_variable not in results.columns or right_variable not in results.columns:
            return jsonify({'status': 'Error', 'message': 'Variable not found'}), 400
        
        # Generate the Plotly plot for the selected variables
        fig = px.line(results, x=results.index, y=left_variable, title=f"{left_variable} vs {right_variable}", color_discrete_sequence=['firebrick'], labels={left_variable: left_variable})

        # Add the right y-axis
        right_trace = px.line(results, x=results.index, y=right_variable, labels={right_variable: right_variable}).data[0]
        right_trace.update(yaxis='y2', name=right_variable)
        fig.add_trace(right_trace)

        # Customize the layout to include a secondary y-axis, a legend, and a white background
        fig.update_layout(
            yaxis=dict(
                title=left_variable
            ),
            yaxis2=dict(
                title=right_variable,
                overlaying='y',
                side='right'
            ),
            xaxis=dict(
                tickformat='%m-%d %H:%M'
            ),
            legend=dict(
                title='Variables',
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            showlegend=True,
            plot_bgcolor='white',  # Set plot background color to white
            paper_bgcolor='white'  # Set the paper background color to white
        )
        
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
        if os.path.isfile(server_log):
            os.remove(server_log) # Let's start from the beginning
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

@app.route('/get_progress', methods=['GET'])
def get_progress():
    with progress_lock:
        progress = 0
        if os.path.isfile(server_log):
            with open(server_log, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    match = pattern.search(last_line)
                    if match:
                        time = float(match.group(1))
                        progress = time
        return jsonify({'progress': progress})

@app.route('/get_progress_max', methods=['GET'])
def get_progress_max():
    return jsonify({'progress_max': progress_max})

@app.route('/server-thermal-profiles')
def server_thermal_profiles():
    return render_template('server_thermal_profiles.html')

@app.route('/run-paraview', methods=['POST'])
def run_paraview():
    data = request.json
    velocity = int(data['velocity'])
    server_temp = int(data['server_temp'])
    cpu_load = float(data['cpu_load'])
    
    try:
        print("updating cgns")
        update_cgns.predict_temperature(velocity=velocity, CPU_load_fraction=cpu_load, inlet_server_temperature=server_temp)
        print("updated cgns")
        subprocess.Popen(['python', '/app/mostcool/thermal/trame_.py', 
                          '--host', '0.0.0.0', 
                          '--port', '1234'])
        return jsonify({'status': 'success'})
    except OSError as e:
        if e.errno == 98:  # Address already in use
            return jsonify({'status': 'warning', 'message': 'Address already in use'})
        else:
            return jsonify({'status': 'error', 'error': str(e)})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=False)
