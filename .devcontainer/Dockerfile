FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye 

COPY requirements.txt /tmp/requirements.txt

RUN apt-get update && apt install -y sudo python3-dev graphviz libgraphviz-dev pkg-config
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt