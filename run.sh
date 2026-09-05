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

resolve_opencda_target() {
    local selected_target=""
    local service
    local -a resolved_services=()
    local -A seen_services=()

    for service in $services; do
        case "$service" in
          opencda|opencda-minimal|opencda-protobuf|opencda-coperception|opencda-cuda)
            if [ -n "$selected_target" ] && [ "$selected_target" != "$service" ]; then
                echo "Error: multiple OpenCDA build targets requested: $selected_target and $service" >&2
                exit 1
            fi
            selected_target="$service"
            service="opencda"
            ;;
        esac

        if [ -z "${seen_services[$service]+set}" ]; then
            resolved_services+=("$service")
            seen_services["$service"]=1
        fi
    done

    OPENCDA_BUILD_TARGET="${selected_target:-opencda}"
    case "$OPENCDA_BUILD_TARGET" in
      opencda)
        OPENCDA_IMAGE_TAG="local"
        ;;
      opencda-minimal)
        OPENCDA_IMAGE_TAG="minimal"
        ;;
      opencda-protobuf)
        OPENCDA_IMAGE_TAG="protobuf"
        ;;
      opencda-coperception)
        OPENCDA_IMAGE_TAG="coperception"
        ;;
      opencda-cuda)
        OPENCDA_IMAGE_TAG="cuda"
        ;;
    esac

    export OPENCDA_BUILD_TARGET
    export OPENCDA_IMAGE_TAG
    services="${resolved_services[*]}"
}

resolve_opencda_target

uses_opencda_service() {
    [ -z "$services" ] || [[ " $services " == *" opencda "* ]]
}

prepare_models_directory() {
    if uses_opencda_service; then
        if ! mkdir -p "$PATH_TO_MODELS"; then
            echo "Error: cannot create models directory: $PATH_TO_MODELS" >&2
            exit 1
        fi
    fi
}

case "$command" in
  build)
    if uses_opencda_service; then
        echo "Building container images (OpenCDA target: $OPENCDA_BUILD_TARGET)..."
    else
        echo "Building container images..."
    fi
    run_compose build $services
    ;;
  up)
    prepare_models_directory
    if uses_opencda_service; then
        echo "Creating and starting containers (OpenCDA target: $OPENCDA_BUILD_TARGET)..."
    else
        echo "Creating and starting containers..."
    fi
    run_compose "up -d" $services
    if echo "$services" | grep -qw "scenario-manager"; then
        xdg-open http://localhost 2>/dev/null || open http://localhost 2>/dev/null || start http://localhost
    fi
    ;;
  down)
    if uses_opencda_service; then
        echo "Stopping and removing containers (OpenCDA target: $OPENCDA_BUILD_TARGET)..."
    else
        echo "Stopping and removing containers..."
    fi
    run_compose down $services
    ;;
  start)
    if uses_opencda_service; then
        echo "Starting existing containers (OpenCDA target: $OPENCDA_BUILD_TARGET)..."
    else
        echo "Starting existing containers..."
    fi
    run_compose start $services
    ;;
  stop)
    if uses_opencda_service; then
        echo "Stopping running containers (OpenCDA target: $OPENCDA_BUILD_TARGET)..."
    else
        echo "Stopping running containers..."
    fi
    run_compose stop $services
    ;;
  restart)
    if uses_opencda_service; then
        echo "Restarting containers (OpenCDA target: $OPENCDA_BUILD_TARGET)..."
    else
        echo "Restarting containers..."
    fi
    run_compose restart $services
    ;;
  *)
    echo "Usage: $0 {build|up|start|stop|down|restart} [services...]"
    echo "OpenCDA targets: opencda, opencda-minimal, opencda-protobuf, opencda-coperception, opencda-cuda"
    exit 1
    ;;
esac
