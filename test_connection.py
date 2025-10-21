import psycopg2
from urllib.parse import quote_plus
import os
import socket
from dotenv import load_dotenv

# Force reload of .env file
os.environ.pop('DB_PASSWORD', None)
os.environ.pop('DB_USER', None)
os.environ.pop('DB_HOST', None)
os.environ.pop('DB_NAME', None)
os.environ.pop('DB_PORT', None)
load_dotenv(override=True)

# Get the environment variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

print("\nDatabase Configuration:")
print(f"Host: {DB_HOST}")
print(f"Database: {DB_NAME}")
print(f"User: {DB_USER}")
print(f"Port: {DB_PORT}")

print("\nDNS Resolution Test:")
try:
    print(f"Resolving {DB_HOST}...")
    ip_address = socket.gethostbyname(DB_HOST)
    print(f"✅ DNS Resolution successful: {ip_address}")
except socket.gaierror as e:
    print(f"❌ DNS Resolution failed: {str(e)}")
    print("This might be due to:")
    print("1. No internet connection")
    print("2. DNS server issues")
    print("3. Incorrect hostname")
    print("4. Firewall blocking DNS resolution")

print("\nDatabase Connection Test:")
try:
    print("Attempting database connection...")
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        sslmode='require',
        connect_timeout=10
    )
    
    cursor = connection.cursor()
    cursor.execute('SELECT version();')
    db_version = cursor.fetchone()
    print("✅ Connected successfully!")
    print(f"PostgreSQL version: {db_version[0]}")
    
except psycopg2.OperationalError as e:
    print("❌ Connection failed!")
    print(f"Error: {str(e)}")
    print("\nPossible issues:")
    print("1. Network connectivity to port 5432")
    print("2. Firewall blocking database access")
    print("3. Invalid credentials")
    print("4. Database server is down")
    
except Exception as e:
    print("❌ Unexpected error!")
    print(f"Error: {str(e)}")
    
finally:
    if 'connection' in locals():
        cursor.close()
        connection.close()
        print("\nConnection closed.")