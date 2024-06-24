ARG PY_VERSION
FROM python:${PY_VERSION}-slim

RUN : \
 && pip install -U pip \
 && pip install tox \
 && :

WORKDIR /project

COPY docker/entrypoint-ensure-home.sh /entrypoint
ENTRYPOINT ["/entrypoint"]
