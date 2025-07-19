#!/bin/sh

# Wait for RabbitMQ to be ready
until nc -z -v -w30 rabbitmq 5672
do
  echo "Waiting for RabbitMQ to start..."
  sleep 1
done

# Wait for PostgreSQL to be ready
until nc -z -v -w30 db 5432
do
  echo "Waiting for PostgreSQL to start..."
  sleep 1
done

# Run the command
exec "$@"