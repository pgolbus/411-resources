#!/bin/bash

# Variables (fill these in!)
IMAGE_NAME="boxing_image"
CONTAINER_TAG="latest"
CONTAINER_NAME="${IMAGE_NAME}_container"
HOST_PORT=5001
CONTAINER_PORT=5000
DB_VOLUME_PATH="./db"
ENV_FILE=".env"
BUILD=true

# Build Docker image
if [ "$BUILD" = true ]; then
  echo "Building Docker image..."
  docker build -t ${IMAGE_NAME}:${CONTAINER_TAG} .
else
  echo "Skipping Docker image build..."
fi

# Create DB directory if it doesn't exist
if [ ! -d "${DB_VOLUME_PATH}" ]; then
  echo "Creating database directory at ${DB_VOLUME_PATH}..."
  mkdir -p "${DB_VOLUME_PATH}"
fi

# Stop and remove existing container
if [ "$(docker ps -q -a -f name=${CONTAINER_NAME})" ]; then
  echo "Stopping existing container: ${CONTAINER_NAME}..."
  docker stop ${CONTAINER_NAME}
  echo "🗑️ Removing container: ${CONTAINER_NAME}..."
  docker rm ${CONTAINER_NAME}
else
  echo "ℹNo existing container named ${CONTAINER_NAME} found."
fi

# Run the Docker container
echo "Running Docker container..."
docker run -d \
  --name ${CONTAINER_NAME} \
  -p ${HOST_PORT}:${CONTAINER_PORT} \
  --env-file ${ENV_FILE} \
  -v "${DB_VOLUME_PATH}":/app/db \
  ${IMAGE_NAME}:${CONTAINER_TAG}

echo "Docker container '${CONTAINER_NAME}' is running on http://localhost:${HOST_PORT}"