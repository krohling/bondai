#!/bin/bash

# ./run-container.sh OPENAI_API_KEY=#######

HOST_VOLUME_DIR="$(pwd)/agent-volume"
CONTAINER_VOLUME_DIR="/agent-volume"

declare -a ARGS
declare -a ENVS

# Define a function to parse environment variable arguments
parse_envs() {
    for env in "$@"; do
        if [[ $env == *=* ]]; then
            ENVS+=("-e" "$env")
        else
            ARGS+=("$env")
        fi
    done
}

parse_envs "$@"

mkdir -p ${HOST_VOLUME_DIR}


docker run -it --rm \
           -v ${HOST_VOLUME_DIR}:${CONTAINER_VOLUME_DIR} \
           -w ${CONTAINER_VOLUME_DIR} \
           "${ENVS[@]}" \
           bondai:latest bondai "${ARGS[@]}"
