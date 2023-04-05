#!/bin/sh

# Fail on errors
set -e

# Update pip
pip install -U pip

# Install poetry
curl -sSL https://install.python-poetry.org | \
    POETRY_HOME=/opt/poetry python -
chmod +x /opt/poetry/bin/poetry
ln -s /opt/poetry/bin/poetry /usr/local/bin

cd /app
# Install prod dependencies
poetry install --no-dev --no-root
