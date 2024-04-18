"""GUI Code"""


from json import dumps
import os
from pathlib import Path
from platform import system
from subprocess import Popen
import sys
from threading import Thread
from time import sleep
from tkinter import BOTH, HORIZONTAL, LEFT, TOP, VERTICAL, W, X, Button, Canvas, Frame, Label, LabelFrame, Menu, OptionMenu, PhotoImage, Scrollbar, StringVar, Tk, filedialog, messagebox, ttk, font
import webbrowser
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import pandas as pd
from plan_tools.runtime import fixup_taskbar_icon_on_windows
from pubsub import pub
from typing import Union
import definitions
import simulator
import paraview
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import ImageTk, Image

plt.rcParams.update({'font.size': 16})  # Adjust font size as needed



class PubSubMessageTypes:
    PRINT = '10'
    STARTING = '20'
    CASE_COMPLETE = '30'
    SIMULATIONS_DONE = '40'
    DIFF_COMPLETE = '50'
    ALL_DONE = '60'
    CANCELLED = '70'
    
class ImageViewer:
    def __init__(self, main, image_folder):
        self.main = main
        self.image_folder = image_folder
        self.image_files = sorted(
            (os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith('jpg')),
            key=lambda x: os.path.basename(x)
        )
        self.current_image = 0

        self.canvas = Canvas(main, bg='white')
        self.canvas.grid(row=0, column=0, sticky='nsew')

        self.vbar = Scrollbar(main, orient=VERTICAL, command=self.canvas.yview)
        self.vbar.grid(row=0, column=1, sticky='ns')
        self.canvas.config(yscrollcommand=self.vbar.set)

        # Configure row and column weights (make the canvas expandable)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # Button frame for navigation buttons
        self.button_frame = Frame(main)
        self.button_frame.grid(row=1, column=0, columnspan=2, sticky='ew')
        main.grid_rowconfigure(1, weight=0)

        self.prev_button = Button(self.button_frame, text='Previous', command=self.show_prev_image)
        self.prev_button.grid(row=0, column=0, sticky='ew')

        self.next_button = Button(self.button_frame, text='Next', command=self.show_next_image)
        self.next_button.grid(row=0, column=1, sticky='ew')
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        # Frame for the horizontal scrollbar
        self.scrollbar_frame = Frame(main)
        self.scrollbar_frame.grid(row=2, column=0, columnspan=2, sticky='ew')
        main.grid_rowconfigure(2, weight=0)

        self.hbar = Scrollbar(self.scrollbar_frame, orient=HORIZONTAL, command=self.canvas.xview)
        self.hbar.pack(fill=X)
        self.canvas.config(xscrollcommand=self.hbar.set)

        self.load_image()

    def load_image(self):
        if self.image_files:
            image_path = self.image_files[self.current_image]
            image = Image.open(image_path)
            self.photo = ImageTk.PhotoImage(image)

            self.canvas.delete('all')

            # Calculate coordinates to center the image
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            x = (canvas_width - self.photo.width()) // 2
            y = (canvas_height - self.photo.height()) // 2
            x = max(x, 0)  # Ensure x is not negative
            y = max(y, 0)  # Ensure y is not negative

            self.canvas.create_image(x, y, image=self.photo, anchor='nw')
            self.canvas.config(scrollregion=self.canvas.bbox('all'))

    def show_next_image(self):
        if self.current_image < len(self.image_files) - 1:
            self.current_image += 1
            self.load_image()

    def show_prev_image(self):
        if self.current_image > 0:
            self.current_image -= 1
            self.load_image()
    

