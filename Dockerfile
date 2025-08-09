FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app

# Create uploads directory
RUN mkdir -p /uploads

# Create initialization script
COPY create_initial_data.sh /create_initial_data.sh
RUN chmod +x /create_initial_data.sh

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["/create_initial_data.sh"]
