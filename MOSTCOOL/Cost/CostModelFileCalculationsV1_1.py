import matplotlib
matplotlib.use('Agg')  # Use the non-interactive backend
import math
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from CostModelFileProcessingV1_1 import table_lookup

Cooling_System_Details_Ref = {
    "chiller": {
        "Name": 'Chiller',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    },
    "coolingTower": {
        "Name": 'Cooling Tower',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    },
    "pump": {
        "Name": 'Pump',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    },
    "fluid": {
        "Name": 'Fluid',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    },
    "ducting": {
        "Name": 'Ducting',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    },
    "piping": {
        "Name": 'Piping',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    },
    "CRAH": {
        "Name": 'Computer Room Air Handler',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    },
    "air_Economizer": {
        "Name": 'Air Economizer',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    }
}

Cooling_System_Details_Analysis = {
    "chiller": {
        "Name": 'Chiller',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    },
    "coolingTower": {
        "Name": 'Cooling Tower',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    },
    "pump": {
        "Name": 'Pump',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    },
    "fluid": {
        "Name": 'Fluid',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    },
    "ducting": {
        "Name": 'Ducting',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    },
    "piping": {
        "Name": 'Piping',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    },
    "CRAH": {
        "Name": 'Computer Room Air Handler',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    },
    "air_Economizer": {
        "Name": 'Air Economizer',
        "Units": 'per_datacenter',  # Adding Units field
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "Total_cost_of_cooling_system": 0.0,
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_Type": 'Cost per maintenance'  # Adding Maintenance Type field
    }
}

variables = {
    "Duration of Simulation (years)": "20",
    "Electricity Cost ($/Wh)": "0.000145",
    "Energy Inflation (per year)": "0.0224",
    "Inflation (per year)": "0.035",
    "Discount Rate (per year)": "0.06",
    "IT Maintenance Cost (per event)": "250000",
    "Cost of Cooling Fluid ($/gallon)": "10.65",
    "Data Center Capacity (W)": "1000",
    "CEPCI Number": "8.008",
    "IT MTBF for the Reference Cooling System (seconds)": "5000",
    "IT MTBF for the Analysis Cooling System (seconds)": "6000",
    "Recovered Heat (fraction of energy cost)": "0.1",
    "Piping Size (Diameter meters)": "4",
    "Duct Size (sq m.)": "4"
}

dataCenterDetails = {
    "Number of Rooms": "2",
    "Number of Rows": "4",
    "Number of Racks": "8",
    "Number of Servers": "16"
}

def chiller_calculator(capacity_value):
    if isinstance(capacity_value, str):
        capacity_value = capacity_value.replace('$', '').replace(',', '')
        capacity_value = float(capacity_value)
    
    chiller_BTU_hr = float(capacity_value) / 3.412
    chiller_Tons_hr = chiller_BTU_hr / 12000
    chiller_Tons = chiller_Tons_hr * 1.2

    if chiller_Tons < 50:
        chiller_cost = chiller_Tons * 1500
    elif chiller_Tons < 150:
        chiller_cost = chiller_Tons * 700
    else:
        chiller_cost = chiller_Tons * 450

    chiller_cost = math.ceil(chiller_cost)  # Always round up to the nearest dollar

    return chiller_cost

def cooling_tower_calculator(capacity_value):
    if isinstance(capacity_value, int):
        capacity_value = str(capacity_value)
    
    capacity_value = capacity_value.replace('$', '').replace(',', '')
    capacity_value = float(capacity_value)
    
    cooling_tower_BTU_hr = float(capacity_value) / 3.412
    cooling_tower_Tons_hr = cooling_tower_BTU_hr / 12000
    cooling_tower_Tons = cooling_tower_Tons_hr * 1.2

    if cooling_tower_Tons < 10:
        cooling_tower_cost = cooling_tower_Tons * 1500
    elif cooling_tower_Tons < 50:
        cooling_tower_cost = cooling_tower_Tons * 1250
    else:
        cooling_tower_cost = cooling_tower_Tons * 750

    cooling_tower_cost = math.ceil(cooling_tower_cost)  # Always round up to the nearest dollar

    return cooling_tower_cost

def pump_calculator(power_consumption_value, CEPCI_Number):
    if isinstance(power_consumption_value, int):
        power_consumption_value = str(power_consumption_value)
            
    pump_cost = ((9500 * float(power_consumption_value) / (23 * 1000)) ** 0.79) * CEPCI_Number
    
    pump_cost = math.ceil(pump_cost)  # Always round up to the nearest dollar

    return pump_cost

def duct_calculator(volume_value, estimate_duct_size, CEPCI_Number):
    if isinstance(volume_value, int):
        volume_value = str(volume_value)
    duct_cost = (700 / estimate_duct_size) * float(volume_value) * CEPCI_Number
    
    duct_cost = math.ceil(duct_cost)  # Always round up to the nearest dollar

    return duct_cost

def pipe_calculator(volume_value, estimate_pipe_size, CEPCI_Number):
    if isinstance(volume_value, int):
        volume_value = str(volume_value)
    
    piping_cost = (80 / estimate_pipe_size) * float(volume_value) * CEPCI_Number
    
    piping_cost = math.ceil(piping_cost)  # Always round up to the nearest dollar

    return piping_cost

def CRAH_calculator(data_center_capacity):
    crah_cost = data_center_capacity * 240
    
    crah_cost = math.ceil(crah_cost)  # Always round up to the nearest dollar

    return crah_cost

def air_economizer_calculator(data_center_capacity):
    air_economizer_cost = data_center_capacity * 132.4
    
    air_economizer_cost = math.ceil(air_economizer_cost)  # Always round up to the nearest dollar

    return air_economizer_cost

def fluid_calculator(volume_value):
    total_volume_gallons = float(volume_value) * 264.172
    fluid_cost = (total_volume_gallons * (1.1 * 12)) / 10000 * 10.65
    
    fluid_cost = math.ceil(fluid_cost)  # Always round up to the nearest dollar

    return fluid_cost

def get_redundancy_multiplier(redundancy):
    if redundancy == "N":
        return 1
    elif redundancy == "N+1":
        return 2
    elif redundancy == "N+2":
        return 3  
    elif redundancy == "2N":
        return 2
    elif redundancy == "2N+1":
        return 3
    else:
        return 1  # Default to 1 if redundancy is not recognized

def update_cooling_system_details(mtbf, gamma, beta, eta, cost_per_maintenance_event, system="reference"):
    details = Cooling_System_Details_Ref if system == "reference" else Cooling_System_Details_Analysis
    if table_lookup["chiller"]["value"]:
        details["chiller"]["Cost_per_equipment"] = chiller_calculator(table_lookup["chiller"]["value"])
    if table_lookup["coolingTower"]["value"]:
        details["coolingTower"]["Cost_per_equipment"] = cooling_tower_calculator(table_lookup["coolingTower"]["value"])
    if table_lookup["pump_power"]["value"]:
        details["pump"]["Cost_per_equipment"] = pump_calculator(table_lookup["pump_power"]["value"], float(variables["CEPCI Number"]))
    if table_lookup["airloopHVAC"]["value"]:
        details["ducting"]["Cost_per_equipment"] = duct_calculator(table_lookup["airloopHVAC"]["value"], float(variables["Duct Size (sq m.)"]), float(variables["CEPCI Number"]))
    if table_lookup["plantLoop"]["value"]:
        details["piping"]["Cost_per_equipment"] = pipe_calculator(table_lookup["plantLoop"]["value"], float(variables["Piping Size (Diameter meters)"]), float(variables["CEPCI Number"]))
        details["fluid"]["Cost_per_equipment"] = fluid_calculator(table_lookup["plantLoop"]["value"])
    details["CRAH"]["Cost_per_equipment"] = CRAH_calculator(float(variables["Data Center Capacity (W)"]))
    details["air_Economizer"]["Cost_per_equipment"] = air_economizer_calculator(float(variables["Data Center Capacity (W)"]))

    for component in details.values():
        component["MTBF"] = mtbf
        component["Gamma"] = gamma
        component["Beta"] = beta
        component["Eta"] = eta
        component["Cost_per_maintenance_event"] = cost_per_maintenance_event
        if component["Cost_per_equipment"] == '':
            component["Cost_per_equipment"] = 0.0
        component["Total_cost_of_cooling_system"] = float(component["Cost_per_equipment"]) * get_redundancy_multiplier(component["Redundancy"])


