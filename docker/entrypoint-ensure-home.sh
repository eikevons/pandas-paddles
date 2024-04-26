#!/bin/sh

if [ -n "$HOME" ] && [ ! -d "$HOME" ]; then
    echo "Creating HOME=$HOME"
    mkdir -p "$HOME"
fi

exec "$@"
