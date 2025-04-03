#!/bin/bash

if [ -f "paths.conf" ]; then
    source paths.conf
else
    echo "Warning: paths.conf not found!"
fi

command="$1"
shift

services="$@"

case "$command" in
  build)
    echo "Building container images..."
    docker compose -f $CAVISE_ROOT/dc-configs/docker-compose.yml --env-file paths.conf build $services
    ;;
  up)
    echo "Creating and starting containers..."
    docker compose -f $CAVISE_ROOT/dc-configs/docker-compose.yml --env-file paths.conf up -d $services
    ;;
  down)
    echo "Stopping and removing containers..."
    docker compose -f $CAVISE_ROOT/dc-configs/docker-compose.yml --env-file paths.conf down $services
    ;;
  start)
    echo "Starting existing containers..."
    docker compose -f $CAVISE_ROOT/dc-configs/docker-compose.yml --env-file paths.conf start $services
    ;;
  stop)
    echo "Stopping running containers..."
    docker compose -f $CAVISE_ROOT/dc-configs/docker-compose.yml --env-file paths.conf stop $services
    ;;
  restart)
    echo "Restarting containers..."
    docker compose -f $CAVISE_ROOT/dc-configs/docker-compose.yml --env-file paths.conf restart $services
    ;;
  *)
    echo "Usage: $0 {build|up|start|stop|down|restart} [services...]"
    exit 1
    ;;
esac
