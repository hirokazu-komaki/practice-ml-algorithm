import sqlite3
import os

conn = sqlite3.connect('reviews.sqlite')
c = conn.cursor()
c.execute("SELECT * FROM review_db WHERE date"\
          " BETWEEN '2022-08-05 00:00:00' AND DATETIME('now')")
results = c.fetchall()
conn.close()
print(results)