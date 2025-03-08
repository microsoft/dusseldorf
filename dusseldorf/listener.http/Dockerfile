FROM  mcr.microsoft.com/azurelinux/base/python:3


ARG libFileName
ENV CONNSTR=CONNSTR

# Installing libpq package which is required for psycopg2
RUN tdnf -y update 
RUN tdnf -y install jq 
RUN tdnf -y install build-essential kernel-headers kernel-devel python3-devel gcc binutils 
RUN tdnf -y install libpq-devel 
RUN ldconfig 

COPY src/ /dusseldorf
COPY src/$libFileName /dusseldorf

COPY deploy/configs/config-test.toml /dusseldorf/config.toml
WORKDIR /dusseldorf

RUN pip3 install $libFileName
RUN pip3 install -r requirements.txt

# Exposing required DNS port
EXPOSE 10080/tcp

# Defining entrypoint and executing
ENTRYPOINT ["python3", "run.py", "10080" ]
