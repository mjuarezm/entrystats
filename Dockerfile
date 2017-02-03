# Pull base image.
FROM debian:jessie

# Install required packages.
RUN apt-key adv --keyserver pool.sks-keyservers.net --recv A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89 \
	&& echo 'deb http://deb.torproject.org/torproject.org jessie main' >> /etc/apt/sources.list \
	&& apt-get update \
	&& apt-get -y --no-install-recommends install tor tor-geoipdb python python-dev python-pip \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*


# Add repo to temp for setup.
ADD . /tmp/entrystats
WORKDIR /tmp/entrystats

# Install python requirements.
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Define working directory to volume.
RUN mkdir /entrystats
WORKDIR /entrystats

# Run tor
CMD ["python", "entry_stats.py"]
