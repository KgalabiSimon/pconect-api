import psycopg2
from dotenv import load_dotenv
import os

# Clear any existing env vars
os.environ.pop('DB_PASSWORD', None)
os.environ.pop('DB_USER', None)
os.environ.pop('DB_HOST', None)
os.environ.pop('DB_NAME', None)
os.environ.pop('DB_PORT', None)

# Force reload of .env file
load_dotenv(override=True)

def test_connection():
    try:
        print("Testing database connection with these parameters:")
        print(f"Host: {os.getenv('DB_HOST')}")
        print(f"Database: {os.getenv('DB_NAME')}")
        print(f"User: {os.getenv('DB_USER')}")
        print(f"Port: {os.getenv('DB_PORT')}")
        # Print the actual password for verification
        print(f"Password from .env: {os.getenv('DB_PASSWORD')}")
        
        # Try connecting with just the username
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),  # Without @server
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', '5432'),
            sslmode='require'
        )
        
        # Test the connection
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()
        print("\n✅ Connection successful!")
        print(f"PostgreSQL version: {db_version[0]}")
        
    except Exception as e:
        print("\n❌ Connection failed!")
        print(f"Error: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    test_connection()