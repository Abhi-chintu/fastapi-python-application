
AWS_REGION ?= ap-south-1
AWS_ACCOUNT_ID ?= 637423245256

ECR_REGISTRY = $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

GATEWAY_REPO = $(ECR_REGISTRY)/demo/gateway
PRODUCTS_REPO = $(ECR_REGISTRY)/demo/product

IMAGE_TAG ?= latest

.PHONY: lint docker-build docker-push

lint:
	/opt/pylint-venv/bin/pylint gateway --exit-zero
	/opt/pylint-venv/bin/pylint products --exit-zero

docker-build:
	docker build -t $(GATEWAY_REPO):$(IMAGE_TAG) -f gateway/Dockerfile .
	docker build -t $(PRODUCTS_REPO):$(IMAGE_TAG) -f products/Dockerfile ./products

docker-push:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_REGISTRY)
	docker push $(GATEWAY_REPO):$(IMAGE_TAG)
	docker push $(PRODUCTS_REPO):$(IMAGE_TAG)
