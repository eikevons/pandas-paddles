FROM python:3.8-slim

# Install curl to install poetry
RUN --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt : \
 && apt-get update \
 && apt-get install --yes --no-install-recommends \
    curl \
 && :

# Install poetry
RUN : \
 && pip install -U pip \
 && curl -sSL https://install.python-poetry.org | \
    POETRY_HOME=/opt/poetry python - \
 && chmod +x /opt/poetry/bin/poetry \
 && ln -s /opt/poetry/bin/poetry /usr/local/bin \
 && :

WORKDIR /project

# Copy project and dependencies.
COPY pyproject.toml poetry.lock* .

# Prevent poetry from creating virtual envs
ENV POETRY_VIRTUALENVS_CREATE=false

COPY docker/entrypoint-ensure-home.sh /entrypoint
ENTRYPOINT ["/entrypoint"]

# Install project
RUN --mount=type=ssh,mode=0666 : \
 && poetry install  --no-root \
 && :

# Make sure packages can be updaated at run-time
RUN : \
 && find /usr/local/ -type d -exec chmod 0777 '{}' ';' \
 && :
