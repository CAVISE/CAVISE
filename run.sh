#!/bin/bash

if [ -f "paths.conf" ]; then
    source paths.conf
else
    echo "Warning: paths.conf not found!"
fi

command="$1"
shift

services="$@"

COMPOSE_MAIN="$CAVISE_ROOT/dc-configs/docker-compose.yml"
COMPOSE_SM="$PATH_TO_SCENARIO_MANAGER/docker-compose.yml"

run_compose() {
    local cmd="$1"
    shift
    local svcs="$@"

    if echo "$svcs" | grep -qw "scenario-manager"; then
        local remaining=$(echo "$svcs" | sed 's/scenario-manager//g' | xargs)
        docker compose -f $COMPOSE_SM --profile prod $cmd $remaining
        svcs="$remaining"
    fi

    if [ -z "$svcs" ] && ! echo "$@" | grep -qw "scenario-manager"; then
        docker compose -f $COMPOSE_MAIN --env-file paths.conf $cmd
    elif [ -n "$svcs" ]; then
        docker compose -f $COMPOSE_MAIN --env-file paths.conf $cmd $svcs
    fi
}

case "$command" in
  build)
    echo "Building container images..."
    run_compose build $services
    ;;
  up)
    echo "Creating and starting containers..."
    run_compose "up -d" $services
    if echo "$services" | grep -qw "scenario-manager"; then
        xdg-open http://localhost 2>/dev/null || open http://localhost 2>/dev/null || start http://localhost
    fi
    ;;
  down)
    echo "Stopping and removing containers..."
    run_compose down $services
    ;;
  start)
    echo "Starting existing containers..."
    run_compose start $services
    ;;
  stop)
    echo "Stopping running containers..."
    run_compose stop $services
    ;;
  restart)
    echo "Restarting containers..."
    run_compose restart $services
    ;;
  *)
    echo "Usage: $0 {build|up|start|stop|down|restart} [services...]"
    exit 1
    ;;
esac
