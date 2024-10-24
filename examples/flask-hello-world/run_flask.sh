#!/bin/bash

# Configuration (using associative arrays for dictionary-like structure)
declare -A config
config=(
  [port]=5001
  [dev_mode]=true
  [rebuild_image]=false
)

# Docker image and container names
IMAGE_NAME="flask-app"
CONTAINER_NAME="flask-container"
VERSION_NUMBER="1.0.0"

# Stop the running container if it exists
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping running container: $CONTAINER_NAME"
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
else
    echo "No running container named $CONTAINER_NAME found."
fi

# Rebuild the image if rebuild_image is set to true
if [ "${config[rebuild_image]}" = true ]; then
    echo "Rebuilding Docker image: ${IMAGE_NAME}:${VERSION_NUMBER}"
    docker build -t "${IMAGE_NAME}:${VERSION_NUMBER}" .
else
    echo "Skipping image rebuild."
fi

# Check if dev_mode is true and set the environment variable accordingly
if [ "${config[dev_mode]}" = true ]; then
    echo "Running in development mode."
    ENV_VAR="-e FLASK_ENV=development"
else
    echo "Running in production mode."
    ENV_VAR="-e FLASK_ENV=production"
fi

# Run the Docker container with the specified port
docker run -d -p "${config[port]}:${config[port]}" \
    $ENV_VAR --name "$CONTAINER_NAME" \
    "$IMAGE_NAME:$VERSION_NUMBER"

# Output the status
if [ $? -eq 0 ]; then
    echo "Container $CONTAINER_NAME started successfully on port ${config[port]}."
else
    echo "Failed to start container $CONTAINER_NAME."
fi