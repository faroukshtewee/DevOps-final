# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for MySQL, Chromium, and libraries for Chrome to work
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    python3-dev \
    chromium \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the environment variable for Chrome binary location
ENV CHROME_BIN=/usr/bin/chromium

RUN apt-get update && apt-get install -y chromium
RUN apt-get update && apt-get install -y libgdk-pixbuf2.0-0

# Copy the requirements file into the container
COPY requirement.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirement.txt

# Copy the entire project into the container
COPY . .

# Expose the port on which your exercises_app runs (default is 8000 for Django)
EXPOSE 8000

# Command to run the application
CMD ["sh", "start_django.sh"]