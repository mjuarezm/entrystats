# Pull base image.
FROM ubuntu

# Install required packages.
RUN \
  apt-get update && \
  apt-get install -y python python-dev python-pip python-virtualenv && \
  apt-get install tshark
  rm -rf /var/lib/apt/lists/*

# Define working directory.
ADD . /opt/entrystats
WORKDIR /opt/entrystats

# Install python requirements.
RUN pip install -r requirements.txt

# Define default command.
CMD "python entry_stats.py"