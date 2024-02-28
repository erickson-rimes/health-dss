import random
import uuid
from address_generator import generate_address

def generate_facility(address, faker):
    facility_types = ["hospital", "clinic", "specialized_hospital", "primary_care_clinic", "diagnostic_lab", "other"]
    ownership_types = ["government", "private", "non_profit", "public_private_partnership"]
    service_offerings = ["emergency_services", "outpatient_services", "surgical_services", "diagnostic_services", "other"]
    update_frequency = ["daily", "weekly", "monthly", "annually", "as_needed"]

    facility = {
        "facilityName": faker.company() + ' ' + random.choice(['Hospital', 'Clinic', 'Lab']),
        "facilityType": random.choice(facility_types),
        "facilityID": str(uuid.uuid4()),
        "address": address,
        "ownership": random.choice(ownership_types),
        "accreditationStatus": random.choice([True, False]),
        "serviceOfferings": random.sample(service_offerings, random.randint(1, len(service_offerings))),
        "specialtyDepartments": [faker.word() for _ in range(random.randint(1, 5))],
        "operatingHours": "24/7" if random.choice([True, False]) else "9AM - 5PM",
        "healthcareProfessionals": {
            "doctors": random.randint(1, 100),
            "nurses": random.randint(1, 200),
            "technicians": random.randint(1, 50),
            "other": random.randint(1, 30)
        },
        "patientCapacity": {
            "outpatient": random.randint(10, 1000),
            "inpatient": random.randint(10, 500),
            "emergency": random.randint(5, 100)
        },
        "medicalEquipment": [faker.word() for _ in range(random.randint(1, 10))],
        "pharmacyServices": random.choice([True, False]),
        "insuranceAccepted": [faker.word() for _ in range(random.randint(1, 3))],
        "accessibilityFeatures": [faker.word() for _ in range(random.randint(1, 3))],
        "transportationAndParking": faker.sentence(),
        "emergencyServices": random.choice([True, False]),
        "technologyIntegration": random.choice([True, False]),
        "safetyAndQualityMetrics": faker.sentence(),
        "affiliations": [faker.word() for _ in range(random.randint(1, 3))],
        "communityOutreachPrograms": [faker.sentence() for _ in range(random.randint(1, 3))],
        "updateFrequency": random.choice(update_frequency)
    }

    return facility

# Example usage:
# Assuming you already have an 'address' from the 'generate_address' function
# address = generate_address(gdf, faker)
# facility = generate_facility(address, faker)
# print(facility)
