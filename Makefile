NAME = moul/armhf-ocs-botnet-worker
AMQP_USER ?= guest:guest
VERSION ?= latest

build:
	docker build -t $(NAME):$(VERSION) .

devel:
	docker run \
	    -v /var/run/docker.sock:/var/run/docker.sock \
	    -e AMQP_USER=$(AMQP_USER) \
            --privileged -i -t --rm \
	    $(NAME):$(VERSION)

sync_docker:
	mv /usr/bin/docker /usr/bin/docker.orig
	/usr/bin/docker.orig run -v /usr/bin:/target -it --rm $(NAME):$(VERSION) cp /usr/bin/docker /target/docker
	service docker restart

release:
	docker push $(NAME):$(VERSION)
