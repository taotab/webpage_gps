import os
import folium
import sqlite3


def visualize_gps_data(database_name, table_name):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the SQLite database file
    database_path = os.path.join(script_dir, database_name)

    # Connect to SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Fetch latitude and longitude data from the table
    cursor.execute(f"SELECT latitude, longitude FROM {table_name}")
    data = cursor.fetchall()

    # Close the connection
    conn.close()

    # Create a map centered around the first GPS coordinates
    m = folium.Map(location=[data[0][0], data[0][1]], zoom_start=10)

    # Add markers for each GPS coordinate
    for coord in data:
        folium.Marker(location=[coord[0], coord[1]]).add_to(m)

    # Save the map as an HTML file
    map_filename = os.path.join(script_dir, 'gps_data_map.html')
    m.save(map_filename)

    print(f"Map saved as {map_filename}")


# Example usage
visualize_gps_data('sensor.db', 'gps_data')
