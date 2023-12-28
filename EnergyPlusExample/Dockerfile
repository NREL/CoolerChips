FROM ubuntu:latest

ENV ENERGYPLUS_LINK=https://github.com/NREL/EnergyPlus/releases/download/v23.2.0/EnergyPlus-23.2.0-7636e6b3e9-Linux-Ubuntu20.04-x86_64.tar.gz
RUN  apt-get update && apt-get install -y wget unzip python3 python3-pip python-is-python3 \
    && wget $ENERGYPLUS_LINK \
    && tar -xzf EnergyPlus-23.2.0-7636e6b3e9-Linux-Ubuntu20.04-x86_64.tar.gz \
    && mv EnergyPlus-23.2.0-7636e6b3e9-Linux-Ubuntu20.04-x86_64 EnergyPlus 

RUN pip install helics matplotlib pandas

RUN ln -s /EnergyPlus/energyplus /usr/local/bin/energyplus

WORKDIR /app

CMD ["bash"]