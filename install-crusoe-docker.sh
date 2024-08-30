#!/bin/bash

# Function to check if a command is available on the system
check_command() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Ansible is installed
if ! check_command "docker compose"; then
    echo "Docker is not installed. Checkout \"https://docs.docker.com/engine/install\""
    exit 1
fi

docker_compose="docker-compose.yaml"

# Check if docker compose file exist in current workdir
if [ -f $docker_compose ]; then
    docker compose up -d
else
    echo "$docker_file does not exist! For successful installation you should not delete or modify provided $docker_file." 1>&2
    exit 1
fi