#!/bin/bash
DIRECTORY=./shared
DONE_FILE_NAME=migration.done

if [ !  -d "$DIRECTORY" ]; then
  echo "create $DIRECTORY "
  mkdir $DIRECTORY
fi
echo "crcheck if $DIRECTORY/$DONE_FILE_NAME  exists "
if  [ ! -f  $DIRECTORY/$DONE_FILE_NAME ]; then
    echo "Start mysql db migration"
    mysql -h db -p$SQL_ROOT_PASSWORD  < data.sql
    touch $DIRECTORY/$DONE_FILE_NAME
fi