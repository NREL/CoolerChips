# Use the nvidia/opengl image as base image (For paraview/trame dependencies)
FROM --platform=linux/x86_64 nvidia/opengl:1.2-glvnd-runtime-ubuntu22.04 

ARG DEBIAN_FRONTEND=noninteractive

ENV ENERGYPLUS_LINK=https://github.com/NREL/EnergyPlus/releases/download/v23.2.0/EnergyPlus-23.2.0-7636e6b3e9-Linux-Ubuntu22.04-x86_64.tar.gz

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget=1.21.* \
    unzip=6.0-* \
    python3=3.10.* \
    python3-pip=22.0.* \
    python-is-python3

# Install system dependencies
RUN  apt-get update && apt-get install -y \
    python3-tk=3.10.* 

# Download and install EnergyPlus    
RUN wget --no-check-certificate  $ENERGYPLUS_LINK \
    && tar -xzf EnergyPlus-23.2.0-7636e6b3e9-Linux-Ubuntu22.04-x86_64.tar.gz \
    && mv EnergyPlus-23.2.0-7636e6b3e9-Linux-Ubuntu22.04-x86_64 EnergyPlus

# Download and install Paraview
RUN wget --no-check-certificate  -O ParaView-5.12.0-egl-MPI-Linux-Python3.10-x86_64.tar.gz "https://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v5.12&type=binary&os=Linux&downloadFile=ParaView-5.12.0-egl-MPI-Linux-Python3.10-x86_64.tar.gz" \
    && tar -xzf ParaView-5.12.0-egl-MPI-Linux-Python3.10-x86_64.tar.gz \
    && mv ParaView-5.12.0-egl-MPI-Linux-Python3.10-x86_64 Paraview

# Copy requirements.txt to the docker image
COPY requirements.txt /app/requirements.txt

# Install Python dependencies from requirements.txt file
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN apt update -y && apt install -y libosmesa6-dev

# Install Paraview/Trame dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        pkg-config \
        libglvnd-dev \
        libgl1-mesa-dev \
        libegl1-mesa-dev \
        libgles2-mesa-dev && \
    rm -rf /var/lib/apt/lists/*

# Create symbolic link for EnergyPlus
RUN ln -s /EnergyPlus/energyplus /usr/local/bin/energyplus

# Paraview env variable
ARG TRAME_DEFAULT_HOST=127.0.0.1

# Set working directory
WORKDIR /app

CMD ["python", "app.py"]
