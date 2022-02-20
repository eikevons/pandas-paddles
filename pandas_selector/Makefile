TARGETS := pandas_selector/__init__.py pyproject.toml
VERSION := $(shell python3 -c "import toml; d = toml.load('../pyproject.toml'); print(d['tool']['poetry']['version'])")

clean:
	rm -rf $(TARGETS) dist/

build: $(TARGETS)
	poetry build

%: %.IN ../pyproject.toml
	VERSION=$(VERSION) envsubst < $< > $*
