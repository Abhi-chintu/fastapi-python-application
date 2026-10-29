PYTHON ?= python3
PIP := $(PYTHON) -m pip

ECR_REGISTRY ?=
IMAGE_TAG ?= $(shell git rev-parse --short HEAD)
GATEWAY_IMAGE = $(ECR_REGISTRY)/python-eks-gateway
PRODUCTS_IMAGE = $(ECR_REGISTRY)/python-eks-products

.PHONY: ci-setup lint static-analysis coverage docker-build docker-push check-ecr

ci-setup:
	$(PIP) install -r gateway/requirements.txt -r products/requirements.txt
	$(PIP) install ruff bandit pytest pytest-cov

lint:
	$(PYTHON) -m ruff check gateway products

static-analysis:
	$(PYTHON) -m bandit -r gateway products

coverage:
	$(PYTHON) -m pytest --cov=gateway --cov=products --cov-report=term-missing --cov-report=xml

check-ecr:
	@test -n "$(ECR_REGISTRY)" || (echo "Set ECR_REGISTRY to your ECR registry URL"; exit 2)

docker-build: check-ecr
	docker build -f gateway/Dockerfile \
		-t $(GATEWAY_IMAGE):$(IMAGE_TAG) -t $(GATEWAY_IMAGE):latest .
	docker build -f products/Dockerfile \
		-t $(PRODUCTS_IMAGE):$(IMAGE_TAG) -t $(PRODUCTS_IMAGE):latest products

docker-push: check-ecr
	docker push $(GATEWAY_IMAGE):$(IMAGE_TAG)
	docker push $(GATEWAY_IMAGE):latest
	docker push $(PRODUCTS_IMAGE):$(IMAGE_TAG)
	docker push $(PRODUCTS_IMAGE):latest
