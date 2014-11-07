NAME = ocs-botnet-worker
MASTER ?= $(shell oc-metadata | grep manager | cut -d= -f3)
AMQP_USER ?= guest:guest

build:
	docker build -t $(NAME) .

run:
	docker run \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-e AMQP_USER=$(AMQP_USER) \
		-e MASTER=$(MASTER) \
		-it --rm $(NAME)

sync_docker:
	mv /usr/bin/docker /usr/bin/docker.orig
	/usr/bin/docker.orig run -v /usr/bin:/target -it --rm $(NAME) cp /usr/bin/docker /target/docker
	service docker restart
