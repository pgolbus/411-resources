# Use the official Ubuntu 22.04 image as the base
FROM ubuntu:22.04

# Set the working directory inside the container
WORKDIR /app

# Update and install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

# Copy the Flask app files into the container
COPY . /app

# Install Flask
RUN pip3 install flask

# Expose the port that the Flask app will run on
EXPOSE 5000

# Set the entry point command to run the Flask app
CMD ["python3", "app.py"]

# Add a health check to monitor the application
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl --fail http://localhost:5000/health || exit 1

