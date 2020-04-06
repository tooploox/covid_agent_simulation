FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update && apt-get -y install \
    build-essential \
    pkg-config \
    python3-pip \
    python3-tk \
    python3 \
    python3-dev \
    wget

RUN pip3 install --upgrade pip

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt