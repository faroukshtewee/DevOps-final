import environ
import mysql.connector
import os


env = environ.Env()

current_dir = os.path.dirname(os.path.abspath(__file__))
print(f'current_dir-----{current_dir}')

env_path = os.path.join(current_dir, ".env")
print(f'env_path-----{env_path}')

# Load environment variables
environ.Env.read_env(env_path)




def get_db_connection(func_name):
    """Establish and return a MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host=env("SQL_HOST"),
            user=env("SQL_USER"),
            password=env("SQL_PASSWORD"),
            database=env("SQL_DATABASE"),
            port=env.int("SQL_PORT", default=3306)
        )
        if connection.is_connected():
            print(f"Database connection successful --- function:{func_name}")
            return connection
        else:
            print(f"Database connection failed! --- function:{func_name}")
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
