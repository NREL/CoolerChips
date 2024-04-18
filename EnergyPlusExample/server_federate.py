"""Datacenter Thermal Model Federate"""

import pandas as pd
import federate
import numpy as np
from scipy.interpolate import Rbf
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import definitions
import logging


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


PUBS = [
    {
        "Name": f'{actuator["component_type"]}/{actuator["control_type"]}/{actuator["actuator_key"]}',
        "Type": "double",
        "Units": actuator["actuator_unit"],
        "Global": True,
    }
    for actuator in definitions.ACTUATORS
][1:3] # only the second and third actuator is used - supply delta T and return delta T

SUBS = [
    {
        "Name": sensor["variable_key"] + "/" + sensor["variable_name"],
        "Type": "double",
        "Units": sensor["variable_unit"],
        "Global": True,
    }
    for sensor in definitions.SENSORS
]

num_servers= 84
server_inlet_velocity=5#in m/s


class Server_thermal_federate:
    def __init__(self) -> None:
        self.total_time = definitions.TOTAL_SECONDS  # get this from IDF
        self.modes = np.loadtxt('ThermalModel_datacenter/modes.csv', delimiter=',')
        self.coefficients = np.loadtxt('ThermalModel_datacenter/coeff.csv', delimiter=',')
        self.parameter_array=np.loadtxt('ThermalModel_datacenter/parameter_array.csv', delimiter=',')
        
        self.rbf_models, self.param_scaler, self.coeff_scaler = self.build_and_scale_rbf_models(self.parameter_array, self.coefficients, kernel_function='multiquadric')
        
        self.subs = [federate.Sub(name=f'{sensor["variable_key"]}/{sensor["variable_name"]}', unit=sensor["variable_unit"]) for sensor in definitions.SENSORS]
        self.pubs = [federate.Pub(name=f'{pub["Name"]}', unit=pub["Units"]) for pub in PUBS]
        self.server_federate = federate.mostcool_federate(federate_name="Server_1", subscriptions=self.subs, publications=self.pubs)
        self.server_federate.time_interval_seconds = definitions.TIMESTEP_PERIOD_SECONDS
    
    # This fucntion "build_and_scale_rbf_models" has to be run once to run the online_prediction function multiple time inside Helics
    def build_and_scale_rbf_models(self, 
                                   training_parameters, 
                                   training_coefficients, 
                                   kernel_function='multiquadric'):
        """
        Build RBF models for each coefficient dimension with parameter and coefficient scaling.

        Parameters:
        - training_parameters: 2D array of parameters used for training.
        - training_coefficients: 2D array of coefficients corresponding to the training parameters.
        - kernel_function: String specifying the kernel function for the RBF models.

        Returns:
        - rbf_models: List of RBF model objects for each coefficient dimension.
        - param_scaler: Fitted scaler for parameters.
        - coeff_scaler: Fitted scaler for coefficients.
        """
        # Initialize and fit scalers
        param_scaler = MinMaxScaler().fit(training_parameters)
        coeff_scaler = MinMaxScaler().fit(training_coefficients)
        
        # Scale training data
        scaled_training_params = param_scaler.transform(training_parameters)
        scaled_training_coeffs = coeff_scaler.transform(training_coefficients)

        # Build RBF models with scaled data
        rbf_models = [
            Rbf(scaled_training_params[:, 0], scaled_training_params[:, 1], scaled_training_coeffs[:, i], function=kernel_function)
            for i in range(scaled_training_coeffs.shape[1])
        ]
        print("RBF models built successfully")

        return rbf_models, param_scaler, coeff_scaler
    
    # Main function to be passed to Helics
    def online_prediction(self, velocity, CPU_load_fraction, inlet_server_temperature,num_servers, rbf_models, param_scaler, coeff_scaler, pod_modes):
        """
        Predict the system state for new velocity, heat load fraction, and inlet_server_temperature using the 
        Reduced Order Model developed in the offline stage. Adjust the predicted temperature state 
        based on the deviation from the assumed inlet temperature of 30°C.

        Parameters:
        - velocity: New velocity value for which to predict the system state.
        - heat_load_fraction: New heat load fraction value for which to predict the system state.
        - inlet_server_temperature: inlet temperature from the assumed 30°C. This should be in °C
        - rbf_models: List of pre-built RBF model objects for predicting each coefficient dimension.
        - param_scaler: Scaler object used for parameter normalization, obtained from the offline stage.
        - coeff_scaler: Scaler object used for coefficients normalization, obtained from the offline stage.
        - pod_modes: 2D array of POD modes obtained from the offline stage.

        Returns:
        - adjusted_predicted_state: 2D array of the predicted system state for the new parameters,
                                    adjusted for the inlet temperature deviation.
        """
        

        
        # Create a 2D array from the input parameters
        new_parameters = np.array([[velocity, CPU_load_fraction]])
        
        # Normalize the new parameters using the parameter scaler
        normalized_new_params = param_scaler.transform(new_parameters)
        
        # Use the RBF models to predict the normalized coefficients for the new parameters
        predicted_normalized_coeffs = np.array([
            model(normalized_new_params[:, 0], normalized_new_params[:, 1]) for model in rbf_models
        ]).T  # Transpose to ensure correct shape
        
        # Invert the normalization of the coefficients
        predicted_coeffs = coeff_scaler.inverse_transform(predicted_normalized_coeffs)
        
        # Reconstruct the system state using the predicted coefficients and POD modes
        #The predicted state is in K
        predicted_state = np.dot(pod_modes, predicted_coeffs.T) 
        #Conveting the Tthe predicted temperatures from K to °C
        predicted_state = predicted_state-273.15
        
        # Adjust the predicted state by the temperature deviation
        # Assuming that the temperature is the quantity of interest in the predicted state
        adjusted_predicted_state = predicted_state - (30-inlet_server_temperature)
        #The above assumption only hold true when constant fluid properties are assumed i.e., the inherent assumption is that fluid properties
        # will not change significantly with changing temperature. 
        #Extrating the maximum CPU temperature from the array
        CPU_temp_max=np.max(adjusted_predicted_state)

        # Define constants
        dens = 1.225 #kg/m^3
        cp = 1006.43 #J/kgK
        server_inlet_area= 0.017560001 # in m^2
        mass_flowrate=dens*server_inlet_area*velocity
        # Load per CPU = 300 W and 2 CPU's are present in the server making total CPU laod to be 600W at 100% capcity
        # All other components RAM, power supply and HDD etc amount to 400W making the total server load to be 1000 W
        if mass_flowrate == 0:
            mass_flowrate = 0.00001
        T_out_server = inlet_server_temperature + (CPU_load_fraction * 600+400)/ (mass_flowrate * cp)

        return CPU_temp_max, T_out_server


    
    def data_center_temperature_deltas(self, 
                                       supply_temperature,
                                       server_inlet_velocity,
                                       total_ite_load_percentage,
                                       num_servers):
        """
        Calculate various temperature deltas based on the total ITE load.

        Parameters:
        - total_ite_load_percentage: The total ITE load %

        Returns:
        - calculated temperature deltas and other values.
        The average supply and return delta_T's should be used as inputs for data_center
        The max supply delta_T can should be used as input to server model 
        """
        Total_ITE_Load=80 #in KW
        ite_load = Total_ITE_Load * total_ite_load_percentage
        avg_supply_delta_T = 0.1169 * ite_load**0.9505
        avg_return_delta_T = 7.6459e-04 * ite_load**1.8956
        max_supply_del_T = 0.0173 * ite_load**1.5363 + 6.9092
        max_return_del_T = -4.7537 * np.exp(ite_load * -0.0099)

        inlet_server_temperature=supply_temperature+max_supply_del_T #Worst case scenario for the server, i.e., hihgest inlet temperature at the server inlet
        #print(inlet_server_temperature)
        # Define constants
        dens = 1.225 #kg/m^3
        cp = 1006.43 #J/kgK
        server_inlet_area= 0.017560001 # in m^2
        mass_flowrate=dens*server_inlet_area*server_inlet_velocity
        # Calculation of pressure drop across the air cooled server
        pressure_drop = 7.4066e+03 * mass_flowrate ** 1.8384 #Pa
        # Calculate energy consumption by fans to cool the CPU
        energy_consumption_by_fans_per_server = pressure_drop * mass_flowrate / dens #in Watts
        total_energy_consumption_by_fans = energy_consumption_by_fans_per_server * num_servers #in Watts
        # Load per CPU = 300 W and 2 CPU's are present in the server making total CPU laod to be 600W at 100% capcity
        # All other components RAM, power supply and HDD etc amount to 400W making the total server load to be 1000 W
        Total_server_Load=ite_load*1000-total_energy_consumption_by_fans
        heat_load_per_server=Total_server_Load/num_servers
        CPU_Load=heat_load_per_server-400 #in Watts
        CPU_Load_fraction=CPU_Load/600 # is a fraction of the total CPU load of 600W
        #print(CPU_Load_fraction)

        return avg_supply_delta_T,avg_return_delta_T, inlet_server_temperature,CPU_Load_fraction

    def run(self):
        CPU_temp_max_log =  pd.DataFrame({
            'Time': [],
            'Value': []
        }).set_index('Time')
        while self.server_federate.granted_time < self.total_time:
            self.server_federate.update_subs()
            Ts = 0
            mass_flow_rate = 0
            for sub in self.subs:
                if sub.name == "East Zone Supply Fan/Fan Air Mass Flow Rate":
                    mass_flow_rate = sub.value
                elif sub.name == "East Air Loop Outlet Node/System Node Temperature":
                    Ts = sub.value 
                elif sub.name == "Data Center CPU Loading Schedule/Schedule Value":
                    cpu_loading = sub.value
            print(f"Ts: {Ts}, mass_flow_rate: {mass_flow_rate}, cpu_loading: {cpu_loading}  at time {self.server_federate.granted_time}")
            supply_approach_temp, return_approach_temperature, inlet_server_temperature, CPU_Load_fraction = self.data_center_temperature_deltas(supply_temperature=Ts, 
                                                                                                                                            server_inlet_velocity=server_inlet_velocity, 
                                                                                                                                            total_ite_load_percentage=cpu_loading, 
                                                                                                                                            num_servers=num_servers)
            CPU_temp_max, T_out_server = self.online_prediction(server_inlet_velocity, 
                                                           CPU_Load_fraction, 
                                                           inlet_server_temperature,
                                                           num_servers, 
                                                           self.rbf_models, 
                                                           self.param_scaler, 
                                                           self.coeff_scaler, 
                                                           self.modes)
            new_data = pd.DataFrame({'Time': [self.server_federate.granted_time], 'Value': [CPU_temp_max]}).set_index('Time')
            CPU_temp_max_log = pd.concat([CPU_temp_max_log, new_data])
            
            if supply_approach_temp is not None:
                self.pubs[0].value = supply_approach_temp
            if return_approach_temperature is not None:
                self.pubs[1].value = return_approach_temperature
            self.server_federate.update_pubs()
            self.server_federate.request_time()
        # Export the DataFrame to a CSV file
        CPU_temp_max_log.to_csv('Output/time_series_data.csv')
        self.server_federate.destroy_federate()
    
    
thermal_model_runner = Server_thermal_federate()
thermal_model_runner.run()
    
