FROM --platform=linux/x86_64 ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

ENV ENERGYPLUS_LINK=https://github.com/NREL/EnergyPlus/releases/download/v23.2.0/EnergyPlus-23.2.0-7636e6b3e9-Linux-Ubuntu22.04-x86_64.tar.gz

# Install system dependencies
RUN  apt-get update && apt-get install -y \
    wget=1.21.*\
    unzip=6.0-* \
#    cmake \
#    git \
    python3=3.10.* \
    python3-pip=22.0.* \
    python-is-python3

# Install system dependencies
RUN  apt-get update && apt-get install -y \
    python3-tk=3.10.* 

# Download and install EnergyPlus    
RUN wget $ENERGYPLUS_LINK \
    && tar -xzf EnergyPlus-23.2.0-7636e6b3e9-Linux-Ubuntu22.04-x86_64.tar.gz \
    && mv EnergyPlus-23.2.0-7636e6b3e9-Linux-Ubuntu22.04-x86_64 EnergyPlus

# Download and install Paraview
RUN wget -O ParaView-5.12.0-MPI-Linux-Python3.10-x86_64.tar.gz "https://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v5.12&type=binary&os=Linux&downloadFile=ParaView-5.12.0-MPI-Linux-Python3.10-x86_64.tar.gz" \
    && tar -xzf ParaView-5.12.0-MPI-Linux-Python3.10-x86_64.tar.gz \
    && mv ParaView-5.12.0-MPI-Linux-Python3.10-x86_64 Paraview

# Install Paraview dependencies
RUN apt-get install ffmpeg libsm6 libxext6 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-xinerama0 libxcb-xinput0 libxcb-xfixes0 libxkbcommon-x11-0 -y

# Copy requirements.txt to the docker image
COPY requirements.txt /app/requirements.txt

# Install Python dependencies from requirements.txt file
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN ln -s /EnergyPlus/energyplus /usr/local/bin/energyplus

WORKDIR /app

CMD ["python", "main.py"]