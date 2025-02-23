import psycopg2

DB_NAME = "eaglehacks_2025"
DB_USER = "eaglehacks_2025"
DB_PASSWORD = "password"
DB_HOST = "localhost" 

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port="5432"
    )
    cur = conn.cursor()
    
    cur.execute("SELECT inet_server_addr();")
    ip_address = cur.fetchone()[0]
    
    print(f"✅ Connected to PostgreSQL running at {ip_address}")

    cur.close()
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)
