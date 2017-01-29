# Pull base image.
FROM ubuntu

# Avoid dialogs during installation.
ENV DEBIAN_FRONTEND noninteractive

# Avoid ERROR: invoke-rc.d: policy-rc.d denied execution of start.
# See: http://askubuntu.com/q/365911
RUN echo "#!/bin/sh\nexit 0" > /usr/sbin/policy-rc.d

# Install required packages.
RUN \
  apt-get update && \
  apt-get install -y python python-dev python-pip python-virtualenv libcurl4-openssl-dev tshark tor

# Define working directory.
ADD . /tmp/entrystats
WORKDIR /tmp/entrystats

# Install python requirements.
RUN pip install -r requirements.txt

RUN mkdir /entrystats
WORKDIR /entrystats

# Run script
CMD [ "python", "./entry_stats.py" ]
