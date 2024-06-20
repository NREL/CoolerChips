import os
import matlab.engine
from src.utils.simData_util import SimData

class ParaPowerPythonApi:
    def __init__(self):
        self.simdata = SimData()
        self.matlab_engine = None

    def run_matlab_sim(self, input_file_path):
        """
        Runs the ParaPower simulation using the MATLAB engine and returns the output
        file path. Adds necessary directories to the MATLAB path, changes the MATLAB
        current folder, and runs the simulation.

        Args:
            input_file_path (string): Path of the input JSON file for the simulation

        Returns:
            string: Path of the output results JSON file 
        """
        # Generate output file path
        output_file_path = self.simdata.create_output_path("TSRM_v1", "therm_mech_results", "ParaPowerResults")
        try:
            # Start MATLAB engine
            self.matlab_engine = matlab.engine.start_matlab()

            # Find the software directory path
            base_dir = os.path.join(self.simdata.find_base_dir('TSRM_v1'), "src")
            api_dir = os.path.join(base_dir, "communication")
            software_dir = os.path.join(base_dir, "therm_mech", "parapower_software")

            # Add the necessary directories to the MATLAB path
            self.matlab_engine.addpath(api_dir, nargout=0)
            self.matlab_engine.addpath(software_dir, nargout=0)
            
            # Change the MATLAB current folder to the ParaPower Software directory
            self.matlab_engine.cd(software_dir, nargout=0)
            
            # Run the MATLAB function
            self.matlab_engine.parapower_matlab_api(input_file_path, output_file_path, nargout=0)

            # Ensure the MATLAB engine is properly closed
            self.matlab_engine.quit()
            self.matlab_engine = None
        except:
            print("Simulation was stopped.")
        return output_file_path

def main():
    parapower = ParaPowerPythonApi()
    input_file_path = os.path.join(parapower.simdata.find_base_dir('TSRM_v1'), "libs", "thermal-stack-config", "AirCooled_NVIDIA_H100_GPU.json")
    parapower.run_matlab_sim(input_file_path)

if __name__ == "__main__":
    main()