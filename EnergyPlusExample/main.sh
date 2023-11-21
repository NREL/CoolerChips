#!/bin/bash

# Set the EnergyPlus version
EPLUS_VERSION="9-6-0"  # Replace this with the actual version you want to download

# Set the download link obtained from the EnergyPlus GitHub Releases page
EPLUS_DOWNLOAD_LINK="https://github.com/NREL/EnergyPlus/releases/download/v9.6.0/EnergyPlus-9.6.0-f420c06a69-Linux-Ubuntu20.04-x86_64.sh"

# Use wget to download the installer
wget "$EPLUS_DOWNLOAD_LINK"

# # Make the installer executable
chmod +x "/workspaces/CoolerChips/EnergyPlus-9.6.0-f420c06a69-Linux-Ubuntu20.04-x86_64.sh"

echo y | sudo /workspaces/CoolerChips/EnergyPlus-9.6.0-f420c06a69-Linux-Ubuntu20.04-x86_64.sh

pip install helics

helics run --path=/workspaces/CoolerChips/EnergyPlusExample/runner.json