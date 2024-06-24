# MOSTCOOL

## Requirements/Tested on:

1. Ubuntu 22.04 with administrator access (Also works on Virtual Machines). If you are using Windows and need to install a Virtual Machine, please follow these instructions ([link](https://github.com/NREL/CoolerChips/blob/main/MOSTCOOL%20Windows%20Instructions.docx)).

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

  
| File Name            | Link                                                                                          | Place in this path in local directory                          |
|----------------------|-----------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| modes.csv            | [link](https://drive.google.com/file/d/19Ed_tRQhcz2zkdxL1GT-yD_eb6NXPUdn/view?usp=drive_link)    | EnergyPlusExample/ThermalModel_datacenter/modes.csv            |
| PythonPOD_Solid.cgns | [link](https://drive.google.com/file/d/19H1HXCjzYx6ymz6PY_3xEAhDZdyza7D0/view?usp=sharing) | EnergyPlusExample/ThermalModel_datacenter/PythonPOD_Solid.cgns |
  

5. Build the container:

`docker compose build`

6. Give docker permission to display it's GUI app on host. This step must be repeated each time the computer/virtual machine is restarted: `xhost +local:docker`

7. Run the container:

`docker compose up`

8. You should see the app pop up:

![image](CoolerChips/mostcool/assets/images/map.png)

## Sample results:

Simulation outputs:


![image](CoolerChips/mostcool/assets/images/simulation_outputs.png)


Results from Paraview:

![image](CoolerChips/mostcool/assets/images/paraview_results.png)

## Individual Model Documentation:

1. Thermal model documentation can be found in the repo root as [NEITcool DOCUMENTATION.pdf](https://github.com/NREL/CoolerChips/blob/gui/NEITcool%20DOCUMENTATION.pdf).

2. EnergyPlus documentation can be found [here](https://energyplus.net/documentation).

3. EnergyPlus Python API Documentation can be found [here](https://energyplus.readthedocs.io/en/latest/api.html).
