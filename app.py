from math import radians, cos, sin, sqrt, atan2
import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

API_KEY = 'your_secure_api_key_here'  # Set a secure API key

latest_data = {"Latitude": "N/A", "Longitude": "N/A",
               "Timestamp": "N/A", "Date": "N/A"}


def get_db_connection():
    try:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        db_path = os.path.join(current_dir, 'sensor.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        print("Database connection successful")  # Debug print
        return conn
    except Exception as e:
        print(f"Database connection failed: {str(e)}")  # Debug print


@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))


@app.route('/get_latest_data', methods=['GET'])
def get_latest_data():
    return jsonify(latest_data)


@app.route('/receive_gps_data', methods=['POST'])
def receive_gps_data():
    api_key = request.headers.get('X-API-KEY')
    if api_key != API_KEY:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    try:
        data = request.get_json(force=True)
        print("Received GPS data:", data)

        conn = get_db_connection()
        cursor = conn.cursor()

        current_date = datetime.now().date()

        cursor.execute("INSERT INTO gps_data (latitude, longitude, timestamp, date) VALUES (?, ?, ?, ?)",
                       (data["Latitude"], data["Longitude"], data["Timestamp"], current_date))

        conn.commit()
        conn.close()

        global latest_data
        latest_data["Timestamp"] = data.get("Timestamp", "N/A")
        latest_data["Latitude"] = data.get("Latitude", "N/A")
        latest_data["Longitude"] = data.get("Longitude", "N/A")
        latest_data["Date"] = str(current_date)

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error processing GPS data: {str(e)}")
        return jsonify({"status": "error"}), 500


@app.route('/readings')
def readings():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM gps_data ORDER BY timestamp DESC LIMIT 15')
    readings = cursor.fetchall()
    conn.close()
    return render_template('readings.html', readings=readings)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('Login successful.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user:
            flash('Account already exists!')
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()
            flash('You have successfully registered! Please login.')
            return redirect(url_for('login'))
    return render_template('register.html')


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of the Earth in kilometers

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance * 1000  # Convert to meters


@app.route('/distance', methods=['GET', 'POST'])
def calculate_distance():
    if 'username' not in session:
        return redirect(url_for('login'))

    distance = None

    if request.method == 'POST':
        date1 = request.form.get('date1')
        time1 = request.form.get('time1')
        date2 = request.form.get('date2')
        time2 = request.form.get('time2')

        # Debug prints to ensure data is received
        print("Date 1:", date1)
        print("Time 1:", time1)
        print("Date 2:", date2)
        print("Time 2:", time2)

        # Convert date and time strings to datetime objects
        datetime1 = datetime.strptime(date1 + ' ' + time1, '%Y-%m-%d %H:%M:%S')
        datetime2 = datetime.strptime(date2 + ' ' + time2, '%Y-%m-%d %H:%M:%S')

        conn = get_db_connection()

        # Get latitude and longitude of Point 1
        cursor = conn.cursor()
        cursor.execute(
            "SELECT latitude, longitude FROM gps_data WHERE timestamp = ? AND date = ?", (time1, date1))
        row = cursor.fetchone()
        if row is not None:
            lat1, lon1 = row[0], row[1]
            print("Coordinates Point 1:", lat1, lon1)  # Debug print
        else:
            flash('Data not found for the specified date and timestamp.')
            return render_template('distance.html', distance=distance)

        # Get latitude and longitude of Point 2
        cursor.execute(
            "SELECT latitude, longitude FROM gps_data WHERE timestamp = ? AND date = ?", (time2, date2))
        row = cursor.fetchone()
        if row is not None:
            lat2, lon2 = row[0], row[1]
            print("Coordinates Point 2:", lat2, lon2)  # Debug print
        else:
            flash('Data not found for the specified date and timestamp.')
            return render_template('distance.html', distance=distance)

        conn.close()

        if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            # Round the distance to 2 decimal places
            distance = round(distance, 2)

            print("Calculated Distance:", distance)  # Debug print
        else:
            flash('Invalid date or timestamp.')

    return render_template('distance.html', distance=distance)


@app.route('/show_map')
def show_map():
    return render_template('map.html')


@app.route('/api/get_all_coordinates', methods=['GET'])
def get_all_coordinates():
    if 'username' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT latitude, longitude, timestamp FROM gps_data ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()

        coordinates = [{"latitude": row["latitude"], "longitude": row["longitude"],
                        "timestamp": row["timestamp"]} for row in rows]
        return jsonify(coordinates)
    except Exception as e:
        print(f"Error fetching coordinates: {str(e)}")
        return jsonify({"status": "error"}), 500

    from flask import render_template


@app.route('/select_start_location', methods=['GET', 'POST'])
def select_start_location():
    if request.method == 'POST':
        # Get date and time input from the form
        start_date = request.form.get('start_date')
        start_time = request.form.get('start_time')

        # Use start_date and start_time to retrieve the latitude and longitude of the starting location from the database
        # Calculate the distance between the starting location and the latest recorded location in the database

        # For demonstration purposes, assume distance calculation
        distance = 100  # Replace with actual distance calculation

        return render_template('display_distance.html', distance=distance)

    return render_template('select_start_location.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
