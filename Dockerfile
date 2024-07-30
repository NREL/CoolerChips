# Use the nvidia/opengl image as base image (For paraview/trame dependencies)
FROM --platform=linux/x86_64 nvidia/opengl:1.2-glvnd-runtime-ubuntu22.04 

ARG DEBIAN_FRONTEND=noninteractive

ARG RUN_TESTS=false

ENV ENERGYPLUS_LINK=https://github.com/NREL/EnergyPlus/releases/download/v23.2.0/EnergyPlus-23.2.0-7636e6b3e9-Linux-Ubuntu22.04-x86_64.tar.gz

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget=1.21.* \
    unzip=6.0-* \
    git \
    python3=3.10.* \
    python3-pip=22.0.* \
    python3-tk=3.10.* \
    python-is-python3 && \
    apt-get clean

# Download and install EnergyPlus    
RUN wget $ENERGYPLUS_LINK \
    && tar -xzf EnergyPlus-23.2.0-7636e6b3e9-Linux-Ubuntu22.04-x86_64.tar.gz \
    && mv EnergyPlus-23.2.0-7636e6b3e9-Linux-Ubuntu22.04-x86_64 EnergyPlus

# Download and install Paraview
RUN wget -O ParaView-5.12.0-egl-MPI-Linux-Python3.10-x86_64.tar.gz "https://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v5.12&type=binary&os=Linux&downloadFile=ParaView-5.12.0-egl-MPI-Linux-Python3.10-x86_64.tar.gz" \
    && tar -xzf ParaView-5.12.0-egl-MPI-Linux-Python3.10-x86_64.tar.gz \
    && mv ParaView-5.12.0-egl-MPI-Linux-Python3.10-x86_64 Paraview

# Clone the repository
RUN git clone --branch main https://github.com/NREL/CoolerChips.git /app

# Install gdown
RUN pip install gdown

# Download files using gdown
RUN gdown "https://drive.google.com/uc?id=19Ed_tRQhcz2zkdxL1GT-yD_eb6NXPUdn" -O "/app/mostcool/thermal/data/modes.csv" && \
    gdown "https://drive.google.com/uc?id=19H1HXCjzYx6ymz6PY_3xEAhDZdyza7D0" -O "/app/mostcool/thermal/data/PythonPOD_Solid.cgns"

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

# Install the mostcool package conditionally
RUN if [ "${RUN_TESTS}" = "true" ]; then pip install /app/[test]; else pip install /app/; fi

# Create symbolic link for EnergyPlus
RUN ln -s /EnergyPlus/energyplus /usr/local/bin/energyplus

# Paraview env variable
ARG TRAME_DEFAULT_HOST=127.0.0.1

# Set working directory
WORKDIR /app/mostcool

CMD ["python", "core/app.py"]
