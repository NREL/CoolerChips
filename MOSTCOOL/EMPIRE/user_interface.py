import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import json
import shutil
import os
from PIL import Image, ImageTk
from tsrm_api import TSRMApi
from src.utils.simData_util import SimData
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        # Add error handling
        if user_file_path:
            return self.api.gen_and_run_sim(user_file_path)
        else:
            return self.api.gen_and_run_sim(None, *params)
        
    def stop_simulation(self):
        """
        Calls the TSRM API function to quit the matlab engine and stop the simulation
        """ 
        self.api.stop_simulation()

class UserInterface:
    def __init__(self):
        api = TSRMApi()
        self.wrapper = TSRMApiWrapper(api)
        self.simdata = SimData()
        self.state = AppState.set_values_from_api(self.simdata, self.wrapper)

    def handle_simulation_completion(self, simulation_output_path):
        """
        Updates the UI upon simulation completion. It configures buttons to save,
        view, and open the result, and updates the status label. 

        Args:
            simulation_output_path (string): Path of the simulation output
        """    
        if simulation_output_path:
            label_selected_output.config(text=f"Input File Selected: {self.state.selected_input_path}")
            button_save_result.config(state=tk.NORMAL, command=lambda: self.save_result_file(simulation_output_path))
            button_view_result.config(state=tk.NORMAL, command=lambda: self.show_result_location(simulation_output_path))
            button_open_result.config(state=tk.NORMAL, command=lambda: self.open_result_file(simulation_output_path))
            status_label.config(text="Simulation completed!")
        else:
            status_label.config(text="Simulation failed. Check the log for errors.")
        stop_simulation_button.config(state=tk.DISABLED)

    def select_input_file(self):
        """
        Opens a file dialog to select an input JSON file and updates
        the state and UI accordingly.
        """
        self.state.selected_input_path = filedialog.askopenfilename(title="Select input JSON file", filetypes=[("JSON files", "*.json")])
        if self.state.selected_input_path:
            label_selected_output.config(text=f"Input File Selected: {self.state.selected_input_path}")
            run_simulation_button.config(state=tk.NORMAL)

    def run_simulation(self, input_option):
        """
        Sets up the UI and starts the simulation in a new thread. Initializes 
        progress bar and status label, and starts the simulation thread.

        Args:
            input_option (IntVar): User's input method choice
        """
        status_label.grid(row=2, column=0, columnspan=2, pady=10)
        progress_bar.grid(row=1, column=0, pady=10)
        status_label.config(text="Simulation in progress...")
        stop_simulation_button.config(state=tk.NORMAL)
        progress_bar.start(10)

        threading.Thread(target=self.run_simulation_thread, args=(input_option,)).start()

    def run_simulation_thread(self, input_option):
        """
        Calls the API wrapper to run the simulation based on user input, either 
        from a JSON file or manual input, and updates the UI upon completion

        Args:
            input_option (IntVar): User's input method choice
        """
        simulation_output_path = None
        if input_option.get() == 1 and self.state.selected_input_path: # User-provided JSON file
            simulation_output_path = self.wrapper.run_simulation(user_file_path=self.state.selected_input_path)
        else: # Manual inputs
            try:
                simulation_output_path = self.wrapper.run_simulation(
                    None,
                    method_variable.get(),
                    component_variable.get(),
                    int(heat_transfer_variable.get()),
                    int(ambient_temp_variable.get()),
                    int(processor_temp_variable.get()),
                    int(initial_temp_variable.get()),
                )
            except KeyError as e:
                messagebox.showerror("Error", f"Simulation failed due to missing key: {e}")
                logging.error(f"Simulation failed due to missing key: {e}")
        progress_bar.stop()
        progress_bar.grid_forget()
        status_label.after(0, self.handle_simulation_completion, simulation_output_path)

    def stop_simulation(self):
        """
        Updates the user interface and status label while calling the api wrapper function
        to stop the matlab engine
        """
        self.wrapper.stop_simulation()
        progress_bar.stop()
        progress_bar.grid_forget()
        status_label.config(text="Simulation stopped before completion")

    def save_result_file(self, result_output_path):
        """
        Saves the simulation result to a user-specified location. Opens a save
        dialog and copies the result file to the chosen path

        Args:
            result_output_path (string): Path of the simulation results
        """    
        file_path = filedialog.asksaveasfilename(title="Save Output File As", defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            shutil.copy(result_output_path, file_path)
            label_selected_output.config(text=f"Output file saved as: {file_path}")

    def show_result_location(self, result_file_path):
        """
        Displays the result file location in a message box.

        Args:
            result_file_path (string): Path of the simulation results
        """
        messagebox.showinfo("File Location", f"Results are at: {result_file_path}")

    def open_result_file(self, result_file_path):
        """
        Opens and displays the content of the result file in a new window.

        Args:
            result_file_path (string): Path of the simulation results.
        """
        try:
            with open(result_file_path, 'r') as result_file:
                result_data = json.load(result_file)
                result_window = tk.Toplevel(root)
                result_window.title("Simulation Results")
                tk.Label(result_window, text=json.dumps(result_data, indent=4), justify="left").pack(padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read the results file: {e}")
            logging.error(f"Failed to read the results file: {e}")

    def handle_input_selection(self, input_option):
        """
        Handles the user's choice between file input and manual input,
        adjusting the UI accordingly.

        Args:
            input_option (IntVar): User's input method choice
        """
        if input_option.get() == 1: # Input file
            button_select_file.grid()
            label_selected_output.grid()
            input_frame.grid_forget()
            if not self.state.selected_input_path:
                run_simulation_button.config(state=tk.DISABLED)
        else: # Manual Entry
            button_select_file.grid_remove()
            label_selected_output.grid_remove()
            input_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
            run_simulation_button.config(state=tk.NORMAL)


        root.update_idletasks()
        root.geometry("")  # Adjust window size dynamically


ui = UserInterface()

# GUI setup
root = tk.Tk()
root.title("Simulation Interface")
root.geometry("800x800")
root.columnconfigure([0, 1, 2], weight=1)

# Create a canvas and scrollbar
canvas = tk.Canvas(root, width=800, height=600)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=scrollbar.set)
frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor="nw")

