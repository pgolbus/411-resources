import sqlite3

conn = sqlite3.connect("boxing.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS boxers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    weight REAL NOT NULL,
    height REAL NOT NULL,
    reach REAL NOT NULL,
    age INTEGER NOT NULL,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()

print("✅ Initialized boxing.db with boxers table.")
