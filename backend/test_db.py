from database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM firms_observations;")

count = cursor.fetchone()[0]

print("FIRMS records in database:", count)

cursor.close()
conn.close()