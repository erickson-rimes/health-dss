# from dataex_region_data_analysis.py  -mt ecmwf_hres -r tmax_daily_tmax_region -ai 14913390-cb22-433c-b291-d0888a0541c8 -uf ADM1_EN -of json -o tmax_daily_tmax_region_data.json

# -mt ecmwf_hres this is the type of data to be pulled
# -r tmax_daily_tmax_region is the weather parameter
# -ai 14913390-cb22-433c-b291-d0888a0541c8 is the asset identifier
# -uf ADM1_EN is the unique field
# -of is the output format
# -o is the output file

import json
import sqlite3
from datetime import datetime, timedelta
import argparse

# Municipality to ISO 3166-2 Code Mapping
municipality_codes = {
    "Aileu": "TL-AL",
    "Ainaro": "TL-AN",
    "Baucau": "TL-BA",
    "Bobonaro": "TL-BO",
    "Covalima": "TL-CO",
    "Dili": "TL-DI",
    "Ermera": "TL-ER",
    "Lautém": "TL-LA",
    "Liquiçá": "TL-LI",
    "Manatuto": "TL-MT",
    "Manufahi": "TL-MF",
    "Oecussi": "TL-OE",
    "Viqueque": "TL-VI"
}

def main(table_name):
    # Load the JSON data
    with open(f"{table_name}.json", 'r') as file:
        data = json.load(file)

    # Extract the forecast initialization date
    forecast_init = datetime.fromisoformat(data['fcst_init'].replace('Z', ''))

    # Initialize SQL connection (SQLite in this case)
    conn = sqlite3.connect('weather_forecast.db')
    cursor = conn.cursor()

    # Create the table (if not already created)
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        forecast_date DATE,
        day_name VARCHAR(20),
        value DECIMAL(5, 2),
        municipality_code VARCHAR(10),
        municipality_name VARCHAR(255)
    );
    ''')

    # Clear the table before inserting new data
    cursor.execute(f'DELETE FROM {table_name}')

    # Iterate over each municipality's forecast data
    for municipality, forecast_data in data['r_data'].items():
        municipality_code = municipality_codes.get(municipality, None)

        if municipality_code:
            # Iterate through the "value" entries
            for idx, value in enumerate(forecast_data['value']):
                # Get the forecast date
                forecast_date = forecast_init + timedelta(days=idx)
                day_name = forecast_date.strftime('%A')  # Get the day name
                
                # Insert into the SQL table
                cursor.execute(f'''
                    INSERT INTO {table_name} (forecast_date, day_name, value, municipality_code, municipality_name)
                    VALUES (?, ?, ?, ?, ?)
                ''', (forecast_date.date(), day_name, value, municipality_code, municipality))

    # Commit and close the connection
    conn.commit()
    conn.close()

    print(f"Data inserted into the {table_name} table successfully.")
    print(f"Total municipalities processed: {len(data['r_data'].items())}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Insert weather forecast data into a SQLite database.")
    parser.add_argument("table_name", help="Name of the table to insert data into")
    args = parser.parse_args()

    main(args.table_name)