# Update the canvas scroll region whenever the frame size changes
frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Add mouse wheel support
def on_mouse_wheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
canvas.bind_all("<MouseWheel>", on_mouse_wheel)

# Load and display logo
image_path = os.path.join(ui.state.base_directory, "logo.png")
image = Image.open(image_path)
scaling_factor = min(780 / image.width, 200 / image.height)
image = image.resize((int(image.width * scaling_factor), int(image.height * scaling_factor)), Image.LANCZOS)
image_photo = ImageTk.PhotoImage(image)
tk.Label(frame, image=image_photo).grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='n')

# Input options
options_frame = ttk.LabelFrame(frame, text="Options to Provide Inputs")
options_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

# Input options frame
input_option = tk.IntVar(value=1)
ttk.Radiobutton(options_frame, text="Import JSON File", value=1, variable=input_option, command=lambda: ui.handle_input_selection(input_option)).grid(row=0, column=0, pady=5, padx=10, sticky='w')
button_select_file = tk.Button(options_frame, text="Choose Input File", command=lambda: ui.select_input_file())
button_select_file.grid(row=1, column=0, pady=5, padx=20, sticky='w')
label_selected_output = tk.Label(options_frame, text="No file selected yet.")
label_selected_output.grid(row=2, column=0, pady=5, padx=10, sticky='w')
ttk.Radiobutton(options_frame, text="Manually Input Values", value=2, variable=input_option, command=lambda: ui.handle_input_selection(input_option)).grid(row=3, column=0, pady=5, padx=10, sticky='w')

# Manual input frame
input_frame = ttk.LabelFrame(frame, text="Simulation Inputs")
cooling_frame = ttk.LabelFrame(input_frame, text="Cooling System Parameters (Environmental Conditions)")
cooling_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
tk.Label(cooling_frame, text="Cooling Method").grid(row=0, column=0, padx=5, pady=5, sticky='w')
method_variable = tk.StringVar(value=ui.state.cooling_types[0])
ttk.Combobox(cooling_frame, textvariable=method_variable, values=ui.state.cooling_types).grid(row=1, column=0, padx=5, pady=5, sticky='w')
tk.Label(cooling_frame, text="Heat Transfer Coefficient (W/m²·K)").grid(row=2, column=0, padx=5, pady=5, sticky='w')
heat_transfer_variable = tk.IntVar()
tk.Entry(cooling_frame, textvariable=heat_transfer_variable).grid(row=3, column=0, padx=5, pady=5, sticky='w')
tk.Label(cooling_frame, text="Ambient Temperature (°C)").grid(row=2, column=1, padx=5, pady=5, sticky='w')
ambient_temp_variable = tk.IntVar()
tk.Entry(cooling_frame, textvariable=ambient_temp_variable).grid(row=3, column=1, padx=5, pady=5, sticky='w')

# Processor frame
processor_frame = ttk.LabelFrame(input_frame, text="Processor Conditions")
processor_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
tk.Label(processor_frame, text="Processor Type").grid(row=0, column=0, padx=5, pady=5, sticky='w')
component_variable = tk.StringVar(value=ui.state.processor_types[0])
ttk.Combobox(processor_frame, textvariable=component_variable, values=ui.state.processor_types).grid(row=1, column=0, padx=5, pady=5, sticky='w')
tk.Label(processor_frame, text="Processing Temperature (°C)").grid(row=2, column=0, padx=5, pady=5, sticky='w')
processor_temp_variable = tk.IntVar()
tk.Entry(processor_frame, textvariable=processor_temp_variable).grid(row=3, column=0, padx=5, pady=5, sticky='w')
tk.Label(processor_frame, text="Initial Temperature (°C)").grid(row=2, column=1, padx=5, pady=5, sticky='w')
initial_temp_variable = tk.IntVar()
tk.Entry(processor_frame, textvariable=initial_temp_variable).grid(row=3, column=1, padx=5, pady=5, sticky='w')

# Run simulation frame
run_frame = ttk.LabelFrame(frame, text="Run Simulation")
run_frame.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
run_simulation_button = tk.Button(run_frame, text="Run Simulation", state=tk.DISABLED, command=lambda: ui.run_simulation(input_option))
run_simulation_button.grid(row=0, column=0, padx=10, pady=10)
stop_simulation_button = tk.Button(run_frame, text="Stop Simulation", state=tk.DISABLED,command=lambda: ui.stop_simulation())
stop_simulation_button.grid(row=0, column=1, padx=10, pady=10)
progress_bar = ttk.Progressbar(run_frame, length=200, mode='indeterminate')
status_label = tk.Label(run_frame, text="Ready to start simulation.")

# Results frame
results_frame = ttk.LabelFrame(frame, text="Results Handling")
results_frame.grid(row=7, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
button_save_result = tk.Button(results_frame, text="Save Output File", state=tk.DISABLED)
button_save_result.grid(row=0, column=0, padx=10, pady=10)
button_view_result = tk.Button(results_frame, text="View Result Location", state=tk.DISABLED)
button_view_result.grid(row=0, column=1, padx=10, pady=10)
button_open_result = tk.Button(results_frame, text="Open Result", state=tk.DISABLED)
button_open_result.grid(row=0, column=2, padx=10, pady=10)

root.update_idletasks()
root.geometry("")
root.mainloop()