import time
import helics as h
import logging


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

PUBS = [{"Name": "Schedule:Constant/Schedule Value/Supply Temperature Difference Schedule Mod",
         "Type": "double",
         "Units": "C",
         "Global": True},
        {"Name": "Schedule:Constant/Schedule Value/Return Temperature Difference Schedule Mod",
         "Type": "double",
         "Units": "C",
         "Global": True}]

SUBS = [{"Name": "Whole Building/Facility Total Building Electricity Demand Rate",
              "Type": "double",
              "Units": "J",
              "Global": True}]

def create_value_federate(fedinitstring, name, period):
    """Create a value federate with the given name and time period."""
    
    fedinfo = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")  # ZMQ is the default and works well for small co-simulations
    h.helicsFederateInfoSetCoreInitString(fedinfo, fedinitstring)  # Can be used to set number of federates, etc
    h.helicsFederateInfoSetIntegerProperty(fedinfo, h.HELICS_PROPERTY_INT_LOG_LEVEL, 1) 
    h.helicsFederateInfoSetTimeProperty(fedinfo, h.HELICS_PROPERTY_TIME_PERIOD, period)
    h.helicsFederateInfoSetFlagOption(fedinfo, h.HELICS_FLAG_UNINTERRUPTIBLE, True)  # Forces the granted time to be the requested time (i.e., EnergyPlus timestep)
    h.helicsFederateInfoSetFlagOption(fedinfo, h.HELICS_FLAG_TERMINATE_ON_ERROR, True)  # Stop the whole co-simulation if there is an error
    h.helicsFederateInfoSetFlagOption(
        fedinfo, h.HELICS_FLAG_WAIT_FOR_CURRENT_TIME_UPDATE, False
    )  #This makes sure that this federate will be the last one granted a given time step. Thus it will have the most up-to-date values for all other federates.
    fed = h.helicsCreateValueFederate(name, fedinfo)
    return fed


def destroy_federate(fed):
    """ Cleaning up HELICS stuff once we've finished the co-simulation. """
    h.helicsFederateDestroy(fed)
    logger.info("Federate finalized")


if __name__ == "__main__":

    ##############  Registering  federate  ##########################
    fedinitstring = " --federates=1"
    name = "Controller"
    period = 10
    fed = create_value_federate(fedinitstring, name, period)
    
    federate_name = h.helicsFederateGetName(fed)
    logger.info(f"Created federate {federate_name}")
    
    pubid = {}
    for i in range(0, len(PUBS)):
        pubid[i] = h.helicsFederateRegisterGlobalTypePublication(
            fed, PUBS[i]["Name"] , PUBS[i]["Type"], PUBS[i]["Units"]
        )
        pub_name = h.helicsPublicationGetName(pubid[i])
        logger.debug(f"\tRegistered publication---> {pub_name}")

    subid = {}
    for i in range(0, len(SUBS)):
        subid[i] = h.helicsFederateRegisterSubscription(fed, SUBS[i]["Name"], SUBS[i]["Units"])
        sub_name = h.helicsInputGetTarget(subid[i])
        logger.debug(f"\tRegistered subscription---> {sub_name}")
        
    sub_count = h.helicsFederateGetInputCount(fed)
    logger.debug(f"\tNumber of subscriptions: {sub_count}")
    pub_count = h.helicsFederateGetPublicationCount(fed)
    logger.debug(f"\tNumber of publications: {pub_count}")

    ##############  Entering Execution Mode  ##################################
    h.helicsFederateEnterExecutingMode(fed)
    logger.info("Entered HELICS execution mode")

    number_of_days = 365
    total_hours = 24 * number_of_days
    total_seconds = total_hours * 60 * 60
    # time_interval_seconds = 10  # get this from IDF timestep?
    time_interval_seconds = int(h.helicsFederateGetTimeProperty(
                            fed,
                            h.HELICS_PROPERTY_TIME_PERIOD))
    logger.debug(f"Time interval is {time_interval_seconds} seconds")

    # Blocking call for a time request at simulation time 0
    initial_time = 0
    
    logger.debug(f"Current time is {h.helicsFederateGetCurrentTime(fed)}. Requesting initial time {initial_time}")
    grantedtime = h.helicsFederateRequestTime(fed, initial_time)
    logger.debug(f"Granted time {grantedtime}")

    grantedtime = 0

    ########## Main co-simulation loop ########################################
    # As long as granted time is in the time range to be simulated...
    while grantedtime < total_seconds:

        # Time request for the next physical interval to be simulated
        requested_time_seconds = grantedtime + time_interval_seconds
        # logger.debug(f"Requesting time {requested_time}")
        grantedtime = h.helicsFederateRequestTime(fed, requested_time_seconds)
        # logger.debug(f"Granted time {grantedtime} seconds while requested time {requested_time_seconds} seconds with time interval {time_interval_seconds} seconds")

        T_delta_supply = 3 + grantedtime / 1000000000
        h.helicsPublicationPublishDouble(pubid[0], T_delta_supply)
        T_delta_return = -1
        h.helicsPublicationPublishDouble(pubid[1], T_delta_return)
        # logger.debug(f"\tPublishing {h.helicsPublicationGetName(pubid[0])} value '{T_delta_supply}'.")


    # Cleaning up HELICS stuff once we've finished the co-simulation.
    destroy_federate(fed)
