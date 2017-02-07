# Pull base image.
FROM debian:latest

# Install required packages.
RUN apt-get update \
	&& apt-get -y install tor python python-dev python-pip \
	&& apt-get clean && rm -rf /var/lib/apt/lists/*


# Add repo to temp for setup.
ADD . /tmp/nodestats
WORKDIR /tmp/nodestats

# Install python requirements.
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Define working directory to volume.
RUN mkdir /nodestats
WORKDIR /nodestats

# Run tor
CMD ["python", "node_stats.py"]
