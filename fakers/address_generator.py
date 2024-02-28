import random

def generate_postal_code(ADM3_PCODE):
    # Assuming that the postal code system follows a similar structure to the P-code, 
    # or is derived from it, we can use the last 5 digits of the P-code as the postal code.
    # If the P-code is not numeric or does not contain enough digits, generate a random 5-digit number.
    if ADM3_PCODE.isdigit() and len(ADM3_PCODE) >= 5:
        return ADM3_PCODE[-5:]
    else:
        return '{:05d}'.format(random.randint(0, 99999))

def generate_address(gdf, faker):
    # Randomly select a row from the GeoDataFrame
    random_row = gdf.sample(1).iloc[0]

    # Generate random street address and postal code
    address_line = faker.street_address()
    postal_code = generate_postal_code(random_row['ADM3_PCODE'])

    # Extract municipality, sub-district, and village
    municipality = random_row['ADM1_EN']
    sub_district = random_row['ADM2_EN']
    village = random_row['ADM3_EN']

    # Extract latitude and longitude from the geometry
    point = random_row['geometry'].representative_point()
    latitude = point.y
    longitude = point.x

    address = {
        "addressLine": address_line,
        "hamlet": None,  # No data available for hamlets
        "village": village,
        "subDistrict": sub_district,
        "municipality": municipality,
        "postalCode": postal_code,
        "gpsCoordinates": {
            "latitude": latitude,
            "longitude": longitude
        }
    }

    return address

# Usage example
# Load the GeoDataFrame with the shapefile data first
# gdf = gpd.read_file('../shapefiles/tls_admbnda_adm3_who_ocha_20200911.shp')

# # Then generate an address
# address = generate_address(gdf)
# print(address)
