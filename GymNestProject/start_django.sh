
# Check if DATABASE is set to MySQL
if [ "$DATABASE" = "mysql" ]; then
    echo "Waiting for MySQL to start..."

    # Wait until the MySQL service is available
    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done

    echo "MySQL started"
fi

# Apply migrations
echo "Checking and applying database migrations..."
python manage.py makemigrations
# Check for pending migrations before running them
if python manage.py showmigrations | grep '\[ \]' > /dev/null; then
    python manage.py migrate
else
    echo "No migrations to apply."
fi

echo "Import Images From AWS..."
python -m exercisesApp.utils.aws_s3

# Start the Django development server
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000

# Execute any additional commands passed to the script
exec "$@"
