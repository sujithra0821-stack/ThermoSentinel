from database import get_connection

conn = get_connection()
cursor = conn.cursor()

query = """
SELECT
    a.latitude,
    a.longitude,
    COUNT(DISTINCT b.acq_date) AS previous_days
FROM firms_observations a
JOIN firms_observations b
    ON b.acq_date < a.acq_date
    AND b.acq_date >= a.acq_date - INTERVAL '7 days'
    AND ST_DWithin(
        a.geom::geography,
        b.geom::geography,
        1000
    )
GROUP BY
    a.latitude,
    a.longitude
HAVING COUNT(DISTINCT b.acq_date) >= 2
ORDER BY previous_days DESC
LIMIT 5;
"""

cursor.execute(query)

results = cursor.fetchall()

for row in results:
    print(row)

cursor.close()
conn.close()