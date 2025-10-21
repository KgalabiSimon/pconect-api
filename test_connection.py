import psycopg2
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

load_dotenv()

# Get the environment variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

print(f"Testing connection to: {DB_HOST}")
print(f"Database: {DB_NAME}")
print(f"User: {DB_USER}")

try:
    # Construct connection string
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        sslmode='require'
    )
    
    # Create a cursor
    cursor = connection.cursor()
    
    # Test the connection
    cursor.execute('SELECT version();')
    db_version = cursor.fetchone()
    print("Connected successfully!")
    print(f"PostgreSQL version: {db_version[0]}")
    
except Exception as e:
    print("Connection failed!")
    print(f"Error: {str(e)}")
    
finally:
    if 'connection' in locals():
        cursor.close()
        connection.close()
        print("Connection closed.")