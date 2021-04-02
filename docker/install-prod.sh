#!/bin/sh

# Fail on errors
set -e

# Update pip
pip install -U pip

# Install poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | \
    POETRY_HOME=/opt/poetry python -
chmod +x /opt/poetry/bin/poetry
ln -s /opt/poetry/bin/poetry /usr/local/bin

cd /app
# Install prod dependencies
poetry install --no-dev --no-root
