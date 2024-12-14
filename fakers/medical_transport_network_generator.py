import sqlite3
import random
import sys
from datetime import datetime, timedelta
import faker

# Initialize Faker instance for generating random names, addresses, and phone numbers
fake = faker.Faker()

# Initialize SQLite database connection
conn = sqlite3.connect('medical_transport.db')  # Change to a file path for a persistent DB
cursor = conn.cursor()

# Create the `vehicles` table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        vehicle_id INTEGER PRIMARY KEY,
        vehicle_type TEXT CHECK(vehicle_type IN ('Ambulance', 'Rescue Vehicle')),
        transport_mode TEXT CHECK(transport_mode IN ('Land', 'Maritime', 'Air')),
        status TEXT CHECK(status IN ('Available', 'In Use', 'Under Maintenance')),
        address TEXT,
        contact_name TEXT,
        contact_phone TEXT,
        last_update_time TEXT,
        organization_id INTEGER,
        FOREIGN KEY (organization_id) REFERENCES organizations (organization_id)
    )
''')

# Create the `organizations` table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS organizations (
        organization_id INTEGER PRIMARY KEY,
        organization_name TEXT,
        iso_3166_2_code TEXT,
        contact_email TEXT,
        contact_phone TEXT
    )
''')

# Function to generate m mock organizations
def generate_mock_organizations(m):
    organizations_data = []
    iso_3166_2_codes = ['TL-AL', 'TL-AN', 'TL-BA', 'TL-BO', 'TL-CO', 'TL-DI', 'TL-ER', 'TL-LA', 'TL-LI', 'TL-MF', 'TL-MT', 'TL-OE', 'TL-VI']
    for i in range(1, m+1):
        organization_name = f'{fake.company()}'
        iso_3166_2_code = random.choice(iso_3166_2_codes)
        contact_email = fake.email()
        contact_phone = fake.phone_number()
        organizations_data.append((i, organization_name, iso_3166_2_code, contact_email, contact_phone))
    return organizations_data

# Function to generate n mock vehicles
def generate_mock_vehicles(n, org_count):
    vehicles_data = []
    vehicle_types = ['Ambulance', 'Rescue Vehicle']
    transport_modes = ['Land', 'Maritime', 'Air']
    statuses = ['Available', 'In Use', 'Under Maintenance']
    
    for i in range(1, n+1):
        vehicle_type = random.choice(vehicle_types)
        transport_mode = random.choice(transport_modes)
        status = random.choice(statuses)
        address = fake.address()
        contact_name = fake.name()
        contact_phone = fake.phone_number()
        last_update_time = (datetime.now() - timedelta(days=random.randint(0, 10))).strftime('%Y-%m-%d %H:%M:%S')
        organization_id = random.randint(1, org_count)
        vehicles_data.append((i, vehicle_type, transport_mode, status, address, contact_name, contact_phone, last_update_time, organization_id))
    return vehicles_data

# Function to populate the database with n vehicles and m organizations
def populate_mock_data(n, m):
    # Generate and insert organizations
    organizations_data = generate_mock_organizations(m)
    cursor.executemany('''
        INSERT INTO organizations (organization_id, organization_name, iso_3166_2_code, contact_email, contact_phone)
        VALUES (?, ?, ?, ?, ?)
    ''', organizations_data)
    
    # Generate and insert vehicles
    vehicles_data = generate_mock_vehicles(n, len(organizations_data))
    cursor.executemany('''
        INSERT INTO vehicles (vehicle_id, vehicle_type, transport_mode, status, address, contact_name, contact_phone, last_update_time, organization_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', vehicles_data)

    # Commit the changes
    conn.commit()

# Main entry point for the script
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_mock_data.py <number_of_vehicles> <number_of_organizations>")
        sys.exit(1)

    n = int(sys.argv[1])  # Number of vehicles
    m = int(sys.argv[2])  # Number of organizations
    
    populate_mock_data(n, m)

    # Fetch and display inserted data for validation
    cursor.execute('SELECT * FROM vehicles')
    vehicles_result = cursor.fetchall()

    cursor.execute('SELECT * FROM organizations')
    organizations_result = cursor.fetchall()

    # Display the results
    print("\nVehicles Data:")
    for row in vehicles_result:
        print(row)

    print("\nOrganizations Data:")
    for row in organizations_result:
        print(row)

    # Close the connection
    conn.close()