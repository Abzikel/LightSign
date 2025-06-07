// Libraries
#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>

// RGB pins
const int RED_PIN = 23;
const int GREEN_PIN = 22;
const int BLUE_PIN = 21;

// Define the Wi-Fi credentials for the Hotspot (Access Point)
const char *ssid = "RGB Controller";
const char *password = "rgbcontroller";

// Create a web server object on port 80 (standard HTTP port)
WebServer server(80);

// Define functions
void changeColor(const char *);
void handleColorChange();
void handleNotFound();

void setup()
{
  // Serial speed
  Serial.begin(115200);
  Serial.println("\nConfiguring ESP32 as Access Point (Hotspot)...");

  // Set frecuency and bit resolution
  ledcSetup(0, 5000, 8);
  ledcSetup(1, 5000, 8);
  ledcSetup(2, 5000, 8);

  // Define RGB pins as PWM outputs
  ledcAttachPin(RED_PIN, 0);
  ledcAttachPin(GREEN_PIN, 1);
  ledcAttachPin(BLUE_PIN, 2);

  // Set the ESP32 as an Access Point (Hotspot)
  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);
  Serial.print("Hotspot created with SSID: ");
  Serial.println(ssid);

  // Route to change the LED color
  server.on("/setColor", HTTP_POST, handleColorChange);

  // Handle any other undefined routes
  server.onNotFound(handleNotFound);

  // Start the server
  server.begin();
  Serial.println("HTTP server started");

  // Turn off the LED
  changeColor("#000000");
}

void loop()
{
  // Handle incoming HTTP requests
  server.handleClient();
}

// Function that changes the RGB Led using an HEX Color
void changeColor(const char *hexColor)
{
  // Simple validation
  if (hexColor[0] != '#' || strlen(hexColor) != 7)
  {
    Serial.println("Invalid color");
    return;
  }

  // Extract values from RGB
  int r = strtol(&hexColor[1], NULL, 16) >> 16;
  int g = (strtol(&hexColor[1], NULL, 16) >> 8) & 0xFF;
  int b = strtol(&hexColor[1], NULL, 16) & 0xFF;

  // Show values on console
  Serial.printf("Color: R=%d, G=%d, B=%d\n", r, g, b);

  // Send values to the LED
  ledcWrite(0, r);
  ledcWrite(1, g);
  ledcWrite(2, b);
}

// Handler for the /setColor endpoint
void handleColorChange()
{
  // Check if the request body is available
  if (server.hasArg("plain"))
  {
    // Get the body content
    String colorHex = server.arg("plain");
    Serial.print("Received POST request to /setColor with body: ");
    Serial.println(colorHex);

    // Convert String to const char*
    changeColor(colorHex.c_str());
    server.send(200, "text/plain", "Color updated successfully!");
  }
  else
  {
    Serial.println("No body in POST request to /setColor.");
    server.send(400, "text/plain", "Bad Request: Please send a hex color in the request body (e.g., #FF00FF).");
  }
}

// Handler for undefined routes
void handleNotFound()
{
  server.send(404, "text/plain", "Not Found");
}
