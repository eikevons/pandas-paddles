PACKAGE_NAME :=  pandas_paddles
IMAGE_NAME := $(PACKAGE_NAME)-dev

WORKDIR := /project

# Filter tests to run:
# make TESTS="pattern" test
TESTS :=
PYTEST_ARGS := --cov=$(WORKDIR)/$(PACKAGE_NAME) -p no:cacheprovider -k "$(TESTS)" $(WORKDIR)/tests
DOCKER_ARGS := -ti --rm \
	       --volume "$(PWD):$(WORKDIR)" \
	       --env "HOME=/tmp/home" \
	       --user "$(shell id -u):$(shell id -g)"

# Enable BuildKit, necessary for `RUN --mount ...`
# See https://docs.docker.com/develop/develop-images/build_enhancements/
DOCKER_BUILDKIT := 1
export DOCKER_BUILDKIT

help:
	@echo "Provided targets"
	@echo "image      build development image"
	@echo "shell      start shell in development image"
	@echo "test       run unit tests. Use make TESTS=... to filter tests"
	@echo "watch      run unit tests on every change. Use make TESTS=... to filter tests"
	@echo "mypy       run mypy on package"
	@echo "docs       create documentation."
	@echo "TODO:"
	@echo "format"
	@echo "wheel"

.PHONY: image image shell test watch docs

image: $(IMAGE_NAME).stamp


$(IMAGE_NAME).stamp: docker/Dockerfile pyproject.toml poetry.lock docker/entrypoint-ensure-home.sh
	docker build --rm \
	    --tag $(IMAGE_NAME) \
	    --file $< \
	    .
	@touch $@

# Interactive targets
shell: image
	docker run \
	    $(DOCKER_ARGS) \
	    --name $(IMAGE_NAME)-$@ \
	    $(IMAGE_NAME) \
	    bash

test: image
	docker run \
	    $(DOCKER_ARGS) \
	    --name $(IMAGE_NAME)-$@ \
	    $(IMAGE_NAME) \
	    python -m pytest $(PYTEST_ARGS)

watch: image
	docker run \
	    $(DOCKER_ARGS) \
	    --name $(IMAGE_NAME)-$@ \
	    $(IMAGE_NAME) \
	    pytest-watch $(WORKDIR)/$(PACKAGE_NAME) $(WORKDIR)/tests -- $(PYTEST_ARGS)

mypy: image
	docker run \
	    $(DOCKER_ARGS) \
	    --name $(IMAGE_NAME)-$@ \
	    $(IMAGE_NAME) \
	    mypy $(WORKDIR)/pandas_paddles/


docs: image
# NOTE: Instead of `--volume "$(PWD)/docs/source/api:$(WORKDIR)/docs/source/api"` we
# could also use `--tmpfs $(WORKDIR)/docs/source/api`. But this works only on Linux
# (See https://docs.docker.com/storage/tmpfs/).
	@mkdir -p docs/build/ docs/source/api
	docker run \
	    $(DOCKER_ARGS) \
	    --name "$(IMAGE_NAME)-$@" \
	    --volume "$(PWD)/docs/build:$(WORKDIR)/docs/build" \
	    --volume "$(PWD)/docs/source/api:$(WORKDIR)/docs/source/api" \
	    $(IMAGE_NAME) \
	    make -C $(WORKDIR)/docs html

