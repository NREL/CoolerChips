import helics as h
import logging


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def destroy_federate(fed):
    # Cleaning up HELICS stuff once we've finished the co-simulation.
    h.helicsFederateDestroy(fed)
    logger.info("Federate finalized")


if __name__ == "__main__":

    ##############  Registering  federate from json  ##########################
    fed = h.helicsCreateValueFederateFromConfig("ControllerConfig.json")
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
    time_interval = 60 * 10  # get this from IDF timestep?

    # Blocking call for a time request at simulation time 0
    initial_time = 60
    logger.debug(f"Requesting initial time {initial_time}")
    grantedtime = h.helicsFederateRequestTime(fed, initial_time)
    logger.debug(f"Granted time {grantedtime}")

    grantedtime = 0
    whole_building_energy = {}
    time_sim = []

    ########## Main co-simulation loop ########################################
    # As long as granted time is in the time range to be simulated...
    while grantedtime < total_interval:

        # Time request for the next physical interval to be simulated
        requested_time = grantedtime + time_interval
        # logger.debug(f"Requesting time {requested_time}")
        grantedtime = h.helicsFederateRequestTime(fed, requested_time)
        # logger.debug(f"Granted time {grantedtime}")

        for j in range(0, pub_count):
            T_delta_supply = 2
            h.helicsPublicationPublishDouble(pubid[0], T_delta_supply)
            T_delta_return = -1
            h.helicsPublicationPublishDouble(pubid[1], T_delta_return)
            # logger.debug(f"\tPublishing {h.helicsPublicationGetName(pubid[j])} value '{T_delta_supply}' at time {grantedtime}")

        for j in range(0, sub_count):
            whole_building_energy[j] = h.helicsInputGetDouble((subid[j]))

        time_sim.append(grantedtime)

    # Cleaning up HELICS stuff once we've finished the co-simulation.
    destroy_federate(fed)
