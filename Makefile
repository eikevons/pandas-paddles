PACKAGE_NAME :=  pandas_selector
IMAGE_NAME := $(PACKAGE_NAME)
DEV_IMAGE_NAME := $(IMAGE_NAME)-dev

# Filter tests to run:
# make TESTS="pattern" test
TESTS :=
PYTEST_ARGS := --cov=/app/$(PACKAGE_NAME) -p no:cacheprovider -k "$(TESTS)" /app/tests

# Enable BuildKit, necessary for `RUN --mount ...`
# See https://docs.docker.com/develop/develop-images/build_enhancements/
DOCKER_BUILDKIT := 1
export DOCKER_BUILDKIT

help:
	@echo "Provided targets"
	@echo "image      build prod image"
	@echo "devimage   build development image"
	@echo "shell      start shell in development image"
	@echo "test       run unit tests. Use make TESTS=... to filter tests"
	@echo "watch      run unit tests on every change. Use make TESTS=... to filter tests"
	@echo "mypy       run mypy on package"
	@echo "docs       create documentation."
	@echo "TODO:"
	@echo "format"
	@echo "wheel"

.PHONY: image devimage shell test watch docs

image: $(IMAGE_NAME).stamp

devimage: $(DEV_IMAGE_NAME).stamp

$(IMAGE_NAME).stamp: docker/prod.dockerfile pyproject.toml poetry.lock docker/install-prod.sh
	docker build --rm \
	    --tag $(IMAGE_NAME) \
	    --file $< \
	    .
	@touch $@

$(DEV_IMAGE_NAME).stamp: docker/dev.dockerfile pyproject.toml poetry.lock $(IMAGE_NAME).stamp
	docker build --rm \
	    --tag $(DEV_IMAGE_NAME) \
	    --build-arg "SRC_IMAGE=$(IMAGE_NAME)" \
	    --file $< \
	    .
	@touch $@

# Interactive targets
shell: devimage
	docker run --rm -ti \
	    --name $(DEV_IMAGE_NAME)-$@ \
	    --volume "$(PWD):/app" \
	    --env "HOME=/tmp/home" \
	    --user "$(shell id -u):$(shell id -g)" \
	    $(DEV_IMAGE_NAME)

test: devimage
	docker run --rm -ti \
	    --name $(DEV_IMAGE_NAME)-$@ \
	    --volume "$(PWD):/app:ro" \
	    --env "HOME=/tmp/home" \
	    -w /tmp/home \
	    $(DEV_IMAGE_NAME) \
	    pytest $(PYTEST_ARGS)

watch: devimage
	docker run --rm -ti \
	    --name $(DEV_IMAGE_NAME)-$@ \
	    --volume "$(PWD):/app:ro" \
	    --env "HOME=/tmp/home" \
	    -w /tmp/home \
	    $(DEV_IMAGE_NAME) \
	    pytest-watch /app/$(PACKAGE_NAME) /app/tests -- $(PYTEST_ARGS)

mypy: devimage
	docker run --rm -ti \
	    --name $(DEV_IMAGE_NAME)-$@ \
	    --volume "$(PWD):/app:ro" \
	    --env "HOME=/tmp/home" \
	    -w /tmp/home \
	    $(DEV_IMAGE_NAME) \
	    mypy /app/pandas_selector/


docs: devimage
# NOTE: Instead of `--volume "$(PWD)/docs/source/api:/app/docs/source/api"` we
# could also use `--tmpfs /app/docs/source/api`. But this works only on Linux
# (See https://docs.docker.com/storage/tmpfs/).
	@mkdir -p docs/build/ docs/source/api
	@docker run --rm --name "$(DEV_IMAGE_NAME)-$@" \
	    --volume "$(PWD):/app:ro" \
	    --volume "$(PWD)/docs/build:/app/docs/build" \
	    --volume "$(PWD)/docs/source/api:/app/docs/source/api" \
	    --user "$(shell id -u):$(shell id -g)" \
	    --workdir /app \
	    $(DEV_IMAGE_NAME) \
	    make -C /app/docs html

