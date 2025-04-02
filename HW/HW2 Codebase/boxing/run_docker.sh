#!/bin/bash

# Variables
IMAGE_NAME="boxing"
CONTAINER_TAG="latest"
HOST_PORT=5000
CONTAINER_PORT=5000
DB_VOLUME_PATH="$(pwd)/db"
BUILD=true

if [ "$BUILD" = true ]; then
  echo "Building Docker image..."
  docker build -t ${IMAGE_NAME}:${CONTAINER_TAG} .
else
  echo "Skipping Docker image build..."
fi

if [ ! -d "${DB_VOLUME_PATH}" ]; then
  echo "Creating database directory at ${DB_VOLUME_PATH}..."
  mkdir -p "${DB_VOLUME_PATH}"
fi

if [ "$(docker ps -q -a -f name=${IMAGE_NAME}_container)" ]; then
  echo "Stopping running container: ${IMAGE_NAME}_container"
  docker stop ${IMAGE_NAME}_container

  if [ $? -eq 0 ]; then
    echo "Removing container: ${IMAGE_NAME}_container"
    docker rm ${IMAGE_NAME}_container
  else
    echo "Failed to stop container: ${IMAGE_NAME}_container"
    exit 1
  fi
else
  echo "No running container named ${IMAGE_NAME}_container found."
fi

# Run the Docker container with the necessary ports and volume mappings
echo "Running Docker container..."
# Add this line to diagnose the command
echo "Running command: docker run -d --name ${IMAGE_NAME}_container -p ${HOST_PORT}:${CONTAINER_PORT} --env-file .env -v ${DB_VOLUME_PATH}:/app/db ${IMAGE_NAME}:${CONTAINER_TAG}"

docker run -d \
  --name "${IMAGE_NAME}_container" \
  -p "${HOST_PORT}:${CONTAINER_PORT}" \
  --env-file .env \
  -v "${DB_VOLUME_PATH}":/app/db \
  "${IMAGE_NAME}:${CONTAINER_TAG}"

# Check if the container started successfully
if [ $? -eq 0 ]; then
  echo "Docker container is running on http://localhost:${HOST_PORT}"
else
  echo "Failed to start container. See error above."
  echo "Press [Enter] to exit..."
  read
fi

