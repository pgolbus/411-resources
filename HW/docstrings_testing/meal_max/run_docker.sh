#!/bin/bash

# Variables
IMAGE_NAME="meal_max"
CONTAINER_TAG="0.2.0"
HOST_PORT=5000
CONTAINER_PORT=5000
DB_VOLUME_PATH="./db"   # Adjust this to the desired host path for the database persistence
BUILD=true  # Set this to true if you want to build the image

# Check if we need to build the Docker image
if [ "$BUILD" = true ]; then
  echo "Building Docker image..."
  docker build -t ${IMAGE_NAME}:${CONTAINER_TAG} .
else
  echo "Skipping Docker image build..."
fi

# Check if the database directory exists; if not, create it
if [ ! -d "${DB_VOLUME_PATH}" ]; then
  echo "Creating database directory at ${DB_VOLUME_PATH}..."
  mkdir -p ${DB_VOLUME_PATH}
fi

# Run the Docker container with the necessary ports and volume mappings
echo "Running Docker container..."
docker run -d \
  --name ${IMAGE_NAME}_container \
  --env-file .env \
  -p ${HOST_PORT}:${CONTAINER_PORT} \
  -v ${DB_VOLUME_PATH}:/app/db \
  ${IMAGE_NAME}:${CONTAINER_TAG}

echo "Docker container is running on port ${HOST_PORT}."
