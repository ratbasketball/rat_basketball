#include <Adafruit_NeoPixel.h>

#define PIN            6   // Pin connected to the data input of both WS2812B panels
#define NUM_PIXELS    128 // Total number of pixels (64 for panel 1, 64 for panel 2)

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_PIXELS, PIN, NEO_GRB + NEO_KHZ800);

// Structure to hold the state of each panel
struct Panel {
  int r, g, b;           // Color
  int brightness;        // Brightness
  unsigned long turnOffTime;  // Time at which to turn off (0 means stay on indefinitely)
};

Panel panels[2];  // Array to hold states of two panels (panel 1 and panel 2)

void setup() {
  // Start serial communication
  Serial.begin(9600);

  // Initialize the WS2812B panels
  strip.begin();
  strip.show(); // Initialize all pixels to "off"

  // Initialize the panels with default values (you can customize this)
  for (int i = 0; i < 2; i++) {
    panels[i].r = 0;
    panels[i].g = 0;
    panels[i].b = 0;
    panels[i].brightness = 255;
    panels[i].turnOffTime = 0;
  }
}

void loop() {
  // Check if new data is available on the serial port
  if (Serial.available() > 0) {
    // Read the incoming data as a string
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove any leading or trailing whitespace

    // Parse the command string into panel number, r, g, b, brightness, and duration
    int panelNum = -1, r = -1, g = -1, b = -1, brightness = -1, duration = -1;
    int numParams = sscanf(command.c_str(), "panel %d %d %d %d %d %d", &panelNum, &r, &g, &b, &brightness, &duration);

    // If the panel number is valid and the command is complete
    if (numParams == 6 && panelNum >= 1 && panelNum <= 2 && r >= 0 && g >= 0 && b >= 0 && brightness >= 0) {
      // Update the selected panel's state
      panelNum--; // Convert to zero-based index
      panels[panelNum].r = r;
      panels[panelNum].g = g;
      panels[panelNum].b = b;
      panels[panelNum].brightness = brightness;

      // Set the brightness of the panel
      strip.setBrightness(brightness);

      // Light up the selected panel
      for (int i = 0; i < NUM_PIXELS; i++) {
        if (panelNum == 0 && i < 64) { // First panel: Pixels 0-63
          strip.setPixelColor(i, strip.Color(r, g, b));
        } else if (panelNum == 1 && i >= 64) { // Second panel: Pixels 64-127
          strip.setPixelColor(i, strip.Color(r, g, b));
        }
      }
      strip.show();  // Update the panels with the new color

      // Handle duration: -1 means stay on indefinitely
      if (duration == -1) {
        panels[panelNum].turnOffTime = 0; // Indicate no turn-off time
      } else {
        // Set the turn-off time based on the current time and the duration
        panels[panelNum].turnOffTime = millis() + duration;
      }
    }
    else {
      // Handle invalid command
      Serial.println("Invalid command format, use: panel <1 or 2> r g b brightness duration");
    }
  }

  // Check if it's time to turn off the LEDs for any panel
  for (int i = 0; i < 2; i++) {
    if (panels[i].turnOffTime != 0 && millis() >= panels[i].turnOffTime) {
      // Turn off the selected panel
      if (i == 0) { // First panel: Pixels 0-63
        for (int j = 0; j < 64; j++) {
          strip.setPixelColor(j, strip.Color(0, 0, 0));
        }
      } else if (i == 1) { // Second panel: Pixels 64-127
        for (int j = 64; j < 128; j++) {
          strip.setPixelColor(j, strip.Color(0, 0, 0));
        }
      }
      strip.show();  // Update the panel to turn off
      panels[i].turnOffTime = 0; // Reset the turn-off time
    }
  }
}
