FROM armbuild/dockerfile-ubuntu:latest

# Install Python & Docker dependencies & Tools
RUN apt-get update && \
    apt-get install -y \
        python python-dev python-pip python-virtualenv \
	curl wget
WORKDIR /data

# Install Celery
RUN pip install celery

# Install redis
RUN pip install redis

# Configure agent
CMD C_FORCE_ROOT=1 celery worker -B -A ocs -l INFO

# Install tools
# RUN apt-get install -y
ADD https://raw.githubusercontent.com/moul/junk/master/mbin/port_docker_image /usr/local/bin/port_docker_image
ADD https://raw.githubusercontent.com/moul/junk/master/mbin/docker-user-repos /usr/local/bin/docker-user-repos

# ARMHF SPECIFIC:
# Install Docker
ADD ./docker-1.3.0 /usr/bin/docker
RUN chmod +x /usr/bin/docker

# Add agent
ADD ./agent.py /data/ocs.py
