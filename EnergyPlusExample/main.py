import subprocess

# Add commands that should be run to this list
commands = [
    ["helics", "run", "--path=runner.json"],
    ["python", "cost_model.py"],
    # Add more as needed
]

for command in commands:
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"Command {command} executed successfully. Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing {command}: {e.stderr}")
        break  # or continue, depending on whether you want to stop on error or not
