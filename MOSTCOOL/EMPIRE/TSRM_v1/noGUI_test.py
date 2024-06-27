import argparse
from src.communication.tsrm_api import TSRMApi

def main(json_file_path):
    # Create an instance of the TSRMApi class
    api = TSRMApi()
    
    # Run the simulation with the provided JSON file path
    result = api.gen_and_run_sim(user_file_path=json_file_path)
    
    # Print the result
    if result:
        print(f"Simulation completed successfully. Reliability calculations output path: {result}")
    else:
        print("Simulation failed.")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run thermal stack reliability simulation using a JSON file.')
    parser.add_argument('json_file_path', type=str, help='Path to the JSON file')
    
    args = parser.parse_args()
    
    # Run the main function with the provided JSON file path
    main(args.json_file_path)
