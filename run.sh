#!/bin/bash

command="$1"
shift

services="$@"

case "$command" in
  build)
    echo "Запуск контейнеров с пересборкой..."
    docker compose -f dc-configs/docker-compose.yml --build -d $services
    ;;
  up)
    echo "Запуск контейнеров..."
    docker compose -f dc-configs/docker-compose.yml up -d $services
    ;;
  down)
    echo "Остановка и удаление контейнеров..."
    docker compose -f dc-configs/docker-compose.yml down $services
    ;;
  start)
    echo "Запуск остановленных контейнеров..."
    docker compose -f dc-configs/docker-compose.yml start $services
    ;;
  stop)
    echo "Остановка контейнеров..."
    docker compose -f dc-configs/docker-compose.yml stop $services
    ;;
  restart)
    echo "Перезапуск контейнеров..."
    docker compose -f dc-configs/docker-compose.yml restart $services
    ;;
  *)
    echo "Использование: $0 {build|up|start|stop|down|restart} [services...]"
    exit 1
    ;;
esac