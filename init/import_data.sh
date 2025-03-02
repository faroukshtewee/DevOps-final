#!/bin/bash
DIRECTORY=./shared
DONE_FILE_NAME=migration.done

# Ensure directory exists
if [ ! -d "$DIRECTORY" ]; then
  echo "Creating directory: $DIRECTORY"
  mkdir -p "$DIRECTORY"
fi

# Check if migration has already been done
echo "Checking if $DIRECTORY/$DONE_FILE_NAME exists"
if [ ! -f "$DIRECTORY/$DONE_FILE_NAME" ]; then
    echo "Start MySQL DB migration"
    mysql -h 172.20.167.246 -u root -p"$SQL_ROOT_PASSWORD" < data.sql
    touch "$DIRECTORY/$DONE_FILE_NAME"
else
    echo "Migration done file does not exist."
fi
