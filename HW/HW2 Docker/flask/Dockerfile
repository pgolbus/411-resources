# Use the official Ubuntu 22.04 LTS as the base image
FROM ubuntu:22.04

# Set the working directory inside the container
WORKDIR /app

# Update and install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*  # Clean up package list to reduce image size

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt || pip install flask

# Port 5000 is the default value for Flask apps
EXPOSE 5000

# Run app.py when the container launches
CMD ["python3", "app.py"]

#  Health check (checks every 30 seconds to ensure service is running)
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:5000/health || exit 1

