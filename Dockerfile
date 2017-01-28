
#
# Dockerfile for local network namespaces.
#
# https://github.com/mjuarezm/entrystats
#

# Pull base image.
FROM dockerfile/ubuntu

# Install Python.
RUN \
  apt-get update && \
  apt-get install -y python python-dev python-pip python-virtualenv && \
  rm -rf /var/lib/apt/lists/*

# Define working directory.
ADD . /opt/entrystats
WORKDIR /opt/entrystats

# Install requirements.
RUN pip install -r requirements.txt

# Define default command.
CMD ["bash"]
