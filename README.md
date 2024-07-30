# MOSTCOOL

## Requirements/Tested on:

1. At least Quad Core CPU

  

2. At least 16 GB RAM

  

3. At least 10 GB storage space

  

  

## How to run:

  

  

1. Install docker in your computer:

https://docs.docker.com/engine/install/

2. Pull our latest stable image:

`docker pull ghcr.io/nrel/mostcool:v1.1.0`

3. Give docker permission to display it's GUI app on host. This step must be repeated each time the computer/virtual machine is restarted: 
`xhost +local:docker`

4. Run the container:

`docker run --network host --env="DISPLAY=${DISPLAY}" --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" mostcool`

5. You should see the app pop up:

![image](mostcool/assets/images/map.png)

## Sample results:
Results from Paraview:
![image](https://github.com/NREL/CoolerChips/assets/45446967/01bdd7a6-07bd-499e-a3d2-85aeeaf80799)
  

Simulation outputs:
![image](https://github.com/NREL/CoolerChips/assets/45446967/e966443c-c551-48b0-8902-b78f1a3862e2)



## Individual Model Documentation:

1. Thermal model documentation can be found in the repo root as [NEITcool DOCUMENTATION.pdf](https://github.com/NREL/CoolerChips/blob/gui/NEITcool%20DOCUMENTATION.pdf).

2. EnergyPlus documentation can be found [here](https://energyplus.net/documentation).

3. EnergyPlus Python API Documentation can be found [here](https://energyplus.readthedocs.io/en/latest/api.html).
