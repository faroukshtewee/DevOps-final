# Use the official Python image from the Docker Hub
FROM mysql:8.0

# Set the working directory inside the container
WORKDIR /app/


# Copy the data.sql file into the container
COPY data.sql .

# Copy the import_data.sh file into the container
COPY import_data.sh .

# Command to run the application
CMD ["sh", "import_data.sh"]
