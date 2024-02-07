"""An example for how to use the EnergyPlus Python API with HELICS."""
from dataclasses import dataclass
import os
from pathlib import Path
import federate as ep_fed
import definitions
import sys

# We specify the path to the EnergyPlus installation directory
ENERGYPLUS_INSTALL_PATH = definitions.ENERGYPLUS_INSTALL_PATH
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
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        self.epw_path = epw_path
        self.idf_path = idf_path
        self.api = EnergyPlusAPI()
        self.warmup_done = False
        self.warmup_count = 0
        self.ep_federate = ep_fed.energyplus_federate()
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


    def _warmup_complete_callback(self, state):
        # There are multiple warmup periods in this IDF, so we need to go through this
        print(f"Warmup {self.warmup_count+1} complete!")
        self.warmup_count = self.warmup_count + 1
        if self.warmup_count > 2:
            self.warmup_done = True


    def _timestep_callback(self, state):
        if self.warmup_done:

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
        self.api.runtime.callback_after_new_environment_warmup_complete(
        state, self._warmup_complete_callback
        )
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
        print(f"EnergyPlus exited with code: {exit_code}, at HELICS time {self.ep_federate.granted_time}.")
        self.ep_federate.destroy_federate()


energyplus_runner = energyplus_runner(
    definitions.OUTPUT_DIR, definitions.EPW_PATH, definitions.IDF_PATH
)
energyplus_runner.run()

# plot ep_fed.results["Time"] vs ep_fed.results["Energy"]
import matplotlib.pyplot as plt

scaled_energy = [x / 1000 for x in ep_fed.results["Energy"]]
plt.plot(ep_fed.results["Time"], scaled_energy)
plt.xlabel("Time (s)")
plt.ylabel("Energy (kJ)")
plt.title("Whole Building/Facility Total Building Electricity Demand Rate")
plt.savefig((os.path.join(definitions.OUTPUT_DIR, "graphs", f"EnergyPlus Electricity Demand Rate")),
            bbox_inches="tight")
plt.show()
