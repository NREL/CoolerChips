import helics as h
import logging


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)



def destroy_federate(fed):
    """
    As part of ending a HELICS co-simulation it is good housekeeping to
    formally destroy a federate. Doing so informs the rest of the
    federation that it is no longer a part of the co-simulation and they
    should proceed without it (if applicable). Generally this is done
    when the co-simulation is complete and all federates end execution
    at more or less the same wall-clock time.

    :param fed: Federate to be destroyed
    :return: (none)
    """
    # Adding extra time request to clear out any pending messages to avoid
    #   annoying errors in the broker log. Any message are tacitly disregarded.
    grantedtime = h.helicsFederateRequestTime(fed, h.HELICS_TIME_MAXTIME)
    status = h.helicsFederateDisconnect(fed)
    h.helicsFederateDestroy(fed)
    logger.info("Federate finalized")


if __name__ == "__main__":

    ##############  Registering  federate from json  ##########################
    fed = h.helicsCreateValueFederateFromConfig("ThermostatConfig.json")
    federate_name = h.helicsFederateGetName(fed)
    logger.info(f"Created federate {federate_name}")

    sub_count = h.helicsFederateGetInputCount(fed)
    logger.debug(f"\tNumber of subscriptions: {sub_count}")
    pub_count = h.helicsFederateGetPublicationCount(fed)
    logger.debug(f"\tNumber of publications: {pub_count}")

    # Diagnostics to confirm JSON config correctly added the required
    #   publications, and subscriptions.
    subid = {}
    for i in range(0, sub_count):
        subid[i] = h.helicsFederateGetInputByIndex(fed, i)
        sub_name = h.helicsSubscriptionGetTarget(subid[i])
        logger.debug(f"\tRegistered subscription---> {sub_name}")

    pubid = {}
    for i in range(0, pub_count):
        pubid[i] = h.helicsFederateGetPublicationByIndex(fed, i)
        pub_name = h.helicsPublicationGetName(pubid[i])
        logger.debug(f"\tRegistered publication---> {pub_name}")

    ##############  Entering Execution Mode  ##################################
    h.helicsFederateEnterExecutingMode(fed)
    logger.info("Entered HELICS execution mode")
    
    
    number_of_days = 365 
    total_timesteps = 24 * 7 * number_of_days
    total_interval = total_timesteps * 60
    time_interval = 60 * 10 # get this from IDF timestep?
    temp_dict = {'time':[], 'temperature':[]}
    
    # Blocking call for a time request at simulation time 0
    initial_time = 60
    logger.debug(f"Requesting initial time {initial_time}")
    grantedtime = h.helicsFederateRequestTime(fed, initial_time)
    logger.debug(f"Granted time {grantedtime}")
    
    grantedtime = 0
    zone_temp = {}
    time_sim = []


    ########## Main co-simulation loop ########################################
    # As long as granted time is in the time range to be simulated...
    while grantedtime < total_interval:

        # Time request for the next physical interval to be simulated
        requested_time = grantedtime + time_interval
        logger.debug(f"Requesting time {requested_time}")
        grantedtime = h.helicsFederateRequestTime(fed, requested_time)
        logger.debug(f"Granted time {grantedtime}")
        
        for j in range(0, pub_count):
            T_delta_supply = 4
            h.helicsPublicationPublishDouble(pubid[0], T_delta_supply)
            T_delta_return = -1
            h.helicsPublicationPublishDouble(pubid[1], T_delta_return)
            logger.debug(f"\tPublishing {h.helicsPublicationGetName(pubid[j])} value '{T_delta_supply}' at time {grantedtime}")            

        for j in range(0, sub_count):
            logger.debug(f"Thermostat {j + 1} time {grantedtime}")            
            zone_temp[j] = h.helicsInputGetDouble((subid[j]))
            logger.debug(f"\tZone Temperature: {zone_temp[j]:.2f} from"
                        f" input {h.helicsSubscriptionGetTarget(subid[j])}")
            
        time_sim.append(grantedtime)
            

    # Cleaning up HELICS stuff once we've finished the co-simulation.
    destroy_federate(fed)