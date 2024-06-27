"""
Module: user_interface.py
Authors:
- Najee Stubbs {nistubbs@uark.edu}, University of Arkansas, Mechanical Engineering Dept.
- Tyler Kuper {tdkuper@uark.edu}, University of Arkansas, Computer Science Dept. 
Date: June 20, 2024

Description:
user_interface.py initializes a graphical user interface (GUI) for interacting with the
TSRM_API and viewing, saving, and managing simulation data. This module contains three classes:
a class which keeps track of the state of the apps variables, a wrapper class that contains all
references to the TSRM_API, and a class that initializes and manages the GUI.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import json
import shutil
import os
from PIL import Image, ImageTk
from src.communication.tsrm_api import TSRMApi
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
            self.api.stop_simulation()
        except Exception as e:
            print(f"Error occurred in stop_simulation: {e}")

class UserInterface:
    def __init__(self, root):
        api = TSRMApi()
        self.wrapper = TSRMApiWrapper(api)
        self.simdata = SimData()
        self.state = AppState.set_values_from_api(self.simdata, self.wrapper)
        # GUI setup
        self.root = root
        self.root.title("Simulation Interface")
        self.root.geometry("800x800")
        self.root.columnconfigure([0, 1, 2], weight=1)
        self.__setup_ui()

    def __setup_ui(self):
        """
        Private function that calls all other setup functions for the user
        interface.
        """
        self.__setup_canvas()
        self.__setup_logo()
        self.__setup_options_frame()
        self.__setup_cooling_frame()
        self.__setup_processor_frame()
        self.__setup_run_simulation_frame()
        self.__setup_results_frame()
        logging.info("User interface successfully initialized")

    def __setup_canvas(self):
        """
        Private setup function for the canvas frame so the scrollbar can function.
        """
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self.root, width=800, height=600)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        # Update the canvas scroll region whenever the frame size changes
        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Add mouse wheel support
        def on_mouse_wheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    def __setup_logo(self):
        """
        Private setup function that loads and displays the logo image at the top of 
        the user interface
        """
        # Load and display logo
        try:
            self.image_path = os.path.join(self.state.base_directory, "logo.png")
            self.image = Image.open(self.image_path)
            scaling_factor = min(780 / self.image.width, 200 / self.image.height)
            self.image = self.image.resize((int(self.image.width * scaling_factor), int(self.image.height * scaling_factor)), Image.LANCZOS)
            self.image_photo = ImageTk.PhotoImage(self.image)
            self.logo = tk.Label(self.frame, image=self.image_photo)
            self.logo.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='n')
        except Exception as e:
            messagebox.showerror("Error", f"An error ocurred while loading the logo image: {e}")

    def __setup_options_frame(self):
        """
        Private setup function for the input option radio buttons and import file section
        """
        # Input options
        self.options_frame = ttk.LabelFrame(self.frame, text="Options to Provide Inputs")
        self.options_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Input options frame
        self.input_option = tk.IntVar(value=1)
        ttk.Radiobutton(self.options_frame, text="Import JSON File", value=1, variable=self.input_option, command=lambda: self.__handle_input_selection()).grid(row=0, column=0, pady=5, padx=10, sticky='w')
        self.button_select_file = tk.Button(self.options_frame, text="Choose Input File", command=lambda: self.select_input_file())
        self.button_select_file.grid(row=1, column=0, pady=5, padx=20, sticky='w')
        self.label_selected_output = tk.Label(self.options_frame, text="No file selected yet.")
        self.label_selected_output.grid(row=2, column=0, pady=5, padx=10, sticky='w')
        ttk.Radiobutton(self.options_frame, text="Manually Input Values", value=2, variable=self.input_option, command=lambda: self.__handle_input_selection()).grid(row=3, column=0, pady=5, padx=10, sticky='w')

    def __setup_cooling_frame(self):
        """
        Private setup function for the manual input frame
        """
        # Manual input frame
        self.input_frame = ttk.LabelFrame(self.frame, text="Simulation Inputs")
        self.cooling_frame = ttk.LabelFrame(self.input_frame, text="Cooling System Parameters (Environmental Conditions)")
        self.cooling_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        tk.Label(self.cooling_frame, text="Cooling Method").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.method_variable = tk.StringVar(value=self.state.cooling_types[0])
        ttk.Combobox(self.cooling_frame, textvariable=self.method_variable, values=self.state.cooling_types).grid(row=1, column=0, padx=5, pady=5, sticky='w')

        # Nested function to check if entry contains digits
        def callback(P):
            if str.isdigit(P) or P == "":
                return True
            else:
                return False
        vcmd = (self.cooling_frame.register(callback))

        # Heat Transfer Coefficient Entry
        tk.Label(self.cooling_frame, text="Heat Transfer Coefficient (W/m²·K)").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.heat_transfer_variable = tk.IntVar()
        heat_transfer_entry = tk.Entry(self.cooling_frame, textvariable=self.heat_transfer_variable, validate='all', validatecommand=(vcmd, '%P'))
        heat_transfer_entry.grid(row=3, column=0, padx=5, pady=5, sticky='w')

        # Ambient Temperature Entry
        tk.Label(self.cooling_frame, text="Ambient Temperature (°C)").grid(row=2, column=1, padx=5, pady=5, sticky='w')
        self.ambient_temp_variable = tk.IntVar()
        ambient_temp_entry = tk.Entry(self.cooling_frame, textvariable=self.ambient_temp_variable, validate='all', validatecommand=(vcmd, '%P'))
        ambient_temp_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')

    def __setup_processor_frame(self):
        """
        Private setup function for the processor conditions section
        """
        # Processor frame
        self.processor_frame = ttk.LabelFrame(self.input_frame, text="Processor Conditions")
        self.processor_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        tk.Label(self.processor_frame, text="Processor Type").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.component_variable = tk.StringVar(value=self.state.processor_types[0])
        ttk.Combobox(self.processor_frame, textvariable=self.component_variable, values=self.state.processor_types).grid(row=1, column=0, padx=5, pady=5, sticky='w')

        # Nested function to check if entry contains digits
        def callback(P):
            if str.isdigit(P) or P == "":
                return True
            else:
                return False
        vcmd = (self.cooling_frame.register(callback))

        # Processing Temperature Entry
        tk.Label(self.processor_frame, text="Processing Temperature (°C)").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.processor_temp_variable = tk.IntVar()
        processor_temp_entry = tk.Entry(self.processor_frame, textvariable=self.processor_temp_variable, validate='all', validatecommand=(vcmd, '%P'))
        processor_temp_entry.grid(row=3, column=0, padx=5, pady=5, sticky='w')

        # Initial Temperature Entry
        tk.Label(self.processor_frame, text="Initial Temperature (°C)").grid(row=2, column=1, padx=5, pady=5, sticky='w')
        self.initial_temp_variable = tk.IntVar()
        initial_temp_entry = tk.Entry(self.processor_frame, textvariable=self.initial_temp_variable, validate='all', validatecommand=(vcmd, '%P'))
        initial_temp_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')

    def __setup_run_simulation_frame(self):
        """
        Private setup function for the run simulation section
        """
        # Run simulation frame
        self.run_frame = ttk.LabelFrame(self.frame, text="Run Simulation")
        self.run_frame.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        self.run_simulation_button = tk.Button(self.run_frame, text="Run Simulation", state=tk.DISABLED, command=lambda: self.run_simulation())
        self.run_simulation_button.grid(row=0, column=0, padx=10, pady=10)
        self.stop_simulation_button = tk.Button(self.run_frame, text="Stop Simulation", state=tk.DISABLED,command=lambda: self.stop_simulation())
        self.stop_simulation_button.grid(row=0, column=1, padx=10, pady=10)
        self.progress_bar = ttk.Progressbar(self.run_frame, length=200, mode='indeterminate')
        self.status_label = tk.Label(self.run_frame, text="Ready to start simulation.") 

    def __setup_results_frame(self):
        """
        Private setup function for the results section
        """
        # Results frame
        self.results_frame = ttk.LabelFrame(self.frame, text="Results Handling")
        self.results_frame.grid(row=7, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        self.button_save_result = tk.Button(self.results_frame, text="Save Output File", state=tk.DISABLED)
        self.button_save_result.grid(row=0, column=0, padx=10, pady=10)
        self.button_view_result = tk.Button(self.results_frame, text="View Result Location", state=tk.DISABLED)
        self.button_view_result.grid(row=0, column=1, padx=10, pady=10)
        self.button_open_result = tk.Button(self.results_frame, text="Open Result", state=tk.DISABLED)
        self.button_open_result.grid(row=0, column=2, padx=10, pady=10)

    def __handle_input_selection(self):
        """
        Handles the user's choice between file input and manual input,
        adjusting the UI accordingly.

        Args:
            input_option (IntVar): User's input method choice
        """
        if self.input_option.get() == 1: # Input file
            self.button_select_file.grid()
            self.label_selected_output.grid()
            self.input_frame.grid_forget()
            if not self.state.selected_input_path:
                self.run_simulation_button.config(state=tk.DISABLED)
        else: # Manual Entry
            self.button_select_file.grid_remove()
            self.label_selected_output.grid_remove()
            self.input_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
            self.run_simulation_button.config(state=tk.NORMAL)

        self.root.update_idletasks()
        self.root.geometry("")  # Adjust window size dynamically

    def __handle_simulation_completion(self, simulation_output_path):
        """
        Updates the UI upon simulation completion. It enables the buttons to save,
        view, and open the result, and updates the status label. 

        Args:
            simulation_output_path (string): Path of the simulation output
        """    
        if simulation_output_path:
            self.label_selected_output.config(text=f"Input File Selected: {self.state.selected_input_path}")
            self.button_save_result.config(state=tk.NORMAL, command=lambda: self.save_result_file(simulation_output_path))
            self.button_view_result.config(state=tk.NORMAL, command=lambda: self.show_result_location(simulation_output_path))
            self.button_open_result.config(state=tk.NORMAL, command=lambda: self.open_result_file(simulation_output_path))
            self.status_label.config(text="Simulation completed!")
            logging.info("Simulation completed!")
        else:
            self.status_label.config(text="Simulation failed. Check the log for errors.")
            logging.info("Simulation failed.")
        self.stop_simulation_button.config(state=tk.DISABLED)

    def __run_simulation_thread(self):
        """
        Calls the API wrapper to run the simulation based on user input, either 
        from a JSON file or manual input, and updates the UI upon completion

        Args:
            input_option (IntVar): User's input method choice
        """
        simulation_output_path = None
        if self.input_option.get() == 1 and self.state.selected_input_path: # User-provided JSON file
            simulation_output_path = self.wrapper.run_simulation(user_file_path=self.state.selected_input_path)
        else: # Manual inputs
            try:
                simulation_output_path = self.wrapper.run_simulation(
                    None,
                    self.method_variable.get(),
                    self.component_variable.get(),
                    int(self.heat_transfer_variable.get()),
                    int(self.ambient_temp_variable.get()),
                    int(self.processor_temp_variable.get()),
                    int(self.initial_temp_variable.get()),
                )
            except KeyError as e:
                messagebox.showerror("Error", f"Simulation failed due to missing key: {e}")
                logging.error(f"Simulation failed due to missing key: {e}")
        self.progress_bar.stop()
        self.progress_bar.grid_forget()
        self.status_label.after(0, self.__handle_simulation_completion, simulation_output_path)

    def select_input_file(self):
        """
        Opens a file dialog to select an input JSON file and updates
        the state and UI accordingly.
        """
        self.state.selected_input_path = filedialog.askopenfilename(title="Select input JSON file", filetypes=[("JSON files", "*.json")])
        if self.state.selected_input_path:
            self.label_selected_output.config(text=f"Input File Selected: {self.state.selected_input_path}")
            self.run_simulation_button.config(state=tk.NORMAL)

    def run_simulation(self):
        """
        Sets up the UI and starts the simulation in a new thread. Initializes 
        progress bar and status label, and starts the simulation thread.

        Args:
            input_option (IntVar): User's input method choice
        """
        self.status_label.grid(row=2, column=0, columnspan=2, pady=10)
        self.progress_bar.grid(row=1, column=0, pady=10)
        self.status_label.config(text="Simulation in progress...")
        self.stop_simulation_button.config(state=tk.NORMAL)
        self.progress_bar.start(10)

        logging.info("Starting simulation thread...")
        threading.Thread(target=self.__run_simulation_thread).start()

    def stop_simulation(self):
        """
        Updates the user interface and status label while calling the api wrapper function
        to stop the matlab engine
        """
        self.wrapper.stop_simulation()
        self.progress_bar.stop()
        self.progress_bar.grid_forget()
        self.status_label.config(text="Simulation stopped before completion")

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
            self.label_selected_output.config(text=f"Output file saved as: {file_path}")
            logging.info("File successfully saved!")

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
                self.result_window = tk.Toplevel(self.root)
                self.result_window.title("Simulation Results")
                tk.Label(self.result_window, text=json.dumps(result_data, indent=4), justify="left").pack(padx=10, pady=10)
                logging.info("Successfully opened output data.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read the results file: {e}")
            logging.error(f"Failed to read the results file: {e}")


def main():
    root = tk.Tk()
    ui = UserInterface(root)
    root.update_idletasks()
    root.geometry("")
    root.mainloop()

if __name__ == "__main__":
    main()
