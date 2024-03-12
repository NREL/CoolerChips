

## This is an EnergyPlus HELICS federate example. 

How to use this:

1. Install docker in your computer:
	https://docs.docker.com/engine/install/

2. Clone this repo:
    `git clone https://github.com/NREL/CoolerChips.git`
3. cd into the cloned directory. 
4. Build the container:
`docker compose build`
5. Run the container:
	`docker compose up`
6. You should see the output image as a file called `Output/graphs/OutputImage.pdf`.



Depending on the control option in definitions.py:
if Control option == change liquid cooling:
![image](https://github.com/NREL/CoolerChips/assets/45446967/51cb4741-77c7-4b44-ba46-238114e23ba6)

else if CONTROL_OPTION == CHANGE_SUPPLY_DELTA_T:
![image](https://github.com/NREL/CoolerChips/assets/45446967/6a2a26ef-902d-44ef-9cec-1e6e5dbd17b7)

else if CONTROL_OPTION == CHANGE_IT_LOAD:
![image](https://github.com/NREL/CoolerChips/assets/45446967/78848b59-fd57-4fd7-88f7-f7bf41a166fe)



