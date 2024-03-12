from dataclasses import dataclass
import definitions
import logging


@dataclass
class Pub:
    name: str
    id: int
    value: float = None


@dataclass
class Sub:
    name: str
    id: int
    value: float = None


class mostcool_federate:
    def __init__(self, federate_name=None):
        import helics as h

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.subs = {}
        self.pubs = {}
        self.granted_time = 0
        self.federate = None
        self.setup_helics_federate(federate_name)
        self.time_interval_seconds = int(
            h.helicsFederateGetTimeProperty(
                self.federate, h.HELICS_PROPERTY_TIME_PERIOD
            )
        )
        self.logger.debug(f"Time interval is {self.time_interval_seconds} seconds")
        
    def create_value_federate(self, fedinitstring, name, period):
        """Create a value federate with the given name and time period."""
        import helics as h
        
        fedinfo = h.helicsCreateFederateInfo()
        h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")  # ZMQ is the default and works well for small co-simulations
        h.helicsFederateInfoSetCoreInitString(fedinfo, fedinitstring)  # Can be used to set number of federates, etc
        h.helicsFederateInfoSetIntegerProperty(fedinfo, h.HELICS_PROPERTY_INT_LOG_LEVEL, definitions.LOG_LEVEL_MAP["helics_log_level_trace"])
        h.helicsFederateInfoSetTimeProperty(fedinfo, h.HELICS_PROPERTY_TIME_PERIOD, period)
        h.helicsFederateInfoSetFlagOption(fedinfo, h.HELICS_FLAG_UNINTERRUPTIBLE, True)  # Forces the granted time to be the requested time (i.e., EnergyPlus timestep)
        h.helicsFederateInfoSetFlagOption(fedinfo, h.HELICS_FLAG_TERMINATE_ON_ERROR, True)  # Stop the whole co-simulation if there is an error
        h.helicsFederateInfoSetFlagOption(
            fedinfo, h.HELICS_FLAG_WAIT_FOR_CURRENT_TIME_UPDATE, True
        )  # This makes sure that this federate will be the last one granted a given time step. Thus it will have the most up-to-date values for all other federates.
        fed = h.helicsCreateValueFederate(name, fedinfo)
        return fed                                          

    # Function to create and configure HELICS federate
    def setup_helics_federate(self, federate_name=None):
        import helics as h
        self.federate = self.create_value_federate("", federate_name, definitions.TIMESTEP_PERIOD_SECONDS)
        self.logger.info(f"HELICS federate for {federate_name} created.")
        self.register_pubs()
        self.register_subs()
        h.helicsFederateEnterExecutingMode(self.federate)
        self.logger.info("Entered HELICS execution mode")

    def register_pubs(self):  # Sensors
        import helics as h

        for i in range(0, len(definitions.SENSORS)):
            self.logger.info(
                f'Registering publication: {definitions.SENSORS[i]["variable_key"]}/{definitions.SENSORS[i]["variable_name"]}'
            )
            pubid = h.helicsFederateRegisterGlobalTypePublication(
                self.federate,
                f'{definitions.SENSORS[i]["variable_key"]}/{definitions.SENSORS[i]["variable_name"]}',
                "double",
                definitions.SENSORS[i]["variable_unit"],
            )
            pub_name = h.helicsPublicationGetName(pubid)
            if pub_name not in self.pubs:
                self.pubs[pub_name] = Pub(name=pub_name, id=pubid)
            self.logger.debug(f"\tRegistered publication---> {pubid} as {pub_name}")

    def register_subs(self):  # Actuators
        import helics as h

        for i in range(0, len(definitions.ACTUATORS)):
            self.logger.info(
                f'Registering subscription: {definitions.ACTUATORS[i]["component_type"]}/{definitions.ACTUATORS[i]["control_type"]}/{definitions.ACTUATORS[i]["actuator_key"]}'
            )
            subid = h.helicsFederateRegisterSubscription(
                self.federate,
                f'{definitions.ACTUATORS[i]["component_type"]}/{definitions.ACTUATORS[i]["control_type"]}/{definitions.ACTUATORS[i]["actuator_key"]}',
                definitions.ACTUATORS[i]["actuator_unit"],
            )
            sub_name = h.helicsInputGetTarget(subid)
            if sub_name not in self.subs:
                self.subs[sub_name] = Sub(name=sub_name, id=subid)
            self.logger.debug(f"\tRegistered subscription---> {sub_name}")

    def request_time(self):
        import helics as h

        requested_time_seconds = self.granted_time + self.time_interval_seconds
        self.granted_time = h.helicsFederateRequestTime(
            self.federate, requested_time_seconds
        )
        self.logger.debug(
            f"Requested time {requested_time_seconds}, granted time {self.granted_time}"
        )
        return self.granted_time

    def update_subs(self):
        import helics as h

        for sub_key in self.subs:
            if h.helicsInputIsUpdated(self.subs[sub_key].id):
                self.subs[sub_key].value = h.helicsInputGetDouble(self.subs[sub_key].id)
            else:
                self.subs[sub_key].value = 0
                self.logger.warning(f"{sub_key} was not updated at {self.granted_time}, set to zero.")

        return self.subs

    def update_pubs(self):
        import helics as h

        for pub_key in self.pubs:
            h.helicsPublicationPublishDouble(
                self.pubs[pub_key].id, self.pubs[pub_key].value
            )

    # Function to clean up HELICS federate
    def destroy_federate(self):
        import helics as h

        h.helicsFederateDisconnect(self.federate)
        h.helicsFederateFree(self.federate)
        h.helicsCloseLibrary()
