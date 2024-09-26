import os
import sqlite3
import psycopg2
from psycopg2 import sql

# PostgreSQL connection details from the docker-compose setup
POSTGRES_DB = "mydb"
POSTGRES_USER = "myuser"
POSTGRES_PASSWORD = "mypassword"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "8053"

# Folder containing the SQLite databases
SQLITE_FOLDER = './sqlite_dbs'

# Function to migrate a single SQLite database to PostgreSQL
def migrate_sqlite_to_postgres(sqlite_db_path):
    try:
        # Connect to SQLite database
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_cursor = sqlite_conn.cursor()

        # Connect to PostgreSQL database
        pg_conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        pg_cursor = pg_conn.cursor()

        # Get the list of all tables in the SQLite database
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = sqlite_cursor.fetchall()

        for table_name in tables:
            table_name = table_name[0]

            # Skip internal SQLite tables like sqlite_sequence
            if table_name == "sqlite_sequence":
                print(f"Skipping internal SQLite table: {table_name}")
                continue

            print(f"Migrating table {table_name} from {sqlite_db_path}...")

            # Fetch the table schema and create the table in PostgreSQL
            sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
            columns = sqlite_cursor.fetchall()

            # Start building the CREATE TABLE statement with double quotes
            create_table_query = f'CREATE TABLE IF NOT EXISTS "{table_name}" ('
            for column in columns:
                column_name, column_type = column[1], column[2]
                
                # Correct the data type for PostgreSQL
                if "INTEGER" in column_type:
                    column_type = "INTEGER"
                elif "TEXT" in column_type:
                    column_type = "TEXT"
                elif "REAL" in column_type:
                    column_type = "REAL"
                elif "BLOB" in column_type:
                    column_type = "BYTEA"

                # Add the column to the CREATE TABLE query with double quotes
                create_table_query += f'"{column_name}" {column_type}, '

            # Finish the CREATE TABLE query
            create_table_query = create_table_query.rstrip(", ") + ");"
            
            # Execute the table creation in PostgreSQL
            pg_cursor.execute(create_table_query)

            # Fetch data from SQLite table
            sqlite_cursor.execute(f"SELECT * FROM {table_name};")
            rows = sqlite_cursor.fetchall()

            # Insert data into PostgreSQL table
            for row in rows:
                insert_query = sql.SQL(f'INSERT INTO "{table_name}" VALUES ({", ".join(["%s"] * len(row))});')
                pg_cursor.execute(insert_query, row)

        # Commit the transaction and close connections
        pg_conn.commit()
        pg_cursor.close()
        pg_conn.close()
        sqlite_conn.close()
        print(f"Migration of {sqlite_db_path} completed successfully.")

    except Exception as e:
        print(f"Error migrating {sqlite_db_path}: {e}")

# Main function to iterate through all SQLite databases in the folder
def migrate_all_sqlite_dbs():
    for sqlite_db in os.listdir(SQLITE_FOLDER):
        if sqlite_db.endswith(".db"):  # Assuming all SQLite databases have the .db extension
            sqlite_db_path = os.path.join(SQLITE_FOLDER, sqlite_db)
            migrate_sqlite_to_postgres(sqlite_db_path)

if __name__ == "__main__":
    migrate_all_sqlite_dbs()