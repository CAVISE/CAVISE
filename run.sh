#!/bin/bash

set -e

if [ -f "paths.conf" ]; then
    source paths.conf
else
    echo "Warning: paths.conf not found!"
fi

# Match bind-mounted workspace ownership, including invocation through sudo.
export uid="${uid:-${SUDO_UID:-$(id -u)}}"
export gid="${gid:-${SUDO_GID:-$(id -g)}}"

command="${1:-}"
if [ "$#" -gt 0 ]; then
    shift
fi

services="$*"

COMPOSE_MAIN="$CAVISE_ROOT/dc-configs/docker-compose.yml"
COMPOSE_SM="$PATH_TO_SCENARIO_MANAGER/docker-compose.yml"

run_compose() {
    local cmd="$1"
    shift
    local svcs="$*"

    if echo "$svcs" | grep -qw "scenario-manager"; then
        local remaining
        remaining=$(echo "$svcs" | sed 's/scenario-manager//g' | xargs)
        docker compose -f "$COMPOSE_SM" --profile prod $cmd
        svcs="$remaining"
    fi

    if [ -z "$svcs" ] && ! echo "$@" | grep -qw "scenario-manager"; then
        docker compose -f "$COMPOSE_MAIN" --env-file paths.conf $cmd
    elif [ -n "$svcs" ]; then
        docker compose -f "$COMPOSE_MAIN" --env-file paths.conf $cmd $svcs
    fi
}

resolve_build_targets() {
    local selected_target=""
    local selected_carla_target=""
    local service
    local -a resolved_services=()
    local -A seen_services=()

    for service in $services; do
        case "$service" in
          carla|carla-extended)
            if [ -n "$selected_carla_target" ] && [ "$selected_carla_target" != "$service" ]; then
                echo "Error: multiple CARLA build targets requested: $selected_carla_target and $service" >&2
                exit 1
            fi
            selected_carla_target="$service"
            service="carla"
            ;;
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

    CARLA_VERSION="${CARLA_VERSION:-0.9.16}"
    if [[ ! "$CARLA_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "Error: CARLA_VERSION must be a release number such as 0.9.16" >&2
        exit 1
    fi
    CARLA_BUILD_TARGET=default
    if [ "$selected_carla_target" = carla-extended ]; then
        CARLA_BUILD_TARGET=extended
    fi

    export CARLA_VERSION CARLA_BUILD_TARGET
    services="${resolved_services[*]}"
}

resolve_build_targets

prepare_carla_maps() {
    if [ "$CARLA_BUILD_TARGET" != extended ]; then
        return
    fi

    local archive="${CARLA_MAPS_ARCHIVE:-$PATH_TO_CARLA/$CARLA_VERSION/AdditionalMaps_${CARLA_VERSION}.tar.gz}"

    if [ -n "${CARLA_MAPS_ARCHIVE:-}" ]; then
        if [ ! -f "$archive" ] || [ ! -r "$archive" ]; then
            echo "Error: CARLA maps archive is not a readable file: $archive" >&2
            return 1
        fi
        archive=$(realpath -- "$archive")
        export CARLA_MAPS_CONTEXT="$(dirname -- "$archive")"
        export CARLA_MAPS_FILE="${archive##*/}"
    fi

    if [ -f "$archive" ]; then
        echo "Checking CARLA maps archive (full scan; large archives may take several minutes): $archive"
        if ! tar -tzf "$archive" > /dev/null; then
            echo "Error: invalid maps archive: $archive. Remove or replace it before rebuilding." >&2
            return 1
        fi
        echo "Using existing CARLA maps: $archive"
        return
    fi

    if ! command -v curl > /dev/null; then
        echo "Error: curl is required to download CARLA maps. Install it or place the archive at $archive" >&2
        return 1
    fi

    mkdir -p "$PATH_TO_CARLA/$CARLA_VERSION"
    echo "Downloading CARLA $CARLA_VERSION additional maps..."
    curl --http1.1 --fail --location --retry 3 --connect-timeout 30 \
        "https://downloads.carlasim.com/Linux/AdditionalMaps_${CARLA_VERSION}.tar.gz" \
        --output "$archive.part"
    echo "Checking downloaded CARLA maps archive (full scan): $archive.part"
    if ! tar -tzf "$archive.part" > /dev/null; then
        echo "Error: downloaded maps archive is invalid: $archive.part" >&2
        return 1
    fi
    mv -- "$archive.part" "$archive"
}

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
    prepare_carla_maps
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
    echo "CARLA targets: carla (default), carla-extended; version: CARLA_VERSION (default: 0.9.16)"
    echo "Existing maps archive: CARLA_MAPS_ARCHIVE=/path/to/AdditionalMaps_<version>.tar.gz"
    echo "OpenCDA targets: opencda, opencda-minimal, opencda-protobuf, opencda-coperception, opencda-cuda"
    exit 1
    ;;
esac
