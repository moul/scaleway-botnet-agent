FROM armbuild/dockerfile-ubuntu:latest

# Install Python & Docker dependencies & Tools
RUN apt-get update && \
    apt-get install -y \
        python python-dev python-pip python-virtualenv \
	curl
WORKDIR /data

# Install Celery
RUN pip install celery

# Install redis
RUN pip install redis

# Configure agent
CMD C_FORCE_ROOT=1 celery worker -B -A ocs -l INFO

# Install Docker
ADD ./docker-1.3.0 /usr/bin/docker
RUN chmod +x /usr/bin/docker

# Add agent
ADD ./agent.py /data/ocs.py
