import random

# Function to generate a random alert
def generate_alert(gdf, faker):
    # Select a random row from the GDF
    random_row = gdf.sample(n=1).iloc[0]
    # Extract the coordinate
    coordinate = random_row['geometry'].representative_point()
    
    # Generate random data for the alert
    alert_type = random.choice(["Extreme Heat", "Extreme Cold", "Heat Stroke Cases", "Dengue Case", "Malaria Case"])
    severity = random.randint(0, 3)
    location = {
        "latitude": coordinate.y,
        "longitude": coordinate.x
    }
    time = faker.date_time_between(start_date="-60d", end_date="now").isoformat()
    administrative_level = random.randint(0, 3)
    details = faker.sentence(nb_words=10)
    case_value = random.randint(1, 100) if alert_type != "Extreme Heat" and alert_type != "Extreme Cold" else random.uniform(20.0, 45.0)
    case_unit = "Cases" if alert_type != "Extreme Heat" and alert_type != "Extreme Cold" else "°Celsius"
    
    # Construct the alert dictionary
    alert = {
        "alertType": alert_type,
        "severity": severity,
        "location": location,
        "time": time,
        "administrativeLevel": administrative_level,
        "details": details,
        "caseValue": case_value,
        "caseUnit": case_unit
    }
    
    return alert
