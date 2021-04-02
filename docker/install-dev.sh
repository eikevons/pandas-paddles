#!/bin/sh

# Fail on errors
set -e

cd /app
# Install dev dependencies
poetry install --no-root
