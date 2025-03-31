# Use the official lightweight Node.js 16 image.
# https://hub.docker.com/_/node
FROM node:16-slim

# Create and change to the app directory.
WORKDIR /usr/src/app

# Copy application dependency manifests to the container image.
# A wildcard is used to ensure both package.json AND package-lock.json are copied.
# Copying this separately prevents re-running npm install on every code change.
COPY package*.json ./

# Install production dependencies.
RUN npm install
RUN npm install axios

# Copy local code to the container image.
COPY . ./

# Inform Docker that the container listens on the specified port at runtime.
EXPOSE 3000

# Argument to accept environment variable at build time
ARG REACT_APP_FLASK_API

# Expose the environment variable to the application
ENV REACT_APP_FLASK_API=$REACT_APP_FLASK_API

# Build the React application.
RUN npm run build

# Serve the built application using a simple HTTP server
RUN npm install -g serve
CMD ["serve", "-s", "build", "-l", "3000"]