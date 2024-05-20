#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <TinyGPS++.h>
#include <SoftwareSerial.h>

const char *ssid = "Dataman";
const char *password = "123890123";
const char *serverUrl = "http://192.168.225.183:5000/receive_gps_data";
const char *apiKey = "your_secure_api_key_here"; // Add your API key here

unsigned long counter = 0;
const unsigned long sendInterval = 50; // Send data every 50 iterations

const long utcOffsetInSeconds = (5 * 3600) + (30 * 60);
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", utcOffsetInSeconds);

#define GPS_RX_PIN 4 // Define the pin connected to GPS module's RX pin
#define GPS_TX_PIN 3 // Define the pin connected to GPS module's TX pin

TinyGPSPlus gps;
SoftwareSerial gpsSerial(GPS_RX_PIN, GPS_TX_PIN);

void setup()
{
    Serial.begin(9600);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("");
    Serial.println("WiFi connected");

    timeClient.begin();
    gpsSerial.begin(9600);
}

void sendDataToServer(String data)
{
    WiFiClient client;
    HTTPClient http;

    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-KEY", apiKey); // Include the API key in the headers

    int httpResponseCode = http.POST(data);

    if (httpResponseCode > 0)
    {
        Serial.print("Data sent successfully! HTTP Response Code: ");
        Serial.println(httpResponseCode);
    }
    else
    {
        Serial.print("Failed to send data. HTTP Response Code: ");
        Serial.println(httpResponseCode);
    }

    http.end();
}

void loop()
{
    timeClient.update();
    gpsSerial.listen();

    // Read GPS data
    while (gpsSerial.available() > 0)
    {
        if (gps.encode(gpsSerial.read()))
        {
            if (gps.location.isValid() && counter >= sendInterval)
            {
                float latitude = gps.location.lat();
                float longitude = gps.location.lng();

                // Create JSON string with GPS coordinates and timestamp
                String gpsData = "{\"Latitude\":" + String(latitude, 6) + ", \"Longitude\":" + String(longitude, 6) + ", \"Timestamp\":\"" + timeClient.getFormattedTime() + "\"}";

                // Send GPS data to Flask server
                sendDataToServer(gpsData);

                counter = 0; // Reset counter
            }
        }
    }

    delay(100);
    counter++;
}
