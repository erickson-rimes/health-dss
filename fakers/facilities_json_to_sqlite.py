import json
import sqlite3

# Step 1: Read the JSON file
with open('facilities.json', 'r') as file:
    facilities = json.load(file)

# Step 2: Prepare the SQLite database
conn = sqlite3.connect('facilities.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS Address (
    id INTEGER PRIMARY KEY,
    addressLine TEXT,
    hamlet TEXT,
    suco TEXT,
    administrativePost TEXT,
    municipality TEXT,
    postalCode TEXT,
    latitude REAL,
    longitude REAL
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Facility (
    id TEXT PRIMARY KEY,
    facilityName TEXT,
    facilityType TEXT,
    addressId INTEGER,
    ownership TEXT,
    accreditationStatus BOOLEAN,
    serviceOfferings TEXT,
    operatingHours TEXT,
    FOREIGN KEY(addressId) REFERENCES Address(id)
)''')

# Step 3: Insert data into the database
for facility in facilities:
    # Insert address
    address = facility['address']
    cursor.execute('''
    INSERT INTO Address (addressLine, hamlet, suco, administrativePost, municipality, postalCode, latitude, longitude)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
        address['addressLine'],
        address.get('hamlet'),
        address.get('suco'),
        address['administrativePost'],
        address['municipality'],
        address['postalCode'],
        address['gpsCoordinates']['latitude'],
        address['gpsCoordinates']['longitude']
    ))
    address_id = cursor.lastrowid

    # Insert facility
    cursor.execute('''
    INSERT INTO Facility (id, facilityName, facilityType, addressId, ownership, accreditationStatus, serviceOfferings, operatingHours)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
        facility['facilityID'],
        facility['facilityName'],
        facility['facilityType'],
        address_id,
        facility['ownership'],
        facility['accreditationStatus'],
        json.dumps(facility['serviceOfferings']),
        facility['operatingHours']
    ))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Facilities and addresses imported into SQLite database successfully.")
