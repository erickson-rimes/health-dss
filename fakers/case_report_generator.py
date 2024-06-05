import random

def generate_case_report(gdf, faker):
    # Select a random row from the GDF
    random_row = gdf.sample(n=1).iloc[0]
    # Extract the coordinate
    coordinate = random_row['geometry'].representative_point()
    
    # Generate random data for the case report
    case_types = ["Heat Stroke", "Dengue Case", "Diarrhea Case"]
    reporting_entity_types = ["Individual", "Health Facility", "Automated System"]
    number_of_cases = random.randint(1, 100)
    male_cases = random.randint(0, number_of_cases)
    female_cases = random.randint(0, number_of_cases - male_cases)
    unknown_cases = number_of_cases - (male_cases + female_cases)

    age_group_0_to_4_cases = random.randint(0, number_of_cases)
    age_group_5_to_18_cases = random.randint(0, number_of_cases - age_group_0_to_4_cases)
    age_group_19_to_58_cases = random.randint(0, number_of_cases - (age_group_0_to_4_cases + age_group_5_to_18_cases))
    age_group_60_plus_cases = random.randint(0, (number_of_cases - (age_group_0_to_4_cases + age_group_5_to_18_cases + age_group_19_to_58_cases)))
    age_group_unknown_cases = number_of_cases - (age_group_0_to_4_cases + age_group_5_to_18_cases + age_group_19_to_58_cases + age_group_60_plus_cases)

    from_date = faker.date_time_between(start_date="-365d", end_date="now")
    from_date_string = from_date.isoformat()

    # to_date must be after from_date
    to_date = faker.date_time_between(start_date=from_date, end_date="-7d")
    to_date_string = to_date.isoformat()

    reporting_date = faker.date_time_between(start_date=to_date, end_date="now")
    reporting_date_string = reporting_date.isoformat()
    
    case_report = {
        "caseType": random.choice(case_types),
        "numberOfCases": number_of_cases,
        "gpsCoordinates": {
            "latitude": coordinate.y,
            "longitude": coordinate.x
        },
        "from": from_date_string,
        # to must be after from
        "to": to_date_string,
        "reportingDate": reporting_date_string,
        "reportingEntityType": random.choice(reporting_entity_types),
        "sexGroupMaleCases": male_cases,
        "sexGroupFemaleCases": female_cases,
        "sexGroupUnknownCases": unknown_cases,
        "ageGroup0To4Cases": age_group_0_to_4_cases,
        "ageGroup5To18Cases": age_group_5_to_18_cases,
        "ageGroup19To59Cases": age_group_19_to_58_cases,
        "ageGroup60PlusCases": age_group_60_plus_cases,
        "ageGroupUnknownCases": age_group_unknown_cases,
        "reportingEntityIdentifier": faker.bothify(text='???-######'),
        "administrativeLevel": random.choice([0, 1, 2, 3])
    }
    
    return case_report
