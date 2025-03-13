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
    echo "Запуск контейнеров с пересборкой..."
    docker compose -f $CAVISE_ROOT/dc-configs/docker-compose.yml --env-file paths.conf build $services
    ;;
  up)
    echo "Запуск контейнеров..."
    docker compose -f $CAVISE_ROOT/dc-configs/docker-compose.yml --env-file paths.conf up -d $services
    ;;
  down)
    echo "Остановка и удаление контейнеров..."
    docker compose -f $CAVISE_ROOT/dc-configs/docker-compose.yml --env-file paths.conf down $services
    ;;
  start)
    echo "Запуск остановленных контейнеров..."
    docker compose -f $CAVISE_ROOT/dc-configs/docker-compose.yml --env-file paths.conf start $services
    ;;
  stop)
    echo "Остановка контейнеров..."
    docker compose -f $CAVISE_ROOT/dc-configs/docker-compose.yml --env-file paths.conf stop $services
    ;;
  restart)
    echo "Перезапуск контейнеров..."
    docker compose -f $CAVISE_ROOT/dc-configs/docker-compose.yml --env-file paths.conf restart $services
    ;;
  *)
    echo "Использование: $0 {build|up|start|stop|down|restart} [services...]"
    exit 1
    ;;
esac