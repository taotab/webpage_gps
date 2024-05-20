## keeps notes...

1. since delay(100) only works with gps module to send to our flask server, can't change it.. keeping it longer like 5000 (5 secons)
makes it not work.
2. but 100ms is too fast, too much frequent data sends to server, its useless to have such many store for location tracking, also
there is overhead to server to handle such many requests.
3. so we kept the delay(100) only, and used the loop counter to send data to server every 50 iterations.
4. 50*100ms = 5 seconds, so every 5 seconds we send data to server.
5. this is done in the loop() function, which is at the last.




## Database table:

1. table is created, cmd: "sqlite3 sensor.db" and ".schema" to check tables
2. "CREATE TABLE IF NOT EXISTS gps_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL,
    longitude REAL,
    timestamp TEXT,
    date TEXT
);"

to create the table.



### About the design of nodemcu->flask->sqlite values sending and formats change Flow:

You're mostly correct. Here's a more detailed explanation:

1. The NodeMCU device sends GPS data to the Flask application. The data is typically sent as a JSON object, which is a string format that can represent complex data structures. Each field in the JSON object can be a number, a string, a boolean, an array, another JSON object, or null.

2. The Flask application receives the JSON object in the `/receive_gps_data` route. It uses the `request.get_json(force=True)` function to parse the JSON object into a Python dictionary. If the JSON object contains numbers, they will be converted to Python's `int` or `float` types. If it contains strings, they will remain as Python's `str` type.

3. The Flask application then stores the data in the SQLite database. When storing the data, SQLite will convert the Python types to SQLite types according to the following rules:
   - Python `int` or `float` types will be stored as SQLite `INTEGER` or `REAL`.
   - Python `str` type will be stored as SQLite `TEXT`.

So, the Flask application does do some processing of the data: it parses the JSON object into a Python dictionary and then stores the data in the SQLite database. But it doesn't change the types of the data; it just stores them as they are received. The SQLite database then stores the data in the format specified by the table schema.