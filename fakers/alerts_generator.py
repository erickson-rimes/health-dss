from faker import Faker
from alert_generator import generate_alert
import geopandas as gpd
import json

faker = Faker()
gdf = gpd.read_file('../shapefiles/tls_admbnda_adm3_who_ocha_20200911.shp')

alerts = []

# generate 1000 alerts
for _ in range(1000):
    alert = generate_alert(gdf, faker)  # Assuming generate_address takes gdf and faker as inputs
    alerts.append(alert)

# save in a json file
with open('alerts.json', 'w') as f:
    json.dump(alerts, f, ensure_ascii=False, indent=4)

print("1000 alerts generated and saved to alerts.json")
