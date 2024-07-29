# CostModelFileCalculationsV1_1.py
import matplotlib.pyplot as plt
import numpy as np
from CostModelFileProcessingV1_1 import table_lookup

Cooling_System_Details = {
    "chiller": {
        "Name": 'Chiller',
        "Cost_per_equipment": '',
        "Redundancy": '',
        "MTBF": '',
        "Cost_per_maintenance_event": '',
        "Total_cost_of_cooling_system": ''
    },
    "coolingTower": {
        "Name": 'Cooling Tower',
        "Cost_per_equipment": '',
        "Redundancy": '',
        "MTBF": '',
        "Cost_per_maintenance_event": '',
        "Total_cost_of_cooling_system": ''
    },
    "pump": {
        "Name": 'Pump',
        "Cost_per_equipment": '',
        "Redundancy": '',
        "MTBF": '',
        "Cost_per_maintenance_event": '',
        "Total_cost_of_cooling_system": ''
    },
    "fluid": {
        "Name": 'Fluid',
        "Cost_per_equipment": '',
        "Redundancy": '',
        "MTBF": '',
        "Cost_per_maintenance_event": '',
        "Total_cost_of_cooling_system": ''
    },
    "ducting": {
        "Name": 'Ducting',
        "Cost_per_equipment": '',
        "Redundancy": '',
        "MTBF": '',
        "Cost_per_maintenance_event": '',
        "Total_cost_of_cooling_system": ''
    },
    "piping": {
        "Name": 'Piping',
        "Cost_per_equipment": '',
        "Redundancy": '',
        "MTBF": '',
        "Cost_per_maintenance_event": '',
        "Total_cost_of_cooling_system": ''
    },
    "CRAH": {
        "Name": 'Computer Room Air Handler',
        "Cost_per_equipment": '',
        "Redundancy": '',
        "MTBF": '',
        "Cost_per_maintenance_event": '',
        "Total_cost_of_cooling_system": ''
    },
    "air_Economizer": {
        "Name": 'Air Economizier',
        "Cost_per_equipment": '',
        "Redundancy": '',
        "MTBF": '',
        "Cost_per_maintenance_event": '',
        "Total_cost_of_cooling_system": ''
    }
}

variables = {
    "Duration of Simulation (seconds)": "631152000",
    "Electricity Cost ($/Wh)": "0.000145",
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
    elif redundancy == "2N":
        return 2
    elif redundancy == "N+1":
        return 2  
    elif redundancy == "2N+1":
        return 3
    else:
        return 1  # Default to 1 if redundancy is not recognized

def update_cooling_system_details():
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

update_cooling_system_details()

def get_cooling_system_details():
    details = [["Name", "Cost_per_equipment", "Redundancy", "MTBF", "Cost_per_maintenance_event", "Total_cost_of_cooling_system"]]
    for component, data in Cooling_System_Details.items():
        details.append([
            data['Name'],
            data.get('Cost_per_equipment', ''),
            data.get('Redundancy', ''),
            data.get('MTBF', ''),
            data.get('Cost_per_maintenance_event', ''),
            data.get('Total_cost_of_cooling_system', '')
        ])
    return details


# Example function that might use the updated Cooling_System_Details
def calculate_total_cooling_cost():
    total_cost = 0
    for component in Cooling_System_Details.values():
        if component["Cost_per_equipment"]:
            total_cost += float(component["Cost_per_equipment"])
    return total_cost

def calculate_irr():
    # Update variables from the settings window (if applicable)
    # self.update_variables_from_settings()

    # Inputs
    SimulationDuration = float(variables["Duration of Simulation (seconds)"]) / (60 * 60 * 24 * 365)  # convert to years
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
    B_MTBF = 18000000  # self.MTBF1
    CoolingMaintenanceCost = 250000  # self.CostPerMaintenanceEvent1
    B_IT_MTBF = float(variables["IT MTBF for the Analysis Cooling System (seconds)"]) / (60 * 60)  # convert to hours
    B_EnergyUsage = 250  # million kWh
    B_AvoidedITFailures = 0
    B_AnnualRecoveredHeat = 1200  # million kWh

    # New Inputs
    N_CapitolCost = B_CapitolCost * 1.1  # assume 10% more for new system
    N_Life = 12  # 12
    N_MTBF = 6000  # self.MTBF2
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

    # Time step adjustment for inflation and discount rates

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
    ax_IRR.plot([0, 20], [0.1, 0.1], 'r-')
    ax_IRR.grid()
    ax_IRR.set_xlabel('Year')
    ax_IRR.set_ylabel('IRR')
    ax_IRR.set_title('IRR')
    
    # Plot NPV
    ax_NPV.scatter(N_Time, Net_NPV, label='NPV Difference')
    ax_NPV.grid()
    ax_NPV.set_xlabel('Year')
    ax_NPV.set_ylabel('NPV Difference ($ in Millions)')
    ax_NPV.setTitle('NPV Difference')
    ax_NPV.legend(loc="upper left")
    
    # Finding the breakeven year
    BreakevenYear = None
    for i in range(1, int(SimulationDuration)):
        if IRR[i] > 0:
            BreakevenYear = i
            break

    if BreakevenYear is not None:
        print('The first breakeven year is at', BreakevenYear)
    else:
        print('No breakeven year found within the simulation duration.')

    # Show plots
    plt.show()
