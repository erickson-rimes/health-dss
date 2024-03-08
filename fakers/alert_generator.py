import geopandas as gpd
import random
from faker import Faker
from datetime import datetime

# Assuming you have a GDF loaded, if not, load it. For example:
# gdf = gpd.read_file('your_file.geojson')

# Initialize Faker
# faker = Faker()

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

# Example usage
# gdf = gpd.read_file('your_geojson_file_path.geojson')  # Update this path to your GDF file
# random_alert = generate_random_alert(gdf)
# print(random_alert)
