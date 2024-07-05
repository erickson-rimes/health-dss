import json
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

def generate_advisory():
    current_time = datetime.now()
    advisory = {
        "id": str(uuid.uuid4()),
        "title": fake.sentence(nb_words=6),
        "author": {
            "id": str(uuid.uuid4()),
            "name": fake.name(),
            "role": "Public Health Officer"
        },
        "content": '\n'.join(fake.paragraphs(nb=5)),
        "tags": [fake.word() for _ in range(random.randint(2, 5))],
        "created_at": current_time.isoformat(),
        "updated_at": (current_time + timedelta(days=random.randint(0, 10))).isoformat(),
        "status": random.choice(["draft", "published", "archived"]),
        "publication_date": (current_time + timedelta(days=random.randint(1, 30))).isoformat(),
        "attachments": [
            {
                "id": str(uuid.uuid4()),
                "url": fake.url(),
                "file_name": fake.file_name(),
                "file_type": fake.mime_type(),
                "size": random.randint(1024, 1048576)
            } for _ in range(random.randint(1, 3))
        ]
    }
    return advisory

def generate_advisories(num_advisories):
    advisories = [generate_advisory() for _ in range(num_advisories)]
    return advisories

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

num_advisories = 1000  # Number of dummy advisories to generate
advisories = generate_advisories(num_advisories)
save_to_json(advisories, 'advisories.json')
print(f"{num_advisories} dummy advisories have been generated and saved to advisories.json")