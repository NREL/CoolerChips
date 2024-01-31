import subprocess

# Add commands that should be run to this list
commands = [
    ["helics", "run", "--path=runner.json"],
    ["python", "cost_model.py"],
    # Add more as needed
]

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    for line in iter(process.stdout.readline, ''):
        print(line, end='')

    process.wait()
    print(f"Command '{' '.join(command)}' finished with exit code {process.returncode}")


for cmd in commands:
    print(f"Running command: {' '.join(cmd)}")
    run_command(cmd)
    print("-" * 50)  # Separator between command outputs
