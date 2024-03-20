from faker import Faker
from case_report_generator import generate_case_report
import geopandas as gpd
import json

faker = Faker()
gdf = gpd.read_file('../shapefiles/tls_admbnda_adm3_who_ocha_20200911.shp')

print(gdf.head())

case_reports = []

# generate 1000 case_reports
for _ in range(1000):
    case_report = generate_case_report(gdf, faker)  # Assuming generate_address takes gdf and faker as inputs
    case_reports.append(case_report)

# save in a json file
with open('case_reports.json', 'w') as f:
    json.dump(case_reports, f, ensure_ascii=False, indent=4)

print("1000 case_reports generated and saved to case_reports.json")
