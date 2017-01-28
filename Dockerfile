# Pull base image.
FROM ubuntu

# Avoid dialogs during installation.
ENV DEBIAN_FRONTEND noninteractive

# Install required packages.
RUN \
  apt-get update && \
  apt-get install -y python python-dev python-pip python-virtualenv && \
  apt-get -y install tshark && \
  rm -rf /var/lib/apt/lists/*

# Define working directory.
ADD . /opt/entrystats
WORKDIR /opt/entrystats

# Install python requirements.
RUN pip install -r requirements.txt
