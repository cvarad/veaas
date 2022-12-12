VERSION=v3
DOCKERUSER=hunarjain09

build:
	docker build -f Dockerfile -t veaas-worker .
push:
	docker tag veaas-worker $(DOCKERUSER)/veaas-worker:$(VERSION)
	docker push $(DOCKERUSER)/veaas-worker:$(VERSION)
	docker tag veaas-worker $(DOCKERUSER)/veaas-worker:latest
	docker push $(DOCKERUSER)/veaas-worker:latest
