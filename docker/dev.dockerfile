ARG SRC_IMAGE
FROM $SRC_IMAGE

RUN --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt : \
 && apt-get update \
 && apt-get install --yes --no-install-recommends \
    bash \
    git \
    jq \
    make \
    vim \
 && :

# Copy and exec prod installation script
COPY docker/install-dev.sh /app/image-setup/install-dev.sh
RUN --mount=type=ssh,mode=0666 : \
 && /app/image-setup/install-dev.sh \
 # Allow all users to install python packages (this is only the dev image)
 && find /usr/local/lib/python3.8/site-packages -type d -exec chmod g+=rwx '{}' ';' \
 && :
# TODO remove install-dev.sh

COPY docker/entrypoint-dev.sh /entrypoint-dev.sh

ENTRYPOINT ["/entrypoint-dev.sh"]

# Use bash as default command
CMD ["bash"]
