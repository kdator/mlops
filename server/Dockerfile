FROM ubuntu:22.04

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3-pip \
    && apt-get clean

RUN python3.10 -m pip install --upgrade pip

RUN pip install -r requirements.txt

WORKDIR server

COPY server.py server.py

EXPOSE 8080
