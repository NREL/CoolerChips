import numpy as np
import matplotlib.pyplot as plt
from scipy.special import gamma
from CostModelFileProcessingV1_1 import table_lookup  # Ensure this import is correct

variables = {
    "Duration of Simulation (seconds)": "631152000",
    "Duration of Simulation (years)": "20",  # Added this line for years duration
    "Electricity Cost ($/kWh)": "0.000145",
    "Energy Inflation (per year)": "0.0224",
    "Inflation (per year)": "0.035",
    "Discount Rate (per year)": "0.06",
    "IT Maintenance Cost (per event)": "250000",
    "Cost of Cooling Fluid ($/gallon)": "0.01065",
    "Data Center Capacity (W)": "1000000",
    "CEPCI Number": "8.008",
    "IT MTBF for the Reference Cooling System (seconds)": "18000000",
    "IT MTBF for the Analysis Cooling System (seconds)": "6000",
    "Recovered Heat (fraction of energy cost)": "31600000",
    "Piping Size (Diameter meters)": "0.1016",
    "Duct Size (sq m.)": "0.3741612"
}

Cooling_System_Details = {
    "chiller": {
        "Name": 'Chiller',
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_type": 'Cost per maintenance',
        "Total_cost_of_cooling_system": 0.0
    },
    "coolingTower": {
        "Name": 'Cooling Tower',
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_type": 'Cost per maintenance',
        "Total_cost_of_cooling_system": 0.0
    },
    "pump": {
        "Name": 'Pump',
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_type": 'Cost per maintenance',
        "Total_cost_of_cooling_system": 0.0
    },
    "fluid": {
        "Name": 'Fluid',
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_type": 'Cost per maintenance',
        "Total_cost_of_cooling_system": 0.0
    },
    "ducting": {
        "Name": 'Ducting',
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_type": 'Cost per maintenance',
        "Total_cost_of_cooling_system": 0.0
    },
    "piping": {
        "Name": 'Piping',
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_type": 'Cost per maintenance',
        "Total_cost_of_cooling_system": 0.0
    },
    "CRAH": {
        "Name": 'Computer Room Air Handler',
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_type": 'Cost per maintenance',
        "Total_cost_of_cooling_system": 0.0
    },
    "air_Economizer": {
        "Name": 'Air Economizer',
        "Cost_per_equipment": 0.0,
        "Redundancy": 'N',
        "MTBF": '',
        "Gamma": '',
        "Beta": '',
        "Eta": '',
        "Cost_per_maintenance_event": '',
        "Maintenance_type": 'Cost per maintenance',
        "Total_cost_of_cooling_system": 0.0
    }
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
                                
    return cooling_tower_cost

def pump_calculator(power_consumption_value, CEPCI_Number):
    if isinstance(power_consumption_value, int):
        power_consumption_value = str(power_consumption_value)
            
    pump_cost = ((9500 * float(power_consumption_value) / (23 * 1000)) ** 0.79) * CEPCI_Number
    
    return pump_cost

def duct_calculator(volume_value, estimate_duct_size, CEPCI_Number):
    if isinstance(volume_value, int):
        volume_value = str(volume_value)
    duct_cost = (700 / estimate_duct_size) * float(volume_value) * CEPCI_Number
    
    return duct_cost

def pipe_calculator(volume_value, estimate_pipe_size, CEPCI_Number):
    if isinstance(volume_value, int):
        volume_value = str(volume_value)
    
    piping_cost = (80 / estimate_pipe_size) * float(volume_value) * CEPCI_Number
    
    return piping_cost

def CRAH_calculator(data_center_capacity):
    crah_cost = data_center_capacity * 240
    
    return crah_cost

def air_economizer_calculator(data_center_capacity):
    air_economizer_cost = data_center_capacity * 132.4
    
    return air_economizer_cost

def fluid_calculator(volume_value):
    total_volume_gallons = float(volume_value) * 264.172
    fluid_cost = (total_volume_gallons * (1.1 * 12)) / 10000 * 10.65
    
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

def update_cooling_system_details(mtbf, gamma, beta, eta, cost_per_maintenance_event):
    if table_lookup["chiller"]["value"]:
        Cooling_System_Details["chiller"]["Cost_per_equipment"] = chiller_calculator(table_lookup["chiller"]["value"])
    if table_lookup["coolingTower"]["value"]:
        Cooling_System_Details["coolingTower"]["Cost_per_equipment"] = cooling_tower_calculator(table_lookup["coolingTower"]["value"])
    if table_lookup["pump_power"]["value"]:
        Cooling_System_Details["pump"]["Cost_per_equipment"] = pump_calculator(table_lookup["pump_power"]["value"], float(variables["CEPCI Number"]))
    if table_lookup["airloopHVAC"]["value"]:
        Cooling_System_Details["ducting"]["Cost_per_equipment"] = duct_calculator(table_lookup["airloopHVAC"]["value"], float(variables["Duct Size (sq m.)"]), float(variables["CEPCI Number"]))
    if table_lookup["plantLoop"]["value"]:
        Cooling_System_Details["piping"]["Cost_per_equipment"] = pipe_calculator(table_lookup["plantLoop"]["value"], float(variables["Piping Size (Diameter meters)"]), float(variables["CEPCI Number"]))
        Cooling_System_Details["fluid"]["Cost_per_equipment"] = fluid_calculator(table_lookup["plantLoop"]["value"])
    Cooling_System_Details["CRAH"]["Cost_per_equipment"] = CRAH_calculator(float(variables["Data Center Capacity (W)"]))
    Cooling_System_Details["air_Economizer"]["Cost_per_equipment"] = air_economizer_calculator(float(variables["Data Center Capacity (W)"]))

    for component in Cooling_System_Details.values():
        component["MTBF"] = mtbf
        component["Gamma"] = gamma
        component["Beta"] = beta
        component["Eta"] = eta
        component["Cost_per_maintenance_event"] = cost_per_maintenance_event
        if component["Cost_per_equipment"] == '':
            component["Cost_per_equipment"] = 0.0
        component["Total_cost_of_cooling_system"] = float(component["Cost_per_equipment"]) * get_redundancy_multiplier(component["Redundancy"])

def get_cooling_system_details():
    details = [["Name", "Units", "Cost per Equipment", "Redundancy", "MTBF", "Gamma (hours)", "Beta", "Eta (hours)", "Cost per Maintenance Event", "Maintenance Type", "Total Cost"]]
    for component, data in Cooling_System_Details.items():
        details.append([
            data['Name'],
            'per_datacenter',  # Default units
            format_currency(data.get('Cost_per_equipment', 0.0)),
            data.get('Redundancy', 'N'),
            data.get('MTBF', ''),
            format_currency(data.get('Gamma', 0.0)),
            data.get('Beta', ''),
            format_currency(data.get('Eta', 0.0)),
            format_currency(data.get('Cost_per_maintenance_event', 0.0)),
            data.get('Maintenance_type', 'Cost per maintenance'),
            format_currency(data.get('Total_cost_of_cooling_system', 0.0))
        ])
    return details

def calculate_total_cooling_cost():
    total_cost = sum(
        float(component["Total_cost_of_cooling_system"].replace(',', '').replace('$', '')) 
        if isinstance(component["Total_cost_of_cooling_system"], str) 
        else float(component["Total_cost_of_cooling_system"])
        for component in Cooling_System_Details.values() 
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
        return gamma(x)

class CostModelCalculations:
    def __init__(self, variables, cooling_system_details):
        self.variables = variables
        self.cooling_system_details = cooling_system_details
        self.MTBF1 = None
        self.CostPerMaintenanceEvent1 = None
        self.MTBF2 = None
        self.CostPerMaintenanceEvent2 = None
        self.canvas_ROI = None
        self.canvas_IRR = None
        self.canvas_NPV = None

    def calculate_irr(self):
        # Update variables from the settings window
        self.update_variables_from_settings()

        # Inputs that will need to later be read as an input somehow
        SimulationDuration = float(self.variables["Duration of Simulation (years)"])
        TimeStepMultiplier = 1  # 12 for every month/4 for every quarter/1 for every year

        # Default Inputs
        ElectricityCost = float(self.variables["Electricity Cost ($/kWh)"])
        EnergyInflation = float(self.variables["Energy Inflation (per year)"])
        Inflation = float(self.variables["Inflation (per year)"])
        DiscountRate = float(self.variables["Discount Rate (per year)"])
        ITMaintenanceCost = float(self.variables["IT Maintenance Cost (per event)"])
        RecoveredHeatValue = float(self.variables["Recovered Heat (fraction of energy cost)"])

        # Calculations to adjust time step
        SimulationDuration = SimulationDuration * TimeStepMultiplier

        # Inputs for Baseline
        B_CapitolCost = float(self.cooling_system_details[1][2].replace('$', '').replace(',', '')) / 1000000  # million dollars
        B_Life = 9  # 9
        B_MTBF = self.MTBF1
        CoolingMaintenanceCost = self.CostPerMaintenanceEvent1
        B_IT_MTBF = float(self.variables["IT MTBF for the Analysis Cooling System (seconds)"])
        B_EnergyUsage = 250  # million kWh get from E+ excel file
        B_AvoidedITFailures = 0
        B_AnnualRecoveredHeat = 1200  # million kWh Needs to calculated from E+ data

        # Inputs for New
        N_CapitolCost = float(self.cooling_system_details[1][2].replace('$', '').replace(',', '')) / 1000000  # million dollars
        N_Life = 12  # 12
        N_MTBF = self.MTBF2
        CoolingMaintenanceCost2 = self.CostPerMaintenanceEvent2
        N_IT_MTBF = float(self.variables["IT MTBF for the Analysis Cooling System (seconds)"])
        N_EnergyUsage = 262.8  # million kWh
        N_AvoidedITFailures = .5
        N_AnnualRecoveredHeat = 1314  # million kWh Needs to calculated from E+ data

        print(N_CapitolCost)
        print(B_CapitolCost)

        # Individual Expenses and Revenue Calculations for baseline
        B_Time, B_Capitol, B_EnergyCost, B_CoolingMaintenance, B_ITMaintenance, B_HeatRevenue, B_Net, B_NPV = self._calculate_individual_expenses_and_revenues(
            SimulationDuration, B_CapitolCost, B_Life, B_EnergyUsage, ElectricityCost, EnergyInflation, B_MTBF,
            CoolingMaintenanceCost, Inflation, B_IT_MTBF, ITMaintenanceCost, B_AvoidedITFailures, B_AnnualRecoveredHeat,
            RecoveredHeatValue, DiscountRate)

        B_CumNPV = np.cumsum(B_NPV)
        IO = B_CapitolCost

        # Individual Expenses and Revenue Calculations for New
        N_Time, N_Capitol, N_EnergyCost, N_CoolingMaintenance, N_ITMaintenance, N_HeatRevenue, N_Net, N_NPV = self._calculate_individual_expenses_and_revenues(
            SimulationDuration, N_CapitolCost, N_Life, N_EnergyUsage, ElectricityCost, EnergyInflation, N_MTBF,
            CoolingMaintenanceCost2, Inflation, N_IT_MTBF, ITMaintenanceCost, N_AvoidedITFailures, N_AnnualRecoveredHeat,
            RecoveredHeatValue, DiscountRate)

        N_CumNPV = np.cumsum(N_NPV)
        Inew = N_CapitolCost

        # ROI and IRR Calculations
        ROI, IRR, Net_NPV, BreakevenYear = self._calculate_roi_irr(SimulationDuration, B_CumNPV, N_CumNPV, Inew, IO, N_NPV, B_NPV)

        # Plot results
        self.plot_results(N_Time, ROI, IRR, Net_NPV)

        print("IRR:", IRR)
        print("ROI:", ROI)
        print("B_cumNPV:", B_CumNPV)
        print("N_cumNPV:", N_CumNPV)
        print("Net_NPV:", Net_NPV)

        # Finding the breakeven year
        if BreakevenYear is not None:
            print('The first breakeven year is at', BreakevenYear)
        else:
            print('No breakeven year found within the simulation duration.')

    def _calculate_individual_expenses_and_revenues(self, SimulationDuration, CapitolCost, Life, EnergyUsage, ElectricityCost,
                                                    EnergyInflation, MTBF, CoolingMaintenanceCost, Inflation, IT_MTBF,
                                                    ITMaintenanceCost, AvoidedITFailures, AnnualRecoveredHeat, RecoveredHeatValue,
                                                    DiscountRate):
        Time = []
        Capitol = []
        EnergyCost = []
        CoolingMaintenance = []
        ITMaintenance = []
        HeatRevenue = []
        Net = []
        NPV = []

        i = 0
        while i <= SimulationDuration:
            Time.append(i)

            # Capitol Costs
            if i % Life == 0:
                Capitol.append(CapitolCost * (1 + Inflation) ** i)
            else:
                Capitol.append(0)

            # Energy Costs
            if i > 0:
                EnergyCost.append(ElectricityCost * EnergyUsage * (1 + EnergyInflation) ** (i - 1))
            else:
                EnergyCost.append(0)

            # Cooling Maintenance
            if i > 0:
                CoolingMaintenance.append(((MTBF / 8760) * CoolingMaintenanceCost * (1 + Inflation) ** i) / 1000000)
            else:
                CoolingMaintenance.append(0)

            # IT Maintenance
            if i > 0:
                ITMaintenance.append((-AvoidedITFailures * ITMaintenanceCost * (1 + Inflation) ** i) / 1000000)
            else:
                ITMaintenance.append(0)

            # Heat Revenue
            if i > 0:
                HeatRevenue.append(-AnnualRecoveredHeat * RecoveredHeatValue * ElectricityCost * (1 + EnergyInflation) ** (i - 1))
            else:
                HeatRevenue.append(0)

            # Net
            Net.append(Capitol[i] + EnergyCost[i] + CoolingMaintenance[i] + ITMaintenance[i] + HeatRevenue[i])

            # NPV
            NPV.append(Capitol[i] / (1 + DiscountRate) ** i + EnergyCost[i] / (1 + DiscountRate) ** i + CoolingMaintenance[i] / (1 + DiscountRate) ** i + ITMaintenance[i] / (1 + DiscountRate) ** i + HeatRevenue[i] / (1 + DiscountRate) ** i)

            i = i + 1

        return Time, Capitol, EnergyCost, CoolingMaintenance, ITMaintenance, HeatRevenue, Net, NPV

    def _calculate_roi_irr(SimulationDuration, B_CumNPV, N_CumNPV, Inew, IO, N_NPV, B_NPV):
        ROI = []
        IRR = []
        Net_NPV = []
        BreakevenYear = None

        i = 0
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

            if BreakevenYear is None and IRR[i] > 0:
                BreakevenYear = i

            i = i + 1

        return ROI, IRR, Net_NPV, BreakevenYear

    def plot_results(self, N_Time, ROI, IRR, Net_NPV):
        # Create Matplotlib figures and axes for both ROI and IRR plots
        fig_ROI, ax_ROI = plt.subplots(figsize=(7, 5))  # Set a fixed figsize for ROI plot
        fig_IRR, ax_IRR = plt.subplots(figsize=(7, 5))  # Set a fixed figsize for IRR plot
        fig_NPV, ax_NPV = plt.subplots(figsize=(7, 5))  # Set a fixed figsize for NPV plot

        # Plot ROI
        ax_ROI.scatter(N_Time, ROI)
        ax_ROI.grid()
        ax_ROI.set_xlabel('Year')
        ax_ROI.set_ylabel('ROI')
        ax_ROI.set_title('ROI')

        # Plot IRR
        ax_IRR.scatter(N_Time, IRR)
        ax_IRR.plot([0, 20], [.1, .1], 'r-')
        ax_IRR.grid()
        ax_IRR.set_xlabel('Year')
        ax_IRR.set_ylabel('IRR')
        ax_IRR.set_title('IRR')

        # Plot NPV
        ax_NPV.scatter(N_Time, Net_NPV, label='NPV Difference')
        ax_NPV.grid()
        ax_NPV.set_xlabel('Year')
        ax_NPV.set_ylabel('NPV Difference ($ in Millions)')
        ax_NPV.set_title('NPV Difference')
        ax_NPV.legend(loc="upper left")

        plt.show()

    def update_variables_from_settings(self):
        # This function should be implemented to update variables from the settings window
        pass
