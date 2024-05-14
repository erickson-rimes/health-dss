import random

# Function to generate a random alert
def generate_alert(gdf, faker):
    severity = random.randint(0, 3)

    # Select a random row from the GDF
    random_row = gdf.sample(n=1).iloc[0]
    # Extract the coordinate
    coordinate = random_row['geometry'].representative_point()
    
    # Generate random data for the alert
    alert_type = random.choice(["Extreme Heat", "Extreme Cold", "Heat Stroke Cases", "Dengue Case", "Diarrhea Case"])
    location = {
        "latitude": coordinate.y,
        "longitude": coordinate.x
    }
    time = faker.date_time_between(start_date="-60d", end_date="now").isoformat()
    administrative_level = random.randint(0, 3)
    details = faker.sentence(nb_words=10)

    # generate case value based on alert type and severity
    if alert_type == "Extreme Heat":
        if severity == 0:
            case_value = random.uniform(20.0, 30.0)
        elif severity == 1:
            case_value = random.uniform(30.0, 40.0)
        elif severity == 2:
            case_value = random.uniform(40.0, 50.0)
        else:
            case_value = random.uniform(50.0, 60.0)
    else:
        if severity == 0:
            case_value = random.randint(1, 30)
        elif severity == 1:
            case_value = random.randint(31, 50)
        elif severity == 2:
            case_value = random.randint(51, 70)
        else:
            case_value = random.randint(71, 90)

    # case_value = random.randint(1, 100) if alert_type != "Extreme Heat" and alert_type != "Extreme Cold" else random.uniform(20.0, 45.0)
    
    
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
