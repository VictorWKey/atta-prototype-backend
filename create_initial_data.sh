#!/bin/bash

# Function to wait for database
wait_for_database() {
    echo "Waiting for database to be ready..."
    
    # Wait for postgres to be reachable
    until pg_isready -h postgres -p 5432 -U atta_user; do
        echo "Database is unavailable - sleeping..."
        sleep 2
    done
    
    echo "Database is ready!"
}

# Install pg_isready if not available
if ! command -v pg_isready &> /dev/null; then
    echo "Installing postgresql-client..."
    apt-get update && apt-get install -y postgresql-client
fi

# Wait for database
wait_for_database

# Run initial data creation
echo "Creating initial data..."
python create_initial_data.py

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
