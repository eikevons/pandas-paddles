PACKAGE_NAME :=  pandas_paddles
IMAGE_BASE := $(PACKAGE_NAME)-test
TOX_DIR := /tmp/tox
TOX_ARGS := --workdir $(TOX_DIR)

WORKDIR := /project

# Filter tests to run:
# make TESTS="pattern" test
TESTS :=
PYTEST_ARGS := --cov=$(WORKDIR)/$(PACKAGE_NAME) -p no:cacheprovider -k "$(TESTS)" $(WORKDIR)/tests

# Enable BuildKit, necessary for `RUN --mount ...`
# See https://docs.docker.com/develop/develop-images/build_enhancements/
DOCKER_BUILDKIT := 1
export DOCKER_BUILDKIT

help:
	@echo "Provided targets"
	@echo "tests     run all unit tests against all Python versions"
	@echo "docs      create documentation."
	@echo "shell     start shell in latest python image"
	@echo "tests-X.Y run unit tests agains Python version X.Y"
	@echo "shell-X.Y start shell in test-image for Python version X.Y"
	@echo "image-X.Y build test-image for Python version X.Y"
	@echo "TODO:"
	@echo "watch      run unit tests on every change. Use make TESTS=... to filter tests"
	@echo "mypy       run mypy on package"
	@echo "format"
	@echo "wheel"

.PHONY: image image shell test watch docs

image: image-3.10


# TODO: Why is
#     image-%: $(IMAGE_BASE)-%.stamp
# not working?

image-3.8: $(IMAGE_BASE)-3.8.stamp
image-3.9: $(IMAGE_BASE)-3.9.stamp
image-3.10: $(IMAGE_BASE)-3.10.stamp
image-3.11: $(IMAGE_BASE)-3.11.stamp
image-3.12: $(IMAGE_BASE)-3.12.stamp

$(IMAGE_BASE)-%.stamp: docker/Dockerfile
	docker build --rm \
	    --tag $(IMAGE_BASE):$* \
	    --build-arg PY_VERSION=$* \
	    --file $< \
	    .
	@touch $@

.tox:
	mkdir -p .tox


tests: tests-3.8 tests-3.9 tests-3.10 tests-3.11 tests-3.12

tests-%: image-% | .tox
	docker run --rm \
	   --user $(shell id -u):$(shell id -g) \
	    --volume "$(PWD):$(WORKDIR):ro" \
	    --volume "$(PWD)/.tox:$(TOX_DIR)" \
	    $(IMAGE_BASE):$* \
	    tox $(TOX_ARGS)

shell-%: image-% | .tox
	docker run --rm \
	   --user $(shell id -u):$(shell id -g) \
	    --volume "$(PWD):$(WORKDIR):ro" \
	    --volume "$(PWD)/docs/source/api/:$(WORKDIR)/docs/source/api/" \
	    --volume "$(PWD)/docs/build/:$(WORKDIR)/docs/build/" \
	    --volume "$(PWD)/.tox:$(TOX_DIR)" \
	    -ti \
	    $(IMAGE_BASE):$* \
	    bash

shell: shell-3.12

docs: image-3.12 | .tox
	@mkdir -p docs/build/ docs/source/api
	docker run --rm \
	   --user $(shell id -u):$(shell id -g) \
	    --volume "$(PWD):$(WORKDIR):ro" \
	    --volume "$(PWD)/docs/source/api/:$(WORKDIR)/docs/source/api/" \
	    --volume "$(PWD)/docs/build/:$(WORKDIR)/docs/build/" \
	    --volume "$(PWD)/.tox:$(TOX_DIR)" \
	    -ti \
	    $(IMAGE_BASE):3.12 \
	    tox $(TOX_ARGS) -e docs r

# # Interactive targets
# shell: image
# 	docker run --rm -ti \
# 	    --name $(IMAGE_NAME)-$@ \
# 	    --volume "$(PWD):$(WORKDIR)" \
# 	    --env "HOME=/tmp/home" \
# 	    --user "$(shell id -u):$(shell id -g)" \
# 	    $(IMAGE_NAME) bash

# mypy: image
# 	docker run --rm -ti \
# 	    --name $(IMAGE_NAME)-$@ \
# 	    --volume "$(PWD):$(WORKDIR):ro" \
# 	    --env "HOME=/tmp/home" \
# 	    -w /tmp/home \
# 	    $(IMAGE_NAME) \
# 	    mypy $(WORKDIR)/pandas_paddles/


# docs: image
# # NOTE: Instead of `--volume "$(PWD)/docs/source/api:$(WORKDIR)/docs/source/api"` we
# # could also use `--tmpfs $(WORKDIR)/docs/source/api`. But this works only on Linux
# # (See https://docs.docker.com/storage/tmpfs/).
# 	@mkdir -p docs/build/ docs/source/api
# 	@docker run --rm --name "$(IMAGE_NAME)-$@" \
# 	    --volume "$(PWD):$(WORKDIR):ro" \
# 	    --volume "$(PWD)/docs/build:$(WORKDIR)/docs/build" \
# 	    --volume "$(PWD)/docs/source/api:$(WORKDIR)/docs/source/api" \
# 	    --user "$(shell id -u):$(shell id -g)" \
# 	    $(IMAGE_NAME) \
# 	    make -C $(WORKDIR)/docs html

