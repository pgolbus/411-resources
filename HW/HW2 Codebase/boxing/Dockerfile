# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the env file to the container
COPY .env /app/.env

# Use port 5002 to host app.
ENV PORT=5002

# Install any needed packages specified in requirements.txt
# In production, you would want to ensure that any re-compiled packages
# With the same version number are re-downloaded
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# Install SQLite3
RUN apt-get update && apt-get install -y sqlite3

# Add a shell script that loads the .env file and handles database creation
COPY ./sql/create_db.sh /app/sql/create_db.sh
COPY ./sql/init_db.sql /app/sql/init_db.sql
RUN chmod +x /app/sql/create_db.sh

# Define a volume for persisting the database
VOLUME ["/app/boxing_db..."]

# Expose port 5002 to container
EXPOSE $PORT

# Run the entrypoint script when the container launches
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

HEALTHCHECK --interval=30s --timeout=3s \
CMD curl -f http://localhost:${PORT}/health || exit 1
