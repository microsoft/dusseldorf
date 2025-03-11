# Dockerfile for DNS listener

FROM  mcr.microsoft.com/azurelinux/base/python:3

ARG libFileName

# Setting environment variables
ENV DSSLDRF_CONNSTR=DSSLDRF_CONNSTR
ENV DSSLDRF_PORT=DSSLDRF_PORT

# Installing required packages
RUN tdnf -y update 
RUN tdnf -y install jq 
RUN tdnf -y install build-essential 
RUN tdnf -y install kernel-headers 
RUN tdnf -y install kernel-devel 
RUN tdnf -y install python3-devel 
RUN tdnf -y install gcc 
RUN tdnf -y install binutils 
# libpq package which is required for psycopg2
RUN tdnf -y install libpq-devel 
RUN ldconfig 
# RUN python3 -m pip install --upgrade pip

COPY src/ /dusseldorf
COPY src/$libFileName /dusseldorf

COPY deploy/configs/test.toml /dusseldorf/config.toml
WORKDIR /dusseldorf

RUN pip3 install $libFileName
RUN pip3 install -r requirements.txt

# Exposing required DNS port
EXPOSE 10053/udp

# Defining entrypoint and executing
# ENTRYPOINT ["python3", "run.py", "10053" ]

ENTRYPOINT ["python3", "run.py" ]

