VERSION=v1
DOCKERUSER=hunarjain09

build:
	docker build -f Dockerfile-rest -t rest .

push:
	docker tag rest $(DOCKERUSER)/rest:$(VERSION)
	docker push $(DOCKERUSER)/rest:$(VERSION)
	docker tag rest $(DOCKERUSER)/rest:latest
	docker push $(DOCKERUSER)/rest:latest
