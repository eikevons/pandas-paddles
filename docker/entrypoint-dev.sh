#!/bin/sh

if [ -n "$HOME" ] && [ ! -d "$HOME" ]; then
    mkdir -p "$HOME"
fi

exec "$@"
