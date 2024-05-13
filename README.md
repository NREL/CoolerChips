

  

  

# MOSTCOOL

  

## Requirements/Tested on:

  

1. Install Docker 
  

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

  
  
 

6. Run the container:

  

`docker compose up`

  

  

7. Wait for the run to complete:

  

![image](https://github.com/NREL/CoolerChips/assets/45446967/9189f34e-5b97-486d-8387-c5049401e23b)


  
8. You can see the plots in the ./Plots/ directory:
  

## Sample results:

  

  

Simulation outputs:

  

![image](https://github.com/NREL/CoolerChips/assets/45446967/9dc5e93b-0303-4de4-87fd-588b7e70efc9)

  

  

Results from Paraview:

  

![image](https://github.com/NREL/CoolerChips/assets/45446967/f607abac-d3b3-4069-8778-86b1e5648a14)


## Individual Model Documentation:

1. Thermal model documentation can be found in the repo root as [NEITcool DOCUMENTATION.pdf](https://github.com/NREL/CoolerChips/blob/gui/NEITcool%20DOCUMENTATION.pdf).
2. EnergyPlus documentation can be found [here](https://energyplus.net/documentation). 
3. EnergyPlus Python API Documentation can be found [here](https://energyplus.readthedocs.io/en/latest/api.html). 
