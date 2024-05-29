import os
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Directory to save the downloaded files
DOWNLOAD_DIRECTORY = os.path.join(os.getcwd(), 'Resources')

# Ensure the directory exists
os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)

# Mapping of locations to their EPW file URLs
location_to_url = {
    "Sterling-Washington":
    "https://github.com/NREL/EnergyPlus/raw/develop/weather/USA_VA_Sterling-Washington.Dulles.Intl.AP.724030_TMY3.epw",
    "Phoenix-Sky Harbor":
    "https://github.com/NREL/EnergyPlus/raw/develop/weather/USA_AZ_Phoenix-Sky.Harbor.Intl.AP.722780_TMY3.epw",
    "Fresno":
    "https://github.com/NREL/EnergyPlus/raw/develop/weather/USA_CA_Fresno.Air.Terminal.723890_TMY3.epw",
    "Boulder":
    "https://github.com/NREL/EnergyPlus/raw/develop/weather/USA_CO_Boulder-Broomfield-Jefferson.County.AP.724699_TMY3.epw",
    "Miami":
    "https://raw.githubusercontent.com/NREL/EnergyPlus/develop/weather/USA_FL_Miami.Intl.AP.722020_TMY3.epw"
}


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


if __name__ == "__main__":
  app.run("0.0.0.0", debug=True)
