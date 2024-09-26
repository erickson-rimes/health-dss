import json
from datetime import datetime, timedelta
import pandas as pd

administrative_posts = [
    "Aileu", # Weekly
    # "Ainaro", # Mix of Monthly (2018 - 2024 with Dengue in Yearly) and Yearly (2013-2017)
    "Atauro", # Weekly
    "Baucau", # Weekly
    "Bobonaro", # Weekly
    # "Covalima", # Weekly, except Diarrhea which is yearly
    "Dili", # Weekly
    "Ermera", # Weekly
    # "Manatuto", # Yearly
    # "Manufahi", # Yearly
    # "Lautem", # Weekly, except Dengue which is yearly
    "Liquica", # Weekly
    # "Raeoa", # Monthly
    "Viqueque", # Weekly
]

administrative_posts_coordinates = {
    "Aileu": (-8.728057, 125.566077),
    "Ainaro": (-8.992432, 125.507534),
    "Atauro": (-8.277722, 125.590804),
    "Baucau": (-8.477936, 126.456318),
    "Bobonaro": (-9.000972, 125.325223),
    "Covalima": (-9.190680, 125.290179),
    "Dili": (-8.556855, 125.560314),
    "Ermera": (-8.749852, 125.396348),
    "Manatuto": (-8.511463, 126.015081),
    "Manufahi": (-9.003858, 125.877233),
    "Lautem": (-8.362167, 127.000200),
    "Liquica": (-8.587984, 125.341889),
    "Raeoa": (-8.424840, 126.884851),
    "Viqueque": (-8.859217, 126.364231)
}

def get_coordinates_for_post(administrative_post):
    """
    Returns the latitude and longitude for a given administrative post.
    
    :param administrative_post: The name of the administrative post (str)
    :return: Tuple containing (latitude, longitude) or (None, None) if not found
    """
    # Normalize the input to lower case for case-insensitive matching
    normalized_post = administrative_post.strip().lower()

    # Iterate through the dictionary and find the match
    for post, coordinates in administrative_posts_coordinates.items():
        if post.lower() == normalized_post:
            return coordinates
    
    # Return None if the post is not found
    return None, None

def get_monday_and_sunday(year, week):
    """
    Returns the datetime of the Monday and Sunday of a given year and week number.

    :param year: The year (int)
    :param week: The week number (int)
    :return: Tuple containing (monday_datetime, sunday_datetime)
    """
    # Start with the first day of the year
    first_day_of_year = datetime(year=year, month=1, day=1)
    
    # Find the first Monday of the year
    days_to_first_monday = (7 - first_day_of_year.weekday()) % 7
    first_monday = first_day_of_year + timedelta(days=days_to_first_monday)
    
    # Calculate the Monday of the given week
    monday_of_week = first_monday + timedelta(weeks=week - 1)
    
    # Sunday is 6 days after the Monday
    sunday_of_week = monday_of_week + timedelta(days=6)
    
    return monday_of_week, sunday_of_week

# Initialize a list to hold the resulting JSON objects
json_list = []


for administrative_post in administrative_posts:
    print(f"processing {administrative_post}")
    file_path = f"./data/{administrative_post}.xlsx"
    data = pd.read_excel(file_path, sheet_name=None, header=0)[administrative_post]

    ari_column_name = 'ARI' if 'ARI' in data.columns else 'ISPA'

    # Assert the existence of 'Year', 'Week', 'Dengue', 'ARI', and 'Diarrhea' columns, print the column name if it does not exist and return an error
    required_columns = ['Year', 'Week', 'Dengue', ari_column_name, 'Diarrhea']
    missing_columns = [column for column in required_columns if column not in data.columns]

    if missing_columns:
        for column in missing_columns:
            print(f"Missing column: {column}")
        print(f"Required columns are missing for {administrative_post}")
        continue

    coordinates = get_coordinates_for_post(administrative_post)

    # Iterate through the rows of the DataFrame
    for index, row in data.iterrows():
        # print(index)
        # If week is missing, skip row
        if pd.isnull(row['Week']):
            continue

        # If year is missing, assume previous year
        if pd.isnull(row['Year']):
            year = previous_year
        else:
            year = row['Year']
            previous_year = row['Year']

        week = row['Week']
        week = int(week)
        year = int(year)

        # Get Dengue Cases
        dengue_cases = int(row['Dengue']) if not pd.isnull(row['Dengue']) else None
        ari_cases = int(row[ari_column_name]) if not pd.isnull(row[ari_column_name]) else None
        diarrhea_cases = int(row['Diarrhea']) if not pd.isnull(row['Diarrhea']) else None
        
        # Calculate the reporting date for the week
        monday, sunday = get_monday_and_sunday(year, week)

        # Prepare the JSON object
        case_entries = [{
            "caseType": "Dengue Case",
            "numberOfCases": dengue_cases,
            "gpsCoordinates": coordinates,
            "weekNumber": week,
            "from": monday.isoformat(),  # No data for these fields, so set as None
            "to": sunday.isoformat(),
            "reportingDate": sunday.isoformat(),
            "reportingEntityType": "Automated System",  # Set to null due to missing information
            "sexGroupMaleCases": None,
            "sexGroupFemaleCases": None,
            "sexGroupUnknownCases": None,
            "ageGroup0To4Cases": None,
            "ageGroup5To18Cases": None,
            "ageGroup19To59Cases": None,
            "ageGroup60PlusCases": None,
            "ageGroupUnknownCases": None,
            "reportingEntityIdentifier": None,
            "administrativeLevel": 1  # Assuming all cases are from level 1 for consistency
        },
        {
            "caseType": "ARI Case",
            "numberOfCases": ari_cases,
            "gpsCoordinates": coordinates,
            "weekNumber": week,
            "from": monday.isoformat(),  # No data for these fields, so set as None
            "to": sunday.isoformat(),
            "reportingDate": sunday.isoformat(),
            "reportingEntityType": "Automated System",  # Set to null due to missing information
            "sexGroupMaleCases": None,
            "sexGroupFemaleCases": None,
            "sexGroupUnknownCases": None,
            "ageGroup0To4Cases": None,
            "ageGroup5To18Cases": None,
            "ageGroup19To59Cases": None,
            "ageGroup60PlusCases": None,
            "ageGroupUnknownCases": None,
            "reportingEntityIdentifier": None,
            "administrativeLevel": 1  # Assuming all cases are from level 1 for consistency
        },
        {
            "caseType": "Diarrhea Case",
            "numberOfCases": diarrhea_cases,
            "gpsCoordinates": coordinates,
            "weekNumber": week,
            "from": monday.isoformat(),  # No data for these fields, so set as None
            "to": sunday.isoformat(),
            "reportingDate": sunday.isoformat(),
            "reportingEntityType": "Automated System",  # Set to null due to missing information
            "sexGroupMaleCases": None,
            "sexGroupFemaleCases": None,
            "sexGroupUnknownCases": None,
            "ageGroup0To4Cases": None,
            "ageGroup5To18Cases": None,
            "ageGroup19To59Cases": None,
            "ageGroup60PlusCases": None,
            "ageGroupUnknownCases": None,
            "reportingEntityIdentifier": None,
            "administrativeLevel": 1  # Assuming all cases are from level 1 for consistency
        }
        ]
        
        json_list.extend(case_entries)

    # Save json to a {administrativePost}_cases.json file
    output_file_path = f"./data/{administrative_post}_cases.json"
    with open(output_file_path, 'w') as output_file:
        json.dump(json_list, output_file)
