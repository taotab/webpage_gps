# uses relative path, even tho program ran from different path,
# it will work fine, as the __file__ is used to get the path of the script

import os
import sqlite3
import csv


def export_to_csv(database_name, table_name, csv_filename):
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Connect to SQLite database
    db_path = os.path.join(script_dir, database_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch data from the table
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()

    # Write data to CSV file
    csv_path = os.path.join(script_dir, csv_filename)
    with open(csv_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write column headers
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(data)

    # Close the connection
    conn.close()


# Example usage
export_to_csv('sensor.db', 'gps_data', 'gps_data.csv')
