VERSION=v2
DOCKERUSER=cvarad

build:
	docker build -f Dockerfile-rest -t rest .

push:
	docker tag rest $(DOCKERUSER)/rest:$(VERSION)
	docker push $(DOCKERUSER)/rest:$(VERSION)
	docker tag rest $(DOCKERUSER)/rest:latest
	docker push $(DOCKERUSER)/rest:latest
