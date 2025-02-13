# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.lock

# Make port 5000 available to the world outside this container
ENV PORT=5002
EXPOSE $PORT

# Define environment variable
ENV FLASK_DEBUG=1

# Run app.py when the container launches

CMD ["flask", "run", "--host=0.0.0.0", "--port=5002"]


# Health check (checks every 30 seconds to see if the endpoint 
# returns a successful response)

HEALTHCHECK --interval=30s --timeout=3s \

CMD curl -f http://localhost:${PORT}/healthcheck || exit 1