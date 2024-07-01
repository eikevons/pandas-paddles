ARG PY_VERSION
FROM python:${PY_VERSION}-slim

RUN \
 --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt \ 
 : \
 && apt-get update \
 && apt-get install --yes --no-install-recommends \
    git \
    make \
 && :

# Configure package manager cache locations
# Use
#   RUN \
#     --mount=type=cache,target=/var/cache/pkg.managers.d \
#     ...
# when installing with package managers
ENV PKG_CACHE_BASE=/var/cache/pkg.managers.d \
    PIP_CACHE_DIR=/var/cache/pkg.managers.d/pip

RUN \
 --mount=type=cache,target=/var/cache/pkg.managers.d \
 : \
 && pip install -U pip \
 && pip install tox \
 && :

WORKDIR /project

COPY docker/entrypoint-ensure-home.sh /entrypoint
ENTRYPOINT ["/entrypoint"]