class MyApp(Frame):

    def __init__(self):
        self.root = Tk(className='mostcool')
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=14)
        Frame.__init__(self, self.root)

        # add the taskbar icon, but its having issues reading the png on Mac, not sure.
        if system() == 'Darwin':
            self.icon_path = Path(__file__).resolve().parent / 'icons' / 'icon.icns'
            if self.icon_path.exists():
                self.root.iconbitmap(str(self.icon_path))
            else:
                print(f"Could not set icon for Mac, expecting to find it at {self.icon_path}")
        elif system() == 'Windows':
            self.icon_path = Path(__file__).resolve().parent / 'icons' / 'icon.png'
            img = PhotoImage(file=str(self.icon_path))
            if self.icon_path.exists():
                self.root.iconphoto(False, img)
            else:
                print(f"Could not set icon for Windows, expecting to find it at {self.icon_path}")
        else:  # Linux
            self.icon_path = Path(__file__).resolve().parent / 'icons' / 'icon.png'
            img = PhotoImage(file=str(self.icon_path))
            if self.icon_path.exists():
                self.root.iconphoto(False, img)
            else:
                print(f"Could not set icon for Windows, expecting to find it at {self.icon_path}")
        # fixup_taskbar_icon_on_windows(mostcool.NAME)

        # high level GUI configuration
        self.root.geometry('1300x1000')
        self.root.resizable(width=True, height=True)
        self.root.option_add('*tearOff', False)  # keeps file menus from looking weird

        # members related to the background thread and operator instance
        self.long_thread = None
        self.background_operator: Union[None, simulator.Simulator] = None

        # tk variables we can access later
        self.idf_path = StringVar()
        self.epw_path = StringVar()
        self.server_model_path = StringVar()
        self.floor_area = StringVar()
        self.paraview_velocity = StringVar()
        self.paraview_server_temp_in = StringVar()
        self.paraview_CPU_load_fraction = StringVar()
        self.control_option = StringVar()
        self.datacenter_location = StringVar()
        self.label_status = StringVar()
        
        

        # widgets that we might want to access later
        self.run_button = None
        self.progress = None
        self.progress_update_id = 0
        self.time_step_spinner = None
        self.wpzfa_option_menu = None
        self.results=None
        self.results_previous = None

        # some data holders
        self.auto_saving = False
        self.manually_saving = False
        self.save_interval = 10000  # ms, so 10 seconds

        # initialize the GUI
        self.main_notebook = None
        self.init_window()

        # try to autoload the last settings, and kick off the auto-save feature
        # self.client_open(auto_open=True)
        self.root.after(self.save_interval, self.auto_save)

        # wire up the background thread
        pub.subscribe(self.print_handler, PubSubMessageTypes.PRINT)
        pub.subscribe(self.starting_handler, PubSubMessageTypes.STARTING)
        pub.subscribe(self.increment_handler, PubSubMessageTypes.CASE_COMPLETE)
        pub.subscribe(self.done_handler, PubSubMessageTypes.ALL_DONE)
        pub.subscribe(self.cancelled_handler, PubSubMessageTypes.CANCELLED)

        # on Linux, initialize the notification class instance
        self.notification = None
        if system() == 'Linux':
            self.notification_icon = Path(self.icon_path)
            # self.notification = Notification('energyplus_regression_runner')



    def init_window(self):
        # changing the title of our main widget
        self.root.title("MOSTCOOL")
        self.root.protocol("WM_DELETE_WINDOW", self.client_exit)
        self.root.pack_propagate(False)

        # create the menu
        menu = Menu(self.root)
        self.root.config(menu=menu)
        file_menu = Menu(menu)
        file_menu.add_command(label="Exit", command=self.client_exit)
        menu.add_cascade(label="File", menu=file_menu)
        help_menu = Menu(menu)
        help_menu.add_command(label="About...", command=self.about_dialog)
        menu.add_cascade(label="Help", menu=help_menu)

        # main notebook holding everything
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(fill='both', expand=True)  # Ensure notebook fills root


        style = ttk.Style()
        style.map("C.TButton",
                  foreground=[('pressed', 'red'), ('active', 'blue')],
                  background=[('pressed', '!disabled', 'black'),
                              ('active', 'white')]
                  )
        spinbox_width = 4
        
        # Intro Pane
        pane_intro = Frame(self.main_notebook)
        pane_intro.pack(fill='both', expand=True)  # Ensure pane_intro fills notebook
        self.main_notebook.add(pane_intro, text='Introduction')
        
        app = ImageViewer(pane_intro, '/app/v1_slide_images/')  # Update this path

        
        # run configuration
        pane_run = Frame(self.main_notebook)
        pane_run.pack(fill='both', expand=True)  # Ensure pane_run fills notebook


        # Map Image
        map_image_frame = LabelFrame(pane_run)  # Adjust text as needed with text="Map Image"
        map_image_frame.pack(fill='x', padx=5, pady=5)
        img = Image.open("/app/Resources/map.png")
        self.img = ImageTk.PhotoImage(img)
        panel = Label(map_image_frame, image=self.img)
        panel.pack(side="top", fill="both", expand="yes")

        # File Selection Menu
        group_run_options = LabelFrame(pane_run)  # Adjust text as needed with text="File Selection"
        group_run_options.pack(fill=X, padx=5)

        
        Label(group_run_options, text="Select datacenter location: ").grid(row=1, column=1, sticky=W)
        self.datacenter_location.set(list(definitions.LOCATION_MAP.keys())[0])
        self.datacenter_location_menu = OptionMenu(group_run_options, self.datacenter_location,
                                                *list(definitions.LOCATION_MAP.keys()))
        self.datacenter_location_menu.grid(row=1, column=2, sticky=W)
        
        
        # Label(group_run_options, text="[Placeholder] Datacenter floor area [m2]: ").grid(row=2, column=1, sticky=W)
        # self.floor_area.set('250')
        # self.fa_option_menu = OptionMenu(group_run_options, self.floor_area,
        #                                         *['250', '500', '750'])
        # self.fa_option_menu.grid(row=2, column=2, sticky=W)
        
        # Label(group_run_options, text="[Placeholder] Watts per zone floor area [W]: ").grid(row=3, column=1, sticky=E)
        # self.wpzfa.set('100')
        # self.wpzfa_option_menu = OptionMenu(group_run_options, self.wpzfa,
        #                                         *['100', '200', '400'])
        # self.wpzfa_option_menu.grid(row=3, column=2, sticky=W)

        self.main_notebook.add(pane_run, text='Run Configuration')
        
        
        # set up a tree-view for the results
        pane_results = ttk.Notebook(self.main_notebook)
        self.main_notebook.add(pane_results, text="Results (initialized)")
        
        self.main_notebook.tab(pane_results, state='disabled')
        plots = Frame(pane_results)
        pane_results.add(plots, text="Plots")
        # Create a frame to hold the label and dropdown menu
        row_frame = Frame(plots)
        row_frame.pack(side='top', fill='x')
        Label(row_frame, text="Building energy output to display: ").pack(side='left')
        # Dropdown menu for selecting the y-axis variable
        self.y_axis_variable = StringVar()
        self.y_axis_variable.set("Select variable")  # default value
        self.y_axis_variable.trace_add("write", lambda name, index, mode: self.update_plot())
        self.y_axis_drop_down_menu = OptionMenu(row_frame, self.y_axis_variable, "Select variable") #, command=self.update_plot)
        self.y_axis_drop_down_menu.pack()
        
        # Placeholder for the Matplotlib figure
        self.fig_ep_plot = Figure(figsize=(5, 4), dpi=100)
        self.plot= self.fig_ep_plot.add_subplot(1, 1, 1)
        self.plot_canvas = FigureCanvasTkAgg(self.fig_ep_plot, plots)  # A tk.DrawingArea.
        self.plot_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        
        # Create the second inner frame within pane_results for thermal model results
        thermal_results = Frame(pane_results)
        pane_results.add(thermal_results, text="External Application Results")
        
        Label(thermal_results, text="Choose variables to view results in Paraview:").grid(row=1, column=1, sticky=W, padx=5, pady=5)
        
        Label(thermal_results, text="Velocity: [m/s]").grid(row=2, column=1, sticky=W, padx=5, pady=5)
        self.paraview_velocity.set(paraview.upper_vel_limit)
        # self.paraview_velocity_option_menu = OptionMenu(thermal_results, self.paraview_velocity,
        #                                         *[str(number) for number in range(paraview.lower_vel_limit, paraview.upper_vel_limit + 1)])
        self.paraview_velocity_spinbox = ttk.Spinbox(thermal_results, from_=paraview.lower_vel_limit, to=paraview.upper_vel_limit, textvariable=self.paraview_velocity)
        self.paraview_velocity_spinbox.grid(row=2, column=2, sticky=W, padx=5, pady=5)
        self.paraview_velocity_spinbox.config(width=spinbox_width)
        
        Label(thermal_results, text="Server Inlet Temperature: [C]").grid(row=3, column=1, sticky=W, padx=5, pady=5)
        self.paraview_server_temp_in.set(30)
        # self.paraview_server_temp_in_option_menu = OptionMenu(thermal_results, self.paraview_server_temp_in,
        #                                         *[str(number) for number in range(10, 50)])
        self.paraview_server_temp_in_spinbox = ttk.Spinbox(thermal_results, from_=0, to=100, textvariable=self.paraview_server_temp_in) 
        self.paraview_server_temp_in_spinbox.grid(row=3, column=2, sticky=W, padx=5, pady=5)
        self.paraview_server_temp_in_spinbox.config(width=spinbox_width)
        
        Label(thermal_results, text="CPU Load Fraction: [-]").grid(row=4, column=1, sticky=W, padx=5, pady=5)
        self.paraview_CPU_load_fraction.set(0.73)
        # self.paraview_CPU_load_fraction_option_menu = OptionMenu(thermal_results, self.paraview_CPU_load_fraction,
        #                                         *[str(number) for number in range(50, 101)])
        self.paraview_CPU_load_fraction_spinbox = ttk.Spinbox(thermal_results, from_=0.5, to=1, increment=0.01, textvariable=self.paraview_CPU_load_fraction)
        self.paraview_CPU_load_fraction_spinbox.grid(row=4, column=2, sticky=W, padx=5, pady=5)
        self.paraview_CPU_load_fraction_spinbox.config(width=spinbox_width)
        
        
        self.open_paraview_button = ttk.Button(thermal_results, text="Open Paraview", command=self.open_paraview,
                                          style="C.TButton")
        self.open_paraview_button.grid(row=5, column=1, sticky=W, padx=5, pady=5)
        
        
        # inner_frame3 = Frame(pane_results)
        # pane_results.add(inner_frame3, text="Cost Model")
                
        # pack the main notebook on the window
        self.main_notebook.pack(fill=BOTH, expand=1)

        # status bar at the bottom
        frame_status = Frame(self.root)
        self.run_button = ttk.Button(frame_status, text="Run", command=self.client_run, style="C.TButton")
        self.run_button.pack(side=LEFT, expand=0, padx=5)
        self.progress = ttk.Progressbar(frame_status, length=250)
        self.progress.pack(side=LEFT, expand=0, padx=5)
        label = Label(frame_status, textvariable=self.label_status)
        self.label_status.set("Initialized")
        label.pack(side=LEFT, anchor=W, padx=5)
        frame_status.pack(fill=X)

    def run(self):
        self.root.mainloop()

    def auto_save(self):
        if self.manually_saving or self.auto_saving:
            return  # just try again later
        self.client_save(auto_save=True)
        self.root.after(self.save_interval, self.auto_save)

    def client_save(self, auto_save=False):
        # we shouldn't come into this function from the auto_save if any other saving is going on already
        if self.auto_saving:
            # if we get in here from the save menu, and we are already trying to auto-save, give it a sec and retry
            sleep(0.5)
            if self.auto_saving:
                # if we are still auto-saving, then just go ahead and warn
                messagebox.showwarning("Auto-saving was already in process, try again.")
                return
        # TODO: Build a JSON structure of things you want saved here
        json_object = {}
        if auto_save:
            self.auto_saving = True
            save_file = os.path.join(os.path.expanduser("~"), ".auto-save.ept")  # TODO: New save file name
            open_save_file = open(save_file, 'w')
        else:
            self.manually_saving = True
            open_save_file = filedialog.asksaveasfile(defaultextension='.ept')
        if not open_save_file:
            return
        open_save_file.write(dumps(json_object, indent=2))
        open_save_file.close()
        if auto_save:
            self.auto_saving = False
        else:
            self.manually_saving = False

    @staticmethod
    def open_file_browser_to_directory(dir_to_open):
        this_platform = system()
        p = None
        if this_platform == 'Linux':
            try:
                p = Popen(['xdg-open', dir_to_open])
            except Exception as this_exception:  # pragma: no cover - not covering bad directories
                print("Could not open file:")
                print(this_exception)
        elif this_platform == 'Windows':  # pragma: no cover - only testing on Linux
            try:
                p = Popen(['start', dir_to_open], shell=True)
            except Exception as this_exception:
                print("Could not open file:")
                print(this_exception)
        elif this_platform == 'Darwin':  # pragma: no cover - only testing on Linux
            try:
                p = Popen(['open', dir_to_open])
            except Exception as this_exception:
                print("Could not open file:")
                print(this_exception)
        return p

    @staticmethod
    def open_documentation():
        url = ''  # TODO: Change URL
        # noinspection PyBroadException
        try:
            webbrowser.open_new_tab(url)
        except Exception:
            # error message
            messagebox.showerror("Docs problem", "Could not open documentation in browser")

    @staticmethod
    def about_dialog():
        # messagebox.showinfo("About", f"MOST COOL\nVersion: {mostcool.VERSION}")
        messagebox.showinfo("About", f"MOST COOL\nVersion: 0.1.0")
        

    def add_to_log(self, message):
        pass  # TODO: Could grab HELICS logs and E+ messages into here...
        # if self.log_message_listbox:
        #     self.log_message_listbox.insert(END, f"[{datetime.now().str f time('%Y-%m-%d %H:%M:%S')}]: {message}")
        #     self.log_message_listbox.yview(END)
        # if self.label_string:
        #     self.label_string.set(message)

    def clear_log(self):
        pass
        # self.log_message_listbox.delete(0, END)

    def copy_log(self):
        pass
        # messages = self.log_message_listbox.get(0, END)
        # message_string = '\n'.join(messages)
        # self.root.clipboard_clear()
        # self.root.clipboard_append(message_string)
        
    def update_option_menu(self, menu, new_options, set_default):
        menu['menu'].delete(0, 'end')
        for option in new_options:
            menu['menu'].add_command(label=option, command=lambda value=option: self.y_axis_variable.set(value))
        self.y_axis_variable.set(new_options[0])

    def update_plot(self):
        """Update the plot with the selected y-axis variable."""
        y_data = self.results[self.y_axis_variable.get()]
        self.plot.clear()
        self.plot.plot(self.results.index, y_data, color='blueviolet', alpha=0.8, label=self.y_axis_variable.get())
        # Plot the previous run if it exists
        # if self.results_previous is not None:
        #     self.plot.plot(self.results_previous.index, self.results_previous[self.y_axis_variable.get()])
        #     self.plot.legend(['Current Run', 'Previous Run'])
            
        # Create a secondary y-axis
        ax2 = self.plot.twinx()
        ax2.clear()
        ax2.yaxis.set_label_position("right")
        ax2.yaxis.tick_right()
        ax2.plot(self.results.index, self.results["Maximum CPU Temperature [C]"], label="Maximum CPU Temperature [C]",
                color='coral', alpha=0.8, linestyle='--')
        ax2.set_ylabel("Temperature [C]")
        ax2.tick_params(axis='y')    
        
        # Set the labels
        self.plot.set_ylabel(self.y_axis_variable.get())
        # Customize the datetime format on the x-axis, and rotate the labels
        self.plot.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        self.fig_ep_plot.autofmt_xdate()
        self.plot.set_xlabel("Date/Time")
        
        # Adjust subplot parameters to make space for the legend at the bottom
        self.fig_ep_plot.subplots_adjust(bottom=0.2)  # Increase bottom margin

        # Set legend for both axes in the lower right corner inside the plot area
        lines, labels = self.plot.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        self.plot.legend(lines + lines2, labels + labels2, loc='lower right')

        self.plot_canvas.draw()


    def set_gui_status_for_run(self, is_running: bool):
        if is_running:
            run_button_state = 'disabled'
            # stop_button_state = 'normal'
            results_tab_title = 'Results (Waiting on current run)'
        else:
            run_button_state = 'normal'
            # stop_button_state = 'disabled'
            # self.update_option_menu()
            results_tab_title = 'Results (Up to date)'
        self.run_button.configure(state=run_button_state)
        self.main_notebook.tab(2, text=results_tab_title)

    def open_paraview(self):
        try:
            paraview.predict_temperature(velocity= int(self.paraview_velocity.get()),
                                        CPU_load_fraction= float(self.paraview_CPU_load_fraction.get()),
                                        inlet_server_temperature= int(self.paraview_server_temp_in.get()))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        
    
    def select_idf(self):
        selected_path = filedialog.askopenfilename()
        if not selected_path:
            return
        self.idf_path.set(selected_path)

    def select_epw(self):
        selected_path = filedialog.askopenfilename()
        if not selected_path:
            return
        self.epw_path.set(selected_path)
        
    def select_server_model(self):
        selected_path = filedialog.askopenfilename()
        if not selected_path:
            return
        self.server_model_path.set(selected_path)        

    def client_run(self):
        if self.long_thread:
            messagebox.showerror("Cannot run another thread, wait for the current to finish -- how'd you get here?!?")
            return
        # TODO: Gather data in preparation to start main run
        self.background_operator = simulator.Simulator(idf_path=self.idf_path.get(), epw_path=self.epw_path.get(), control_option=self.control_option.get(),
                                             datacenter_location=self.datacenter_location.get())
        self.background_operator.add_callbacks(print_callback=MyApp.print_listener,
                                               sim_starting_callback=MyApp.starting_listener,
                                               increment_callback=MyApp.increment_listener,
                                               all_done_callback=MyApp.done_listener,
                                               cancel_callback=MyApp.cancelled_listener)
        # self.background_operator_plotter = plotter.Plotter(y_axis_variable=self.y_axis_variable.get())
        # self.background_operator_plotter.add_callbacks(all_done_callback=MyApp.done_listener)
        self.set_gui_status_for_run(True)
        self.long_thread = Thread(target=self.background_operator.run)
        self.long_thread.daemon = True
        self.add_to_log("Starting a run")
        self.long_thread.start()

    @staticmethod
    def print_listener(msg):
        pub.sendMessage(PubSubMessageTypes.PRINT, msg=msg)

    def print_handler(self, msg):
        self.add_to_log(msg)

    @staticmethod
    def starting_listener(num_progress_steps):
        pub.sendMessage(
            PubSubMessageTypes.STARTING,
            num_progress_steps=num_progress_steps
        )

    def starting_handler(self, num_progress_steps):
        self.label_status.set("Running")
        num_progress_steps = 10
        self.progress['maximum'] = num_progress_steps
        self.progress['value'] = 0

        def update_progress(value):
            """Increment progress bar value and schedule next increment or reset."""
            progress_bar_steps = 10  # Setting the number of steps directly in the handler
            if value < progress_bar_steps:
                self.progress['value'] = value + 1
                self.progress_update_id = self.root.after(1000, update_progress, value + 1)  # Schedule next increment
            else:
                self.progress['value'] = 0  # Reset the progress bar
                self.progress_update_id = self.root.after(1000, update_progress, 0)  # Restart the progress update

        update_progress(0)  # Start the progress update

    @staticmethod
    def increment_listener(some_string):
        pub.sendMessage(PubSubMessageTypes.CASE_COMPLETE, some_string=some_string)

    def increment_handler(self, some_string):
        self.progress['value'] += 1
        self.add_to_log(some_string)

    @staticmethod
    def done_listener(results):
        pub.sendMessage(PubSubMessageTypes.ALL_DONE, results=results)

    def done_handler(self, results=None):
        if results is None:
            # Cancel the scheduled progress bar update
            if hasattr(self, 'progress_update_id'):
                self.root.after_cancel(self.progress_update_id)
                self.progress['value'] = 0  # Reset the progress bar
            pass
        self.add_to_log("All done, finished")
        self.label_status.set("Hey, all done!")
        self.main_notebook.tab(2, state="normal") # TODO: 1 corresponds to the index of the thermal model results tab, change if needed
        if self.results is not None:
            self.results_previous = self.results
        self.results = results
        self.update_option_menu(self.y_axis_drop_down_menu, results.columns[1:], results.columns[1])
        # Cancel the scheduled progress bar update
        if hasattr(self, 'progress_update_id'):
            self.root.after_cancel(self.progress_update_id)
            self.progress['value'] = 10  
        self.client_done()

    @staticmethod
    def cancelled_listener():
        pub.sendMessage(PubSubMessageTypes.CANCELLED)

    def cancelled_handler(self):
        self.add_to_log("Cancelled!")
        self.label_status.set("Properly cancelled!")
        self.client_done()

    def client_stop(self):
        self.add_to_log("Attempting to cancel")
        self.label_status.set("Attempting to cancel...")
        # TODO: Implement cancelling self.background_operator.interrupt_please()

    def client_exit(self):
        if self.long_thread:
            messagebox.showerror("Uh oh!", "Cannot exit program while operations are running; abort them then exit")
            return
        sys.exit()

    def client_done(self):
        self.set_gui_status_for_run(False)
        self.long_thread = None
