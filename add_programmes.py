import psycopg2
import os
from dotenv import load_dotenv
import uuid

load_dotenv(override=True)

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT", "5432"),
    sslmode='require',
    connect_timeout=10
)
cur = conn.cursor()

programme_names = [
    "programme A1",
    "programme A2",
    "programme 2",
    "programme 3",
    "programme 4",
    "programme 5"
]

for name in programme_names:
    cur.execute(
        "INSERT INTO programmes (id, name) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING;",
        (str(uuid.uuid4()), name)
    )

conn.commit()
print("✅ Programmes added.")
cur.close()
conn.close()
