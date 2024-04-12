



# MOSTCOOL

## Requirements/Tested on:
1. Ubuntu 22.04 with administrator access (Also works on Virtual Machines).
2. At least Quad Core CPU
3. At least 16 GB RAM
4. At least 4 GB hard disk space


## How to run:

1. Install docker in your computer:
	https://docs.docker.com/engine/install/

2. Clone this repo:
    `git clone https://github.com/NREL/CoolerChips.git`

  
3. cd into the cloned directory.
4. Download required dependencies and place them in these paths:

| File Name            | Link | Place in this path in local directory                          |
|----------------------|------|----------------------------------------------------------------|
| Modes.csv            | link | EnergyPlusExample/ThermalModel_datacenter/Modes.csv            |
| PythonPOD_Solid.cgns | link | EnergyPlusExample/ThermalModel_datacenter/PythonPOD_Solid.cgns |

5. Build the container:
`docker compose build`
6. Run the container:
	`docker compose up`
7. Give docker permission to display it's GUI app on host: `xhost +local:docker`

8. You should see the app pop up:
![image](https://github.com/NREL/CoolerChips/assets/45446967/39e9495c-0458-42ae-86ea-47ae77e3990c)

## Sample results:

Simulation outputs:
![image](https://github.com/NREL/CoolerChips/assets/45446967/9dc5e93b-0303-4de4-87fd-588b7e70efc9)




Results from Paraview:
![image](https://github.com/NREL/CoolerChips/assets/45446967/f607abac-d3b3-4069-8778-86b1e5648a14)




