FROM rayproject/ray:2.2.0-py310-cpu

USER root:root

# apt-get and system utilities

RUN apt-get update \
  && apt-get -y install apt-transport-https \
  && apt-get -y install apt-utils \
  && apt-get -y install curl \
  && apt-get -y install gcc \
  && apt-get -y install g++ \
  && apt-get -y install unixodbc unixodbc-dev \
  && apt-get clean

# adding custom MS repository
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

## TBD - upgrade to 20.04 and test
RUN curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# install SQL Server drivers
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# install SQL Server tools
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN /bin/bash -c "source ~/.bashrc"

# python libraries
RUN apt-get update && apt-get install -y \
    python3-pip python3-dev python3-setuptools \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# install necessary locales
RUN apt-get update && apt-get install -y locales \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen

RUN pip3 install --upgrade pip

# install SQL Server Python SQL Server connector module - pyodbc
# TBD - versions in this list might change depending on new releases and dependencies  
RUN pip3 install pyodbc
RUN pip3 install pyomo
RUN pip3 install cplex
RUN pip3 install protobuf==4.21.11
RUN pip3 install azureml-defaults
RUN pip3 install inference-schema
RUN pip3 install joblib
RUN pip3 install sqlalchemy
RUN pip3 install matplotlib
RUN pip3 install ray[default] gluonts torch mxnet orjson

