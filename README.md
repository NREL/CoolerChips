# mostcool

## Requirements/Tested on:

1. At least Quad Core CPU

  

2. At least 16 GB RAM

  

3. At least 10 GB storage space

  

  

## How to run:

Note: You may be able to skip some of these steps (Step 4, 5) but the app will not function correctly. 

  

1. Install docker in your computer:

  

https://docs.docker.com/engine/install/

  

  

2. Clone this repo by typing this in the terminal:

  

`git clone https://github.com/NREL/CoolerChips.git`

  

  

3. cd into the cloned directory.

4. Checkout the `web_app` branch : `git checkout web_app`
  

5. Download the files below (required dependencies) and place them in these paths:

  

  
  


| File Name            | Link                                                                                          | Place in this path in local directory                          |
|----------------------|-----------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| modes.csv            | [link](https://drive.google.com/file/d/19Ed_tRQhcz2zkdxL1GT-yD_eb6NXPUdn/view?usp=drive_link)    | mostcool/ThermalModel_datacenter/Modes.csv            |
| PythonPOD_Solid.cgns | [link](https://drive.google.com/file/d/19H1HXCjzYx6ymz6PY_3xEAhDZdyza7D0/view?usp=sharing) | mostcool/ThermalModel_datacenter/PythonPOD_Solid.cgns |

  

  

6. Build the container:

  

`docker compose build`



7. Run the container:

  

`docker compose up`

  

 8.  The terminal will tell you on which address the app is running:
  ![image](https://github.com/NREL/CoolerChips/assets/45446967/9485ce73-2f61-4de3-a249-673838180668)


 

10. Copy-paste the address in a browser window and the application should come up:
![image](https://github.com/NREL/CoolerChips/assets/45446967/903a037f-08f6-4b89-a93d-b10b88752531)
  

## Sample results:
Results from Paraview:
![image](https://github.com/NREL/CoolerChips/assets/45446967/01bdd7a6-07bd-499e-a3d2-85aeeaf80799)
  

Simulation outputs:
![image](https://github.com/NREL/CoolerChips/assets/45446967/e966443c-c551-48b0-8902-b78f1a3862e2)



## Individual Model Documentation:

1. Thermal model documentation can be found in the repo root as [NEITcool DOCUMENTATION.pdf](https://github.com/NREL/CoolerChips/blob/gui/NEITcool%20DOCUMENTATION.pdf).
2. EnergyPlus documentation can be found [here](https://energyplus.net/documentation). 
3. EnergyPlus Python API Documentation can be found [here](https://energyplus.readthedocs.io/en/latest/api.html). 
