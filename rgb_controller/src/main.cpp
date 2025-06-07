// Libraries
#include <Arduino.h>

// RGB pins
const int RED_PIN = 23;
const int GREEN_PIN = 22;
const int BLUE_PIN = 21;

// Define functions
void changeColor(const char*);

void setup() {
  // Serial speed
  Serial.begin(115200);

  // Set frecuency and bit resolution
  ledcSetup(0, 5000, 8);
  ledcSetup(1, 5000, 8);
  ledcSetup(2, 5000, 8);

  // Define RGB pins as PWM outputs
  ledcAttachPin(RED_PIN, 0); 
  ledcAttachPin(GREEN_PIN, 1);
  ledcAttachPin(BLUE_PIN, 2);

  // Change color
  changeColor("#0000FF");
}

void loop() {
  // Do nothing
}

// Function that changes the RGB Led using an HEX Color
void changeColor(const char* hexColor) {
  // Simple validation
  if (hexColor[0] != '#' || strlen(hexColor) != 7) {
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
