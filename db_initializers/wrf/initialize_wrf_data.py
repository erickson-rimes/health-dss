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
    CREATE TABLE IF NOT EXISTS geo_features_temp (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            INSERT INTO geo_features_temp (title, fill, fill_opacity, stroke, stroke_opacity, stroke_width, geometry)
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
        
        cursor = conn.cursor()

        # Ensure the GeoJSON contains features
        if geojson_data['type'] == 'FeatureCollection':
            features = geojson_data['features']
            
            query = """
                INSERT INTO geo_features_temp (geometry)
                VALUES (?)
            """
            
            for feature in features:
                geometry = json.dumps({"features": [feature], "type":"FeatureCollection"})
                cursor.execute(query, (geometry,))
            
            print(f"{len(features)} features inserted into the database.")

        # query = """
        #     INSERT INTO geo_features_temp (geometry) 
        #     VALUES (?)
        # """

        # cursor.execute(query, (json.dumps(geojson_data),))

        # print("GeoJSON data inserted into the database.")
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()