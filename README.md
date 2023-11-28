
## This is an EnergyPlus HELICS federate example. 

How to use this:

1. Clone this repo:
    `git clone   https://github.com/jmythms/CoolerChips`
2. cd into the cloned directory. 
3. Download and install EnergyPlus:
   
	a. Set the download link obtained from the EnergyPlus GitHub Releases page
`EPLUS_DOWNLOAD_LINK="https://github.com/NREL/EnergyPlus/releases/download/v9.6.0/EnergyPlus-9.6.0-f420c06a69-Linux-Ubuntu20.04-x86_64.sh"`

	 b. Use wget to download the installer
    `wget -O  ./EnergyPlus-9.6.0-f420c06a69-Linux-Ubuntu20.04-x86_64.sh  "$EPLUS_DOWNLOAD_LINK"`
   
    c. Make the installer executable
`chmod +x  "./EnergyPlus-9.6.0-f420c06a69-Linux-Ubuntu20.04-x86_64.sh"`

	d. Install EnergyPlus:
	`./EnergyPlus-9.6.0-f420c06a69-Linux-Ubuntu20.04-x86_64.sh`

      Note: When asked for the install location, please install it in this path:
			`./EnergyPlusExample/EnergyPlus`. 
			If you don't want to do that change the EnergyPlus install path in the [EnergyPlus.py file](https://github.com/jmythms/CoolerChips/blob/e55cdea21185bcb2fc671aab6883febd1f7b6f7b/EnergyPlusExample/EnergyPlus.py#L10) so everything works properly. 

5. Install pyHELICS:
	`pip install helics`

6. Run our example:
	`helics run --path=./EnergyPlusExample/runner.json`
		
