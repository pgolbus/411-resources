# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy project files
COPY . /app
COPY .env /app/.env

# 🧩 Install curl and bash
RUN apt-get update && apt-get install -y curl bash sqlite3

# Install Python packages
RUN pip install -r requirements.txt

# Add shell script + DB init
COPY ./sql/create_db.sh /app/sql/create_db.sh
COPY ./sql/init_db.sql /app/sql/init_db.sql
RUN chmod +x /app/sql/create_db.sh

# Persist database
VOLUME ["/app/db"]

# Expose app port
EXPOSE 5000

# Entry point
CMD ["/app/entrypoint.sh"]
