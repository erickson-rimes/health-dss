import json
import sqlite3

def create_database(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS advisory (
            id TEXT PRIMARY KEY,
            title TEXT,
            author_id TEXT,
            author_name TEXT,
            author_role TEXT,
            content TEXT,
            created_at TEXT,
            updated_at TEXT,
            status TEXT,
            publication_date TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS attachment (
            id TEXT PRIMARY KEY,
            advisory_id TEXT,
            url TEXT,
            file_name TEXT,
            file_type TEXT,
            size INTEGER,
            FOREIGN KEY (advisory_id) REFERENCES advisory (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS tag (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            advisory_id TEXT,
            tag TEXT,
            FOREIGN KEY (advisory_id) REFERENCES advisory (id)
        )
    ''')
    conn.commit()
    conn.close()

def insert_advisory(c, advisory):
    c.execute('''
        INSERT INTO advisory (
            id, title, author_id, author_name, author_role, content, created_at, updated_at, status, publication_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        advisory['id'],
        advisory['title'],
        advisory['author']['id'],
        advisory['author']['name'],
        advisory['author']['role'],
        advisory['content'],
        advisory['created_at'],
        advisory['updated_at'],
        advisory['status'],
        advisory['publication_date']
    ))

def insert_attachments(c, advisory_id, attachments):
    for attachment in attachments:
        c.execute('''
            INSERT INTO attachment (
                id, advisory_id, url, file_name, file_type, size
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            attachment['id'],
            advisory_id,
            attachment['url'],
            attachment['file_name'],
            attachment['file_type'],
            attachment['size']
        ))

def insert_tags(c, advisory_id, tags):
    for tag in tags:
        c.execute('''
            INSERT INTO tag (
                advisory_id, tag
            ) VALUES (?, ?)
        ''', (advisory_id, tag))

def json_to_sqlite(json_file, db_name):
    with open(json_file, 'r') as f:
        advisories = json.load(f)
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    for advisory in advisories:
        insert_advisory(c, advisory)
        insert_attachments(c, advisory['id'], advisory['attachments'])
        insert_tags(c, advisory['id'], advisory['tags'])

    conn.commit()
    conn.close()

db_name = 'advisories.db'
json_file = 'advisories.json'

create_database(db_name)
json_to_sqlite(json_file, db_name)
print(f"Data from {json_file} has been converted and saved to {db_name}")