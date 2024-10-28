# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Ensure pip is up to date
RUN pip install --upgrade pip

# Install any necessary dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.lock

# Set default environment variables for port and Flask environment
ENV FLASK_ENV=development
ENV FLASK_PORT=5000

# Expose the default port, but this can be overridden
EXPOSE ${FLASK_PORT}

# Run the Flask app using environment variables for host, port, and mode
CMD ["flask", "run", "--host=0.0.0.0", "--port=${FLASK_PORT}"]