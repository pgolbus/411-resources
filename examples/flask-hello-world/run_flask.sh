#!/bin/bash


PORT=5001
FLASK_ENV=development
REBUILD_IMAGE=false

# Docker image and container names
IMAGE_NAME="flask-app"
CONTAINER_NAME="flask-container"
VERSION_NUMBER="1.0.0"

# Stop and remove the running container if it exists
if [ "$(docker ps -q -a -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping running container: $CONTAINER_NAME"
    docker stop $CONTAINER_NAME

    # Check if the stop was successful
    if [ $? -eq 0 ]; then
        echo "Removing container: $CONTAINER_NAME"
        docker rm $CONTAINER_NAME
    else
        echo "Failed to stop container: $CONTAINER_NAME"
        exit 1
    fi
else
    echo "No running container named $CONTAINER_NAME found."
fi

# Rebuild the image if rebuild_image is set to true
if [ "${REBUILD_IMAGE}" = true ]; then
    echo "Rebuilding Docker image: ${IMAGE_NAME}:${VERSION_NUMBER}"
    docker build -t "${IMAGE_NAME}:${VERSION_NUMBER}" .
else
    echo "Skipping image rebuild."
fi

docker run -d -p "${PORT}:${PORT}" \
    -e FLASK_ENV="$FLASK_ENV" \
    --name "$CONTAINER_NAME" \
    "${IMAGE_NAME}:${VERSION_NUMBER}"


# Output the status
if [ $? -eq 0 ]; then
    echo "Container $CONTAINER_NAME started successfully on port $PORT."
else
    echo "Failed to start container $CONTAINER_NAME."
fi