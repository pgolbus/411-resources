#!/bin/bash

# Define the database path
DB_PATH="./db/boxer.db"

# Check if the database file already exists
if [ -f "$DB_PATH" ]; then
    echo "Recreating database at $DB_PATH."
    # Drop and recreate the tables
    sqlite3 "$DB_PATH" < ./sql/init_db.sql
    echo "Database recreated successfully."
else
    echo "Creating database at $DB_PATH."
    # Create the database for the first time
    sqlite3 "$DB_PATH" < ./sql/init_db.sql
    echo "Database created successfully."
fi
