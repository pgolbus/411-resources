#!/bin/bash
# test joey
# Variables
IMAGE_NAME="boxing-image"
CONTAINER_NAME="boxing-container"
HOST_PORT=5001
IMAGE_NAME=boxing_image
CONTAINER_TAG=latest
HOST_PORT=5001
CONTAINER_PORT=5000
DB_VOLUME_PATH="db"  # Relative path to your database directory
BUILD=false  # Set this to true if you want to build the image
DB_VOLUME_PATH=$(pwd)/db # Adjust this to the desired host path for the database persistence
BUILD=true # Set this to true if you want to build the image

# Check if we need to build the Docker image
if [ "$BUILD" = true ]; then
    echo "Building Docker image..."
    docker build -t $IMAGE_NAME ./boxing
  echo "Building Docker image..."
  docker build -t ${IMAGE_NAME}:${CONTAINER_TAG} .

else
    echo "Skipping Docker image build..."
fi

# Check if the database directory exists; if not, create it
if [ ! -d "${DB_VOLUME_PATH}" ]; then
    echo "Creating database directory at ${DB_VOLUME_PATH}..."
    mkdir -p ${DB_VOLUME_PATH}
  echo "Creating database directory at ${DB_VOLUME_PATH}..."
  mkdir -p "${DB_VOLUME_PATH}"
fi

# Stop and remove the running container if it exists
if [ "$(docker ps -q -a -f name=${CONTAINER_NAME})" ]; then
    echo "Stopping running container: ${CONTAINER_NAME}"
    docker stop ${CONTAINER_NAME}
if [ "$(docker ps -q -a -f name=${IMAGE_NAME}_container)" ]; then
    echo "Stopping running container: ${IMAGE_NAME}_container"
    docker stop ${IMAGE_NAME}_container

    # Check if the stop was successful
    if [ $? -eq 0 ]; then
        echo "Removing container: ${CONTAINER_NAME}"
        docker rm ${CONTAINER_NAME}
        echo "Removing container: ${IMAGE_NAME}_container"
        docker rm ${IMAGE_NAME}_container
    else
        echo "Failed to stop container: ${CONTAINER_NAME}"
        exit 1
    fi
else
    echo "No running container named ${CONTAINER_NAME} found."
fi

# Run the Docker container with the necessary ports and volume mappings
echo "Running Docker container..."
docker run -d \
    --name ${CONTAINER_NAME} \
    --env-file .env \
    -v "$(pwd)/${DB_VOLUME_PATH}:/app/db" \
    -p ${HOST_PORT}:${CONTAINER_PORT} \
    ${IMAGE_NAME}

docker run -d \
  --name ${IMAGE_NAME}_container \
  --env-file .env \
  -p ${HOST_PORT}:${CONTAINER_PORT} \
  -v ${DB_VOLUME_PATH}:/app/db \
  ${IMAGE_NAME}:${CONTAINER_TAG}
echo "Docker container is running on port ${HOST_PORT}."
echo "Database is persisted at ${DB_VOLUME_PATH} and mapped to /app/db in the container."