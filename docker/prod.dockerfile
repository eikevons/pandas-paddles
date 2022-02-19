FROM python:3.8-slim

# Install curl to install poetry
RUN --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt : \
 && apt-get update \
 && apt-get install --yes --no-install-recommends \
    curl \
 && :

WORKDIR /app

# Copy project and dependencies.
COPY pyproject.toml poetry.lock* /app/
# Use poetry.lock* to cope with missing lock-file
COPY pandas_paddles/ /app/

# Prevent poetry from creating virtual envs
ENV POETRY_VIRTUALENVS_CREATE=false

# Copy and exec prod installation script
COPY docker/install-prod.sh /app/image-setup/install-prod.sh
RUN --mount=type=ssh,mode=0666 : \
 # Install project
 && /app/image-setup/install-prod.sh \
 && :
# TODO remove install-prod.sh
