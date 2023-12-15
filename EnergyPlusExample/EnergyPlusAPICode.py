"""An example for how to use the EnergyPlus Python API with HELICS."""
from dataclasses import dataclass
import federate as ep_fed
import EnergyPlusExample.definitions as definitions
import sys

# We specify the path to the EnergyPlus installation directory
ENERGYPLUS_INSTALL_PATH = "./EnergyPlus"
# Add the path to the pyenergyplus directory to sys.path
sys.path.append(ENERGYPLUS_INSTALL_PATH)
from pyenergyplus.api import EnergyPlusAPI


@dataclass
class Actuator:
    component_type: str
    control_type: str
    actuator_key: str
    sub_instance: ep_fed.Sub = None  # The current value of the acuator is stored here
    actuator_handle: str = None


@dataclass
class Sensor:
    variable_name: str
    variable_key: str
    variable_unit: str = None
    pub_instance: ep_fed.Pub = None  # The current value of the sensor is stored here
    sensor_handle: str = None


class energyplus_runner:
    def __init__(self, output_dir, epw_path, idf_path):
        self.output_dir = output_dir
        self.epw_path = epw_path
        self.idf_path = idf_path
        self.api = EnergyPlusAPI()
        self.ep_federate = ep_fed.energyplus_federate(definitions.CONFIG_PATH)
        self.actuators = [
            Actuator(
                component_type=actuator["component_type"],
                control_type=actuator["control_type"],
                actuator_key=actuator["actuator_key"],
                sub_instance=self.ep_federate.subs[
                    f'{actuator["component_type"]}/{actuator["control_type"]}/{actuator["actuator_key"]}'
                ],
            )
            for actuator in definitions.ACTUATORS
        ]
        self.sensors = [
            Sensor(
                variable_name=sensor["variable_name"],
                variable_key=sensor["variable_key"],
                variable_unit=sensor["variable_unit"],
                pub_instance=self.ep_federate.pubs[
                    f'{sensor["variable_key"]}/{sensor["variable_name"]}'
                ],
            )
            for sensor in definitions.SENSORS
        ]

    def set_actuators(self, state):
        for actuator in self.actuators:
            handle = self.api.exchange.get_actuator_handle(
                state,
                actuator.component_type,
                actuator.control_type,
                actuator.actuator_key,
            )
            self.api.exchange.set_actuator_value(
                state, handle, actuator.sub_instance.value
            )

    def get_sensors(self, state):
        for sensor in self.sensors:
            handle = self.api.exchange.get_variable_handle(
                state, sensor.variable_name, sensor.variable_key
            )
            sensor.pub_instance.value = self.api.exchange.get_variable_value(
                state, handle
            )

    def _timestep_callback(self, state):
        if self.api.exchange.warmup_flag(state) == 0:

            # Request next time
            self.ep_federate.request_time()

            # Get subbed actuator values and set them in EnergyPlus
            self.ep_federate.update_actuators()
            self.set_actuators(state)

            # Get sensor values from EnergyPlus and publish them
            self.get_sensors(state)
            self.ep_federate.update_sensors()

    def run(self):
        state = self.api.state_manager.new_state()
        # Register callbacks
        self.api.runtime.callback_end_zone_timestep_after_zone_reporting(
            state, self._timestep_callback
        )
        # Run EnergyPlus
        exit_code = self.api.runtime.run_energyplus(
            state,
            [
                "-r",
                "-d",
                self.output_dir,
                "-w",
                self.epw_path,
                self.idf_path,
            ],
        )
        print(f"EnergyPlus exited with code: {exit_code}")
        self.ep_federate.destroy_federate()


energyplus_runner = energyplus_runner(
    definitions.OUTPUT_DIR, definitions.EPW_PATH, definitions.IDF_PATH
)
energyplus_runner.run()

# plot ep_fed.results["Time"] vs ep_fed.results["Energy"]
import matplotlib.pyplot as plt

plt.plot(ep_fed.results["Time"], ep_fed.results["Energy"])
plt.xlabel("Time (s)")
plt.ylabel("Energy (J)")
plt.show()
