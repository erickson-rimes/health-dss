import json
import sqlite3

# Load GeoJSON file
def load_geojson(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

# Create table if it doesn't exist
def create_table_if_not_exists(conn):
    cursor = conn.cursor()
    
    # SQL query to create the table with a TEXT column for geometry
    create_table_query = """
    CREATE TABLE IF NOT EXISTS geo_features (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        fill TEXT,
        fill_opacity REAL,
        stroke TEXT,
        stroke_opacity REAL,
        stroke_width REAL,
        geometry TEXT
    );
    """
    
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()

# Insert features into SQLite
def insert_features(features, conn):
    cursor = conn.cursor()
    
    for feature in features:
        # Extract geometry and properties
        geom = json.dumps(feature['geometry'])  # Store geometry as text
        properties = feature['properties']
        
        # Extract feature properties
        title = properties.get('title', 'Unknown')
        fill = properties.get('fill', '#000000')
        fill_opacity = properties.get('fill-opacity', 1.0)
        stroke = properties.get('stroke', '#000000')
        stroke_opacity = properties.get('stroke-opacity', 1.0)
        stroke_width = properties.get('stroke-width', 1.0)
        
        # SQL query to insert the feature into the geo_features table
        query = """
            INSERT INTO geo_features (title, fill, fill_opacity, stroke, stroke_opacity, stroke_width, geometry)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        # Execute the query with the extracted values using parameterized queries to avoid quoting issues
        cursor.execute(query, (
            title, fill, fill_opacity, stroke, stroke_opacity, stroke_width, geom
        ))
    
    # Commit the transaction
    conn.commit()
    cursor.close()

def main():
    # Load the GeoJSON file
    geojson_data = load_geojson('data_contourf_Q2_L12.json')
    
    # SQLite database file path
    db_path = 'wrf_geojson.db'
    
    # Connect to SQLite
    try:
        conn = sqlite3.connect(db_path)
        print("Connected to the database.")
        
        # Create the table if it doesn't exist
        create_table_if_not_exists(conn)
        
        # Ensure the GeoJSON contains features
        if geojson_data['type'] == 'FeatureCollection':
            features = geojson_data['features']
            
            # Insert features into the database
            insert_features(features, conn)
            print(f"{len(features)} features inserted into the database.")
        
        # Close the connection
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()