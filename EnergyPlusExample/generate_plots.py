import subprocess
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pathlib import Path
import sys

def fix_datetime(dt_str):
    date_part, time_part = dt_str.split()
    # Split the date and time
    # Only adjust if time is '24:00:00', else return the original datetime string
    if time_part == '24:00:00':
        # Convert to datetime object to easily add a day
        dt = pd.to_datetime(date_part, format='%m/%d') + pd.Timedelta(days=1)
        
        # Replace '24:00:00' with '00:00:00' and format the datetime back to string
        # Adjust the format if your date includes the year or other components
        return dt.strftime(' %m/%d') + '  00:00:00'
    else:
        return dt_str
    
def fix_results(results, thermal_model_timeseries):
    results['Date/Time'] = results['Date/Time'].apply(fix_datetime)
    results['Date/Time'] = pd.to_datetime(results['Date/Time'], format='  %m/%d  %H:%M:%S')
    results.set_index('Date/Time', inplace=True)
    results.columns = results.columns.str.replace(r'\(TimeStep\)', '', regex=True)

    if Path(thermal_model_timeseries).exists():
        time_series = pd.read_csv(thermal_model_timeseries).drop(index=0)
        results["Maximum CPU Temperature [C]"] = time_series["Value"].values
    else:
        print(f"Thermal model CSV output not found at {thermal_model_timeseries}")
    return results

def plot_results(results, y_axis_variable, output_directory):
    plt.clf()
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(results.index, results[y_axis_variable], color='blueviolet', alpha=0.8, label=y_axis_variable)
    ax1.set_ylabel(y_axis_variable)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    fig.autofmt_xdate()
    ax1.set_xlabel("Date/Time")
    
    ax2 = ax1.twinx()
    ax2.plot(results.index, results["Maximum CPU Temperature [C]"], label="Maximum CPU Temperature [C]", color='coral', alpha=0.8, linestyle='--')
    ax2.set_ylabel("Temperature [C]")
    ax2.tick_params(axis='y')

    fig.subplots_adjust(bottom=0.2)
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='lower right')
    
    plt.savefig(Path(output_directory) / f"{y_axis_variable.replace(':', '_').replace(' ', '_').replace('/', '_per_')}.png")
    plt.close()

def create_plots(data_file, thermal_model_file, output_directory):

    if not Path(data_file).exists():
        print(f"Data file not found: {data_file}")
        sys.exit(1)
    results = pd.read_csv(data_file).drop(index=0)
    results = fix_results(results, thermal_model_file)

    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    for variable in results.columns:
        if variable != "Maximum CPU Temperature [C]":
            plot_results(results, variable, output_directory)




if __name__ == "__main__":
    
    process = subprocess.Popen(["helics", "run", "--path=runner.json"], 
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    for line in iter(process.stdout.readline, ''):
        print(line, end='')

    process.wait()
    print(f"Co-simulation finished with exit code {process.returncode}")

    create_plots("Output/eplusout.csv",
         "Output/time_series_data.csv",
         "Plots")