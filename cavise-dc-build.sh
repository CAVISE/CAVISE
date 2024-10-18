#!/bin/bash

if [ -d "artery" ]; then
    echo "Initializing git submodules in artery directory..."
    cd artery
    git submodule init
    git submodule update
    cd ..
else
    echo "Directory artery does not exist."
    exit 1
fi

if [ $# -eq 0 ]
then
    echo "Building docker compose"
    docker-compose build
else
    echo "Building docker compose with $1 only"
    docker-compose build "$1"
fi