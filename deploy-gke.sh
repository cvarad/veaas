#!/bin/sh

# Set zone
gcloud config set compute/zone us-central1-b
# Create default 3-node cluster
gcloud container clusters create mykube --preemptible --release-channel None --zone us-central1-b

# Install ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.5.1/deploy/static/provider/cloud/deploy.yaml
# Install minio
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install -f minio/minio-config.yaml -n minio-ns --create-namespace minio-proj bitnami/minio
# Install NATS
helm repo add nats https://nats-io.github.io/k8s/helm/charts/
helm install my-nats nats/nats

# Create services
kubectl apply -f rest/rest-service.yaml
kubectl apply -f minio/minio-external-service.yaml
# Create deployments
kubectl apply -f rest/rest-deployment.yaml
kubectl apply -f logs/logs-deployment.yaml
kubectl apply -f worker/worker-deployment.yaml
# Wait for the ingress installation to be ready, then configure ingress
sleep 60
kubectl apply -f rest/rest-ingress.yaml

# Port-forward minio console for debugging
kubectl port-forward -n minio-ns --address 0.0.0.0 service/minio-proj 9001:9001 &