# Implementation of semiconductor reliability calculations for failure rate and MTTF.
# Reference: https://www.renesas.com/us/en/document/qsg/calculation-semiconductor-failure-rates

import numpy as np
from scipy.stats import chi2

def calculate_acceleration_factor(E_a, T_use, T_stress):
    """
    Calculate the acceleration factor AF.

    Parameters:
    E_a (float): Thermal Activation Energy in eV.
    T_use (float): Use temperature in degrees Celsius.
    T_stress (float): Life test stress temperature in degrees Celsius.

    Returns:
    float: Acceleration factor AF.
    """
    k = 8.63e-5  # Boltzmann's constant in eV/K
    T_use_K = T_use + 273.15  # Convert use temperature to Kelvin
    T_stress_K = T_stress + 273.15  # Convert stress temperature to Kelvin

    AF = np.exp((E_a / k) * (1 / T_use_K - 1 / T_stress_K))
    return AF

def calculate_MTTF(T_use):
    """
    Calculate the failure rate λ and the Mean Time To Failure (MTTF).

    Parameters:
    x (list): Number of failures for each failure mechanism.
    num_units (list): Number of units in operation for each life test.
    time_operation (list): Time of operation for each life test.
    E_a (list): Thermal Activation Energy for each failure mechanism.
    T_use (float): Use temperature in degrees Celsius.
    T_stress (list): Stress temperatures for each life test.
    alpha (float): Risk associated with confidence level (CL).

    Returns:
    tuple: Failure rate λ in FITs and MTTF in hours.
    """
    #--------------------------------
    x = [1, 1]  # Number of failures for each failure mechanism
    num_units = [600, 599, 598]  # Number of units in operation for the life test
    time_operation = [1000, 1000, 1000]  # Time of operation for the life test in hours
    E_a = [0.7, 0.3]  # Thermal Activation Energy for each failure mechanism
    T_stress = [170, 170]  # Stress temperature in degrees Celsius (150°C ambient + 20°C rise)
    alpha = 0.05  # Risk associated with CL (0.05 for 95% confidence level)
    #--------------------------------

    # Calculate total number of failures
    r = sum(x)
    
    # Calculate chi-square factor for the given confidence level
    M = chi2.ppf(1 - alpha, 2 * r + 2) / 2
    print(f"[MTTF Calculation] Chi-square factor (M): {M:.6f}")

    # Corrected TDH calculation
    TDH = sum([num_unit * time_op for num_unit, time_op in zip(num_units, time_operation)])
    print(f"[MTTF Calculation] Total Device Hours (TDH): {TDH}")

    # Calculate AF for each failure mechanism and stress temperature
    AF = [calculate_acceleration_factor(E_a_i, T_use, T_stress_i) for E_a_i, T_stress_i in zip(E_a, T_stress)]
    print(f"[MTTF Calculation] Acceleration Factors (AF): {AF}")

    # Calculate the failure rate
    lambda_val = sum(x_i / (TDH * AF_i) for x_i, AF_i in zip(x, AF)) * (M * 1e9) / sum(x)
    lambda_val = round(lambda_val)  # Round to the nearest whole number
    print(f"[MTTF Calculation] Failure rate λ: {lambda_val} FITs")
    
    # Calculate MTTF
    MTTF = (1 / lambda_val) * 1e9

    return (f"Final Failure rate λ: {lambda_val} FITs"), (f"[MTTF Calculation] MTTF: {MTTF:.4e} hours @ {int((1-alpha)*100)}% CL")


"""
if __name__ == "__main__":
    x = [1]  # Number of failures for each failure mechanism
    num_units = [600]  # Number of units in operation for the life test
    time_operation = [1000]  # Time of operation for the life test in hours
    E_a = [0.4]  # Thermal Activation Energy for each failure mechanism
    T_use = 70  # Use temperature in degrees Celsius (55°C + 20°C internal rise)
    T_stress = [120, 120]  # Stress temperature in degrees Celsius (150°C ambient + 20°C rise)
    alpha = 0.05  # Risk associated with CL (0.05 for 95% confidence level)

    lambda_val, MTTF = calculate_MTTF(x, num_units, time_operation, E_a, T_use, T_stress, alpha)
    print(f"Final Failure rate λ: {lambda_val} FITs")
    print(f"Final MTTF: {MTTF:.2e} hours @ {int((1-alpha)*100)}% CL")
    """