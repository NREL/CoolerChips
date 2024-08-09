import numpy as np
from mostcool.core.federate import mostcool_federate as federate
import mostcool.core.definitions as definitions
from mostcool.thermal.data_center.DC_rbf_models import build_and_scale_rbf_models, online_prediction_DC_ROM
from mostcool.thermal.data_center.surface_isolation_DC import DataCenterCGNS
from mostcool.thermal.data_center.dc_rom_outputs import dc_rom_outputs


class Datacenter_federate:
    def __init__(self) -> None:
        self.total_time = definitions.TOTAL_SECONDS
        self.modes = np.load('/app/mostcool/thermal/data_center/data/modes.npy')
        self.coefficients = np.load('/app/mostcool/thermal/data_center/data/coefficients.npy')
        self.parameter_array = np.load('/app/mostcool/thermal/data_center/data/parameter_array.npy')
        self.parameter_array = np.delete(self.parameter_array, 1, axis=1)
        # Build RBF models and scale data (to be run once)
        self.rbf_models, self.param_scaler, self.coeff_scaler = build_and_scale_rbf_models(self.parameter_array, 
                                                                                 self.coefficients, 
                                                                                 kernel_function='multiquadric')
        # Initializing surface isolation class for extracting surface temperatures
        self.datacenter = DataCenterCGNS('/app/mostcool/thermal/data_center/data/cgns_DC.cgns')
        self.datacenter_federate = federate(federate_name="Datacenter_federate",
                                            subscriptions=None,
                                            publications=None)
        self.datacenter_federate.time_interval_seconds = definitions.TIMESTEP_PERIOD_SECONDS


    def run(self):
        print("Starting datacenter federate run.")

        # Example usage for prediction
        tot_vol_flow_rate_crah = 16772.549378917283  # in cfm
        rack_flow_rate1 = 877.8471592479111  # 800cfm to 2000cfm.
        rack_heat_load1 = 5605.209396433776  # 2000W-12000W.
        rack_flow_rate2 = 831.1856050890956  # 800cfm to 2000cfm.
        rack_heat_load2 = 3274.698032971656  # 2000W-12000W.
        supply_temperature = 12  # in °C

        # Predict the temperature state
        while self.datacenter_federate.granted_time < self.total_time:
            predicted_state = online_prediction_DC_ROM(tot_vol_flow_rate_crah, rack_flow_rate1, rack_heat_load1,
                                                    rack_flow_rate2, rack_heat_load2, supply_temperature,
                                                    self.rbf_models, 
                                                    self.param_scaler, 
                                                    self.coeff_scaler, 
                                                    self.modes)


            [server_inlet_temps, server_outlet_temps, avg_crah_in, avg_crah_ret,
                        supply_approach_temp, return_approach_temp, server_locations]=dc_rom_outputs(predicted_state, self.datacenter)

            #checking outputs
            print(f'''At time: {self.datacenter_federate.granted_time}:
                  server_inlet_temps: {server_inlet_temps[:3]}...,
                  server_outlet_temps: {server_outlet_temps[:3]}...,
                  avg_crah_in: {avg_crah_in},
                  avg_crah_ret: {avg_crah_ret},
                  supply_approach_temp: {supply_approach_temp},
                  return_approach_temp: {return_approach_temp},
                  server_locations: {server_locations[:3]}...''')
            self.datacenter_federate.request_time()

        self.datacenter_federate.destroy_federate()

datacenter_model_runner =  Datacenter_federate()
datacenter_model_runner.run()