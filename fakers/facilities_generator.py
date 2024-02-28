from faker import Faker
from address_generator import generate_address
from facility_generator import generate_facility
import geopandas as gpd
import json

faker = Faker()
gdf = gpd.read_file('../shapefiles/tls_admbnda_adm3_who_ocha_20200911.shp')

facilities = []

# generate 1000 facilities
for _ in range(1000):
    address = generate_address(gdf, faker)  # Assuming generate_address takes gdf and faker as inputs
    facility = generate_facility(address, faker)  # Assuming generate_facility takes an address and faker as inputs
    facilities.append(facility)

# save in a json file
with open('facilities.json', 'w') as f:
    json.dump(facilities, f, ensure_ascii=False, indent=4)

print("1000 facilities generated and saved to facilities.json")
