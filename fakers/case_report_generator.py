import random

def generate_case_report(gdf, faker):
    # Select a random row from the GDF
    random_row = gdf.sample(n=1).iloc[0]
    # Extract the coordinate
    coordinate = random_row['geometry'].representative_point()
    
    # Generate random data for the case report
    case_types = ["Heat Stroke", "Dengue Case", "Diarrhea Case"]
    reporting_entity_types = ["Individual", "Health Facility", "Automated System"]
    
    case_report = {
        "caseType": random.choice(case_types),
        "numberOfCases": random.randint(1, 100),
        "gpsCoordinates": {
            "latitude": coordinate.y,
            "longitude": coordinate.x
        },
        "from": faker.date_time_between(start_date="-365d", end_date="-335d").isoformat(),
        "to": faker.date_time_between(start_date="-334d", end_date="now").isoformat(),
        "reportingDate": faker.date_time_between(start_date="-334d", end_date="now").isoformat(),
        "reportingEntityType": random.choice(reporting_entity_types),
        "reportingEntityIdentifier": faker.bothify(text='???-######'),
        "administrativeLevel": random.choice([0, 1, 2, 3])
    }
    
    return case_report
