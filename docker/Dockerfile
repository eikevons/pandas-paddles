FROM python:3.8-slim

# Install curl to install poetry
RUN --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt : \
 && apt-get update \
 && apt-get install --yes --no-install-recommends \
    curl \
    make \
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

COPY docker/entrypoint-ensure-home.sh /entrypoint
ENTRYPOINT ["/entrypoint"]

# Copy project and dependencies.
COPY pyproject.toml poetry.lock* .

# Prevent poetry from creating virtual envs
ENV POETRY_VIRTUALENVS_CREATE=false

# Install dependencies project
RUN : \
 && poetry install --no-root \
 && :

COPY README.rst .
COPY pandas_paddles pandas_paddles
COPY tests tests
# Install dependencies project
RUN : \
 && poetry install \
 && :

# Make sure packages can be updaated at run-time
RUN : \
 && find /usr/local/ -type d -exec chmod 0777 '{}' ';' \
 && :
