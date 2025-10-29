import psycopg2,os

# Replace with your actual connection details
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# Find all schemas with 'spacetype' ENUM
enum_query = '''
SELECT n.nspname as enum_schema, t.typname as enum_name
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
WHERE t.typname = 'spacetype';
'''
cur.execute(enum_query)
results = cur.fetchall()

if not results:
    print("No 'spacetype' ENUM found in any schema.")
else:
    for schema, enum_name in results:
        drop_sql = f"DROP TYPE IF EXISTS {schema}.spacetype CASCADE;"
        print(f"Dropping: {drop_sql}")
        cur.execute(drop_sql)
    conn.commit()
    print("Dropped all 'spacetype' ENUMs found.")

# Also drop 'bookingstatus' ENUM from all schemas
booking_enum_query = '''
SELECT n.nspname as enum_schema, t.typname as enum_name
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
WHERE t.typname = 'bookingstatus';
'''
cur.execute(booking_enum_query)
results = cur.fetchall()

if not results:
    print("No 'bookingstatus' ENUM found in any schema.")
else:
    for schema, enum_name in results:
        drop_sql = f"DROP TYPE IF EXISTS {schema}.bookingstatus CASCADE;"
        print(f"Dropping: {drop_sql}")
        cur.execute(drop_sql)
    conn.commit()
    print("Dropped all 'bookingstatus' ENUMs found.")

# Also drop 'checkinstatus' ENUM from all schemas
checkin_enum_query = '''
SELECT n.nspname as enum_schema, t.typname as enum_name
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
WHERE t.typname = 'checkinstatus';
'''
cur.execute(checkin_enum_query)
results = cur.fetchall()

if not results:
    print("No 'checkinstatus' ENUM found in any schema.")
else:
    for schema, enum_name in results:
        drop_sql = f"DROP TYPE IF EXISTS {schema}.checkinstatus CASCADE;"
        print(f"Dropping: {drop_sql}")
        cur.execute(drop_sql)
    conn.commit()
    print("Dropped all 'checkinstatus' ENUMs found.")

# Also drop 'usertype' ENUM from all schemas
usertype_enum_query = '''
SELECT n.nspname as enum_schema, t.typname as enum_name
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
WHERE t.typname = 'usertype';
'''
cur.execute(usertype_enum_query)
results = cur.fetchall()

if not results:
    print("No 'usertype' ENUM found in any schema.")
else:
    for schema, enum_name in results:
        drop_sql = f"DROP TYPE IF EXISTS {schema}.usertype CASCADE;"
        print(f"Dropping: {drop_sql}")
        cur.execute(drop_sql)
    conn.commit()
    print("Dropped all 'usertype' ENUMs found.")

cur.close()
conn.close()
