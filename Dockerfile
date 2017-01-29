# Pull base image.
FROM ubuntu

# Avoid dialogs during installation.
ENV DEBIAN_FRONTEND noninteractive

# Install required packages.
RUN \
  apt-get update && \
  apt-get install -y python python-dev python-pip python-virtualenv libcurl4-openssl-dev tshark tor

# Add repo to temp for setup.
ADD . /tmp/entrystats
WORKDIR /tmp/entrystats

# Install python requirements.
RUN pip install -r requirements.txt

# Define working directory to volume.
RUN mkdir /entrystats
WORKDIR /entrystats

# Run script
CMD [ "python", "./entry_stats.py" ]
