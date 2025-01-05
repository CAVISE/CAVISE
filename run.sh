#!/bin/bash

command="$1"
shift

services="$@"

case "$command" in
  build)
    echo "Запуск контейнеров с пересборкой..."
    docker compose -f simdata/compose.yml --project-directory="$PWD" --env-file cavise/scripts/environments/base.env up --build -d $services
    ;;
  up)
    echo "Запуск контейнеров..."
    docker compose -f simdata/compose.yml --project-directory="$PWD" --env-file cavise/scripts/environments/base.env up -d $services
    ;;
  down)
    echo "Остановка и удаление контейнеров..."
    docker compose -f simdata/compose.yml --project-directory="$PWD" --env-file cavise/scripts/environments/base.env down $services
    ;;
  start)
    echo "Запуск остановленных контейнеров..."
    docker compose -f simdata/compose.yml --project-directory="$PWD" --env-file cavise/scripts/environments/base.env start $services
    ;;
  stop)
    echo "Остановка контейнеров..."
    docker compose -f simdata/compose.yml --project-directory="$PWD" --env-file cavise/scripts/environments/base.env stop $services
    ;;
  restart)
    echo "Перезапуск контейнеров..."
    docker compose -f simdata/compose.yml --project-directory="$PWD" --env-file cavise/scripts/environments/base.env restart $services
    ;;
  *)
    echo "Использование: $0 {build|up|start|stop|down|restart} [services...]"
    exit 1
    ;;
esac