# Use the official Ubuntu 22.04 LTS as the base image
FROM ubuntu:22.04

# Set the working directory inside the container
WORKDIR /app

# Update and install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flask

# Set the environment variable for the port
ENV PORT=5002
# Expose the port to the outside world
EXPOSE $PORT

# Health check (checks every 30 seconds to see if the endpoint returns a successful response)
HEALTHCHECK --interval=30s --timeout=3s \
CMD curl -f http://localhost:${PORT}/healthcheck || exit 1

# Run app.py when the container launches
CMD ["python3", "app.py"]

