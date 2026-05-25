// set pin numbers for switch, joystick axes, and LED
#include <Mouse.h>

const int switchPin   =  9;   // switch to turn on and off mouse control
const int mouseButton = 10;   // input pin for the mouse pushButton
const int xAxis  = 1;         // joystick X axis to A1
const int yAxis  = 0;         // joystick Y axis to A0
const int ledPin = 13;        // Mouse control LED

// parameters for reading the joystick
int range = 10;              // output range of X or Y movement (zero to range)
int responseDelay = 5;        // response delay of the mouse, in ms
int threshold = range / 2;    // resting threshold
int center = range / 2;       // resting position value

boolean mouseIsActive = false;      // whether or not to control the mouse
int lastSwitchState = LOW;          // previous switch state
boolean mouseButtonPressed = false; // whether or not mouse button pressed
int lastReading = 1;       // last joystick/mouse button reading
long debounceTime = 0;      // last time the mouse button was toggled
long debounce = 50;         // debounce time, increase if the mouse clicks rapidly

void setup() {
  pinMode(switchPin, INPUT_PULLUP);   // the switch pin
  pinMode(mouseButton, INPUT_PULLUP); // mouse button on joystick
  pinMode(ledPin, OUTPUT);            // the LED pin
  Mouse.begin();
}

void loop() {
  int switchState;    // State of the mouse enable/disable button
  int buttonState;    // State of the mouse left button switch on joystick
  int xReading, yReading; // readings of the joystick movements
  int buttonReading;      // reading of the joystick (left mouse) button

  switchState = digitalRead(switchPin); // read the mouse disable switch
  // if it's changed and it's high, toggle the mouse state
  if (switchState != lastSwitchState) {
    if (switchState == HIGH) {
      // commented these lines since my mouse is always on
      // mouseIsActive = !mouseIsActive;
      // digitalWrite(ledPin, mouseIsActive);   // toggle LED to indicate mouse state
    }
  }
  lastSwitchState = switchState; // save switch state for next comparison
  mouseIsActive = true;
  // read and scale the two joystick readings, one for each axis
  xReading = readAxis(xAxis);
  yReading = readAxis(yAxis);

  // Normalize diagonal movement to ensure consistent speed
  if (xReading != 0 || yReading != 0) {
    float magnitude = sqrt(xReading * xReading + yReading * yReading);
    if (magnitude > range) {
      xReading = (xReading * range) / magnitude;
      yReading = (yReading * range) / magnitude;
    }
  }

  // Read the joystick button as the left mouse button. Debounce per
  // Ladyada code at https://learn.adafruit.com/tilt-sensor/using-a-tilt-sensor
  buttonReading = digitalRead(mouseButton); // read the mouse left button (push joystick)
  if (buttonReading != lastReading) {       // switch changed
    debounceTime = millis();                // reset debounce timer
  }
  if ((millis() - debounceTime) > debounce) {
    buttonState = buttonReading;
    if (buttonState == LOW) {
      Mouse.press(MOUSE_LEFT);
    } else {
      Mouse.release();
    }
  }
  lastReading = buttonReading;
  digitalWrite(ledPin, mouseButtonPressed); // toggle LED to indicate button state

  // if the mouse control state is active, move the mouse:
  if (mouseIsActive) {
    if (mouseButtonPressed) { // if joystick pressed down, indicate that too
      Mouse.move(xReading, yReading, 0);
    } else {
      Mouse.move(xReading, yReading, 0); // move, no mouse button press
    }
  }
  delay(responseDelay); // wait between mouse readings
}

// Reads a joystick axis (0 or 1 for x or y) and scales the
// analog input range to a range from 0 to <range>
int readAxis(int thisAxis) {
  int reading = analogRead(thisAxis); // read the analog input

  // map the reading from the analog input range to the output range
  reading = map(reading, 0, 1023, 0, range);

  // if the output reading is outside from the rest position threshold, use it
  int distance = reading - center;

  // Apply deadzone and centering delay
  if (abs(distance) < threshold) { // if distance not to threshold, no move
    distance = 0;                  // prevents tiny jitters due to readings
    delay(10);                     // Delay to center the joystick
  }
  return distance; // return the distance for this axis
}

