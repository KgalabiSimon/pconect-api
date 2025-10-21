import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Get current credentials from .env
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "5432")

# New password
NEW_PASSWORD = "TshepoK@2025"  # You can change this to your desired password

try:
    # Connect with current credentials
    print(f"Connecting to {DB_HOST} as {DB_USER}...")
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        sslmode='require'
    )
    conn.autocommit = True

    # Create a cursor
    cur = conn.cursor()
    
    # Change the password
    print("Changing password...")
    escaped_password = NEW_PASSWORD.replace("'", "''")
    cur.execute(f"ALTER USER {DB_USER} WITH PASSWORD '{escaped_password}'")
    
    print("Password changed successfully!")
    print("\nNow update your .env file with the new password:")
    print(f"DB_PASSWORD={NEW_PASSWORD}")
    
except Exception as e:
    print(f"Error changing password: {str(e)}")
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()