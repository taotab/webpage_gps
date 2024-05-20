import sqlite3
import csv


def export_to_csv(database_name, table_name, csv_filename):
    # Connect to SQLite database
    conn = sqlite3.connect(
        "/home/tab/Documents/projects nodemcu/Try222/nerist_round_entries/sensor.db")
    cursor = conn.cursor()

    # Fetch data from the table
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()

    # Write data to CSV file
    with open(csv_filename, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write column headers
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(data)

    # Close the connection
    conn.close()


# Example usage
export_to_csv('sensor.db', 'gps_data', 'gps_data.csv')
