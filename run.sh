#!/bin/bash

case "$1" in
  build)
    echo "Запуск контейнеров..."
    docker compose --env-file compose.env up --build -d
    ;;
  up)
    echo "Запуск контейнеров..."
    docker compose --env-file compose.env up -d
    ;;
  down)
    echo "Остановка и удаление контейнеров..."
    docker compose --env-file compose.env down
    ;;
  start)
    echo "Запуск остановленного контейнеров..."
    docker compose --env-file compose.env start
    ;;
  stop)
    echo "Остановка контейнеров..."
    docker compose --env-file compose.env stop
    ;;
  restart)
    echo "Перезапуск контейнеров..."
    docker compose --env-file compose.env restart
    ;;
  *)
    echo "Использование: $0 {build|up|start|stop|down|restart}"
    exit 1
    ;;
esac