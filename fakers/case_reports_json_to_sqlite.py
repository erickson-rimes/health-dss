import json
import sqlite3

# Step 1: Read the JSON file with case reports
with open('case_reports.json', 'r') as file:
    case_reports = json.load(file)

# Step 2: Prepare the SQLite database for case reports
conn = sqlite3.connect('case_reports.db')
c = conn.cursor()

# Create table to store case reports
c.execute('''
CREATE TABLE IF NOT EXISTS case_reports (
    id INTEGER PRIMARY KEY,
    caseType TEXT,
    numberOfCases INTEGER,
    latitude REAL,
    longitude REAL,
    fromDateTime TEXT,
    toDateTime TEXT,
    reportingDate TEXT,
    reportingEntityType TEXT,
    reportingEntityIdentifier TEXT,
    administrativeLevel INTEGER
)
''')

# Step 3: Insert data into the database
# Function to insert a case report JSON object into the SQLite table
def insert_case_report(json_obj):
    c.execute('''
    INSERT INTO case_reports (caseType, numberOfCases, latitude, longitude, fromDateTime, toDateTime, reportingDate, reportingEntityType, reportingEntityIdentifier, administrativeLevel)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        json_obj['caseType'],
        json_obj['numberOfCases'],
        json_obj['gpsCoordinates']['latitude'],
        json_obj['gpsCoordinates']['longitude'],
        json_obj['from'],
        json_obj['to'],
        json_obj['reportingDate'],
        json_obj['reportingEntityType'],
        json_obj['reportingEntityIdentifier'],
        json_obj['administrativeLevel']
    ))

# Insert each object from the JSON array into the SQLite database
for obj in case_reports:
    insert_case_report(obj)

# Commit changes and close the connection to the database
conn.commit()
conn.close()

print("Case reports imported into SQLite database successfully.")
