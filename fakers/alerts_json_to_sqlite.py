import json
import sqlite3

# Step 1: Read the JSON file
with open('alerts.json', 'r') as file:
    alerts = json.load(file)

# Step 2: Prepare the SQLite database
# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('alerts.db')
c = conn.cursor()

# Create table to store alerts
c.execute('''
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY,
    alertType TEXT,
    severity INTEGER,
    latitude REAL,
    longitude REAL,
    time TEXT,
    administrativeLevel INTEGER,
    details TEXT,
    caseValue REAL,
    caseUnit TEXT
)
''')

# Step 3: Insert data into the database
# Function to insert a JSON object into the SQLite table
def insert_alert(json_obj):
    c.execute('''
    INSERT INTO alerts (alertType, severity, latitude, longitude, time, administrativeLevel, details, caseValue, caseUnit)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        json_obj['alertType'],
        json_obj['severity'],
        json_obj['location']['latitude'],
        json_obj['location']['longitude'],
        json_obj['time'],
        json_obj['administrativeLevel'],
        json_obj['details'],
        json_obj['caseValue'],
        json_obj['caseUnit']
    ))

# Insert each object from the JSON array into the SQLite database
for obj in alerts:
    insert_alert(obj)

# Commit changes and close the connection to the database
conn.commit()
conn.close()

print("Alerts imported into SQLite database successfully.")