def get_cooling_system_details(system="reference"):
    details = [["Name", "Units", "Cost per Equipment", "Redundancy", "Total Cost", "MTBF", "Gamma (hours)", "Beta", "Eta (hours)", "Cost per Maintenance Event", "Maintenance Type"]]
    cooling_system = Cooling_System_Details_Ref if system == "reference" else Cooling_System_Details_Analysis
    for component, data in cooling_system.items():
        details.append([
            data['Name'],
            'per_datacenter',  # Default units
            format_currency(data.get('Cost_per_equipment', 0.0)),
            data.get('Redundancy', 'N'),
            format_currency(data.get('Total_cost_of_cooling_system', 0.0)),
            data.get('MTBF', ''),
            data.get('Gamma', 0.0),
            data.get('Beta', ''),
            data.get('Eta', 0.0),
            format_currency(data.get('Cost_per_maintenance_event', 0.0)),
            data.get('Maintenance_type', 'Cost per maintenance'),
        ])
    return details

def calculate_total_cooling_cost(system="reference"):
    cooling_system = Cooling_System_Details_Ref if system == "reference" else Cooling_System_Details_Analysis
    total_cost = sum(
        float(component["Total_cost_of_cooling_system"].replace(',', '').replace('$', '')) 
        if isinstance(component["Total_cost_of_cooling_system"], str) 
        else float(component["Total_cost_of_cooling_system"])
        for component in cooling_system.values() 
        if component["Total_cost_of_cooling_system"]
    )
    return total_cost


def format_currency(value):
    try:
        value = float(value)
    except ValueError:
        value = 0.0
    return "${:,.2f}".format(value)

class MonteCarloMaintenance:
    def __init__(self, monte_carlo=True, samples=1, number_items=3):
        self.monte_carlo = monte_carlo
        self.samples = samples
        self.number_items = number_items
        self.fail_dist_gamma = np.zeros(4000)  # max of 4000 items
        self.fail_dist_beta = np.zeros(4000)
        self.fail_dist_eta = np.zeros(4000)
        self.maint_cost = np.zeros(4000)
        self.next_failure = np.zeros(4000)
        self.year_cost = np.zeros(100)  # max of 100 years

    def run_simulation(self, stype, dura, input_data):
        # Convert duration to seconds
        dura = dura * 365 * 24 * 60 * 60  # sec

        # Determine if Monte Carlo simulation is to be used
        self.monte_carlo = (stype == "Yes")

        if not self.monte_carlo:
            self.samples = 1

        # Get input data and initialize distributions
        for i, data in enumerate(input_data):
            x, gamma1, beta, eta, cost = data
            if x > 0:
                lambda_val = 1 / x  # 1/hours
            else:
                lambda_val = -1

            # Convert to a Weibull or collect Weibull parameters
            if lambda_val > 0:
                gamma1 = 0
                beta = 1
                eta = 1 / lambda_val
            self.fail_dist_gamma[i] = gamma1 * 60 * 60  # sec
            self.fail_dist_beta[i] = beta
            self.fail_dist_eta[i] = eta * 60 * 60  # sec
            self.maint_cost[i] = cost  # $

        # Initialize the costs accumulations
        self.year_cost.fill(0)

        # Monte Carlo loop
        for _ in range(self.samples):
            self._initialize_failures(dura)
            self._simulate_failures(dura)

        # Print annual costs
        x = int(dura / 365 / 24 / 60 / 60)
        sum_cost = np.sum(self.year_cost[:x]) / self.samples
        return [(k, self.year_cost[k] / self.samples) for k in range(1, x+1)], sum_cost / x

    def _initialize_failures(self, dura):
        self.next_failure.fill(dura)
        for i in range(self.number_items):
            self._sample_weibull(0, i)

    def _simulate_failures(self, dura):
        clock = 0
        for _ in range(200):
            ff, failure_i = min((self.next_failure[i], i) for i in range(self.number_items))
            clock = ff
            if clock >= dura:
                break
            self._sum_cost(clock, failure_i)
            self._sample_weibull(clock, failure_i)

    def _sample_weibull(self, clock, i):
        if self.monte_carlo:
            F = np.random.rand()
            Power = 1 / self.fail_dist_beta[i]
            logx = np.log(1 - F)
            self.next_failure[i] = clock + self.fail_dist_gamma[i] + self.fail_dist_eta[i] * ((-logx) ** Power)
        else:
            self.next_failure[i] = clock + self.fail_dist_gamma[i] + self.fail_dist_eta[i] * self._gamma(1 + 1 / self.fail_dist_beta[i])

    def _sum_cost(self, clock, i):
        y = int(clock / 365 / 24 / 60 / 60) + 1
        self.year_cost[y] += self.maint_cost[i]

    @staticmethod
    def _gamma(x):
        from scipy.special import gamma
        return gamma(x)

def calculate_irr():
    # Update variables from the settings window (if applicable)
    # self.update_variables_from_settings()

    # Inputs
    SimulationDuration = float(variables["Duration of Simulation (years)"]) 
    TimeStepMultiplier = 1  # 12 for every month/4 for every quarter/1 for every year
    
    # Default Inputs
    ElectricityCost = float(variables["Electricity Cost ($/Wh)"]) * 1000  # convert to $/kWh
    EnergyInflation = float(variables["Energy Inflation (per year)"])
    Inflation = float(variables["Inflation (per year)"])
    DiscountRate = float(variables["Discount Rate (per year)"])
    ITMaintenanceCost = float(variables["IT Maintenance Cost (per event)"])
    RecoveredHeatValue = float(variables["Recovered Heat (fraction of energy cost)"])

    # Adjust time step
    SimulationDuration = SimulationDuration * TimeStepMultiplier
    
    # Baseline Inputs
    B_CapitolCost = float(calculate_total_cooling_cost()) / 1000000  # million dollars
    B_Life = 9  # 9
    B_MTBF = 180000  # self.MTBF1
    CoolingMaintenanceCost = 250000  # self.CostPerMaintenanceEvent1
    B_IT_MTBF = float(variables["IT MTBF for the Analysis Cooling System (seconds)"]) / (60 * 60)  # convert to hours
    B_EnergyUsage = 250  # million kWh
    B_AvoidedITFailures = 0
    B_AnnualRecoveredHeat = 1200  # million kWh

    # New Inputs
    N_CapitolCost = float(calculate_total_cooling_cost("Analysis")) / 1000000  # million dollars
    N_Life = 12  # 12
    N_MTBF = 60000  # self.MTBF2
    CoolingMaintenanceCost2 = 300000  # self.CostPerMaintenanceEvent2
    N_IT_MTBF = float(variables["IT MTBF for the Analysis Cooling System (seconds)"]) / (60 * 60)  # convert to hours
    N_EnergyUsage = 262.8  # million kWh
    N_AvoidedITFailures = 0.5
    N_AnnualRecoveredHeat = 1314  # million kWh

    print(N_CapitolCost)
    print(B_CapitolCost)

    # Individual Expenses and Revenue Calculations for baseline
    B_Time = []
    B_Capitol = []
    B_EnergyCost = []
    B_CoolingMaintenance = []
    B_ITMaintenance = []
    B_HeatRevenue = []
    B_Net = []
    B_NPV = []
    B_CumNPV = []

    i = 0
    while i <= SimulationDuration:
        B_Time.append(i)

        # Capitol Costs
        if i % B_Life == 0:
            B_Capitol.append(B_CapitolCost * (1 + Inflation) ** i)
        else:
            B_Capitol.append(0)

        # Energy Costs
        if i > 0:
            B_EnergyCost.append(ElectricityCost * B_EnergyUsage * (1 + EnergyInflation) ** (i - 1))
        else:
            B_EnergyCost.append(0)

        # Cooling Maintenance
        if i > 0:
            B_CoolingMaintenance.append(((B_MTBF / 8760) * CoolingMaintenanceCost * (1 + Inflation) ** i) / 1000000)
        else:
            B_CoolingMaintenance.append(0)

        # IT Maintenance
        if i > 0:
            B_ITMaintenance.append((-B_AvoidedITFailures * ITMaintenanceCost * (1 + Inflation) ** i) / 1000000)
        else:
            B_ITMaintenance.append(0)

        # Heat Revenue
        if i > 0:
            B_HeatRevenue.append(-B_AnnualRecoveredHeat * RecoveredHeatValue * ElectricityCost * (1 + EnergyInflation) ** (i - 1))
        else:
            B_HeatRevenue.append(0)

        # Net
        B_Net.append(B_Capitol[i] + B_EnergyCost[i] + B_CoolingMaintenance[i] + B_ITMaintenance[i] + B_HeatRevenue[i])

        # NPV
        B_NPV.append(B_Capitol[i] / (1 + DiscountRate) ** i + B_EnergyCost[i] / (1 + DiscountRate) ** i + B_CoolingMaintenance[i] / (1 + DiscountRate) ** i + B_ITMaintenance[i] / (1 + DiscountRate) ** i + B_HeatRevenue[i] / (1 + DiscountRate) ** i)

        # Cum NPV
        B_CumNPV = np.cumsum(B_NPV)

        # IO (PV)
        IO = B_CapitolCost

        i = i + 1

    # Individual Expenses and Revenue Calculations for New
    N_Time = []
    N_Capitol = []
    N_EnergyCost = []
    N_CoolingMaintenance = []
    N_ITMaintenance = []
    N_HeatRevenue = []
    N_Net = []
    N_NPV = []
    N_CumNPV = []

    i = 0
    while i <= SimulationDuration:
        N_Time.append(i)

        # Capitol Costs
        if i % N_Life == 0:
            N_Capitol.append(N_CapitolCost * (1 + Inflation) ** i)
        else:
            N_Capitol.append(0)

        # Energy Costs
        if i > 0:
            N_EnergyCost.append(ElectricityCost * N_EnergyUsage * (1 + EnergyInflation) ** (i - 1))
        else:
            N_EnergyCost.append(0)

        # Cooling Maintenance
        if i > 0:
            N_CoolingMaintenance.append(((N_MTBF / 8760) * CoolingMaintenanceCost2 * (1 + Inflation) ** i) / 1000000)
        else:
            N_CoolingMaintenance.append(0)

        # IT Maintenance
        if i > 0:
            N_ITMaintenance.append((-N_AvoidedITFailures * ITMaintenanceCost * (1 + Inflation) ** i) / 1000000)
        else:
            N_ITMaintenance.append(0)

        # Heat Revenue
        if i > 0:
            N_HeatRevenue.append(-N_AnnualRecoveredHeat * RecoveredHeatValue * ElectricityCost * (1 + EnergyInflation) ** (i - 1))
        else:
            N_HeatRevenue.append(0)

        # Net
        N_Net.append(N_Capitol[i] + N_EnergyCost[i] + N_CoolingMaintenance[i] + N_ITMaintenance[i] + N_HeatRevenue[i])

        # NPV
        N_NPV.append(N_Capitol[i] / (1 + DiscountRate) ** i + N_EnergyCost[i] / (1 + DiscountRate) ** i + N_CoolingMaintenance[i] / (1 + DiscountRate) ** i + N_ITMaintenance[i] / (1 + DiscountRate) ** i + N_HeatRevenue[i] / (1 + DiscountRate) ** i)

        # Cum NPV
        N_CumNPV = np.cumsum(N_NPV)

        # Inew (PV)
        Inew = N_CapitolCost

        i = i + 1

    # ROI and IRR Calculations
    i = 0
    ROI = []
    IRR = []
    Net_NPV = []
    
    while i <= SimulationDuration:
        # ROI Calc
        if Inew - IO > 0:
            ROI.append((B_CumNPV[i] - N_CumNPV[i]) / (Inew - IO))
        else:
            ROI.append(0)
        # IRR Calc
        if i > 0:
            IRR.append((1 + ROI[i]) ** (1 / i) - 1)
        else:
            IRR.append(0)
            
        Net_NPV.append(B_NPV[i] - N_NPV[i])
        i = i + 1      

    print(ROI)
    print(IRR)
    print(Net_NPV)

    return SimulationDuration, ROI, IRR, Net_NPV

def generategraphs (Time, ROI, IRR, Net_NPV):
    # Create Matplotlib figures and axes for both ROI and IRR plots
        fig_ROI, ax_ROI = plt.subplots(figsize=(7, 5))  # Set a fixed figsize for ROI plot
        fig_IRR, ax_IRR = plt.subplots(figsize=(7, 5))  # Set a fixed figsize for IRR plot
        fig_NPV, ax_NPV = plt.subplots(figsize=(7, 5))  # Set a fixed figsize for NPV plot

        # Plot ROI
        ax_ROI.scatter(Time, ROI)
        ax_ROI.grid()
        ax_ROI.set_xlabel('Year')
        ax_ROI.set_ylabel('ROI')
        ax_ROI.set_title('ROI')

        # Plot IRR
        ax_IRR.scatter(Time, IRR)
        ax_IRR.grid()
        ax_IRR.set_xlabel('Year')
        ax_IRR.set_ylabel('IRR')
        ax_IRR.set_title('IRR')

        # Plot NPV
        ax_NPV.scatter(Time, Net_NPV, label='NPV Difference')
        ax_NPV.grid()
        ax_NPV.set_xlabel('Year')
        ax_NPV.set_ylabel('NPV Difference ($ in Millions)')
        ax_NPV.set_title('NPV Difference')
        ax_NPV.legend(loc="upper left")

        plt.show()