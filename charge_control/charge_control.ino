const int RELAY_ON_PIN = 3;
const int RELAY_OFF_PIN = 2;
const int USB_IN_PIN = 4;
const int ON_BUTTON_PIN = 5;
const int HALF_LIPO_VOLTAGE_PIN = 0;
const int BUZZER_PIN = 7;

const float MIN_ALLOWED_OFF = 7.71;
const float MIN_REQUIRED_OFF = 7.42;
const float CHARGED_THRESHOLD = 9.0;
const float BUZZ_DELAY = 1.0;

float last_buzz_stamp = -2.0 * BUZZ_DELAY;
bool permanent_off;

float moving_avg = 0;
float moving_denom = 0;
const float DECAY_FACTOR = 0.95;

float start_charged_stamp = -1;


void turn_on_pin_for_set_time(int pinName, int setTimeInMilliseconds) {
  digitalWrite(pinName, HIGH);
  delay(setTimeInMilliseconds);
  digitalWrite(pinName, LOW);
}

void setup() {
  pinMode(RELAY_ON_PIN, OUTPUT);
  pinMode(RELAY_OFF_PIN, OUTPUT);
  pinMode(USB_IN_PIN, INPUT);
  pinMode(ON_BUTTON_PIN, INPUT);
  pinMode(HALF_LIPO_VOLTAGE_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  Serial.begin(115200);
  Serial.println("BOOTED");

  turn_on_pin_for_set_time(RELAY_ON_PIN, 100);
  permanent_off = false;

  while (digitalRead(ON_BUTTON_PIN) == HIGH) {
    delay(10);
  }

  delay(100);
}

void loop() {
  delay(20);
  float lipo_reading = analogRead(HALF_LIPO_VOLTAGE_PIN);
  // we multiply by 2 as it goes through voltage divider
  // this is the voltage of the 2-cell lipo
  float voltage = 2 * 5.0 * (lipo_reading / 1024.0);

  long millis_stamp = millis();
  long buzz_millis = BUZZ_DELAY * 1000;
  float stamp = millis_stamp / 1000.0;
  float time_since_buzz = stamp - last_buzz_stamp;

  Serial.print("lipo reading: ");
  Serial.println(lipo_reading);
  Serial.print("lipo voltage: ");
  Serial.println(voltage);

  Serial.print("usb in: ");
  Serial.println(digitalRead(USB_IN_PIN));

  moving_avg = moving_avg * DECAY_FACTOR + voltage;
  moving_denom = moving_denom * DECAY_FACTOR + 1.0;
  float smooth_voltage = moving_avg / moving_denom;
  Serial.print("SMOOTH_VOLTAGE: ");
  Serial.println(smooth_voltage);
  
  String mode = "UNKNOWN";
  bool is_charging = digitalRead(USB_IN_PIN);
  bool is_fully_charged = smooth_voltage > CHARGED_THRESHOLD;

  if (is_charging && (smooth_voltage > CHARGED_THRESHOLD)) {
    Serial.println("<<< VOLTAGE EXCEEDED >>>");
    if (time_since_buzz > BUZZ_DELAY * 2) {
      tone(BUZZER_PIN, 2000, buzz_millis);
      last_buzz_stamp = stamp;
    }
  }
  
  if (permanent_off) {
    digitalWrite(RELAY_OFF_PIN, HIGH);
    mode = "PERMA_OFF";
  } else {
    if ((smooth_voltage < MIN_REQUIRED_OFF) && !is_charging) {
      turn_on_pin_for_set_time(RELAY_OFF_PIN, 100);
      mode = "FORCE_OFF";
    } else {
      turn_on_pin_for_set_time(RELAY_ON_PIN, 20);
      mode = "TURN_ON";
    }

    if ((digitalRead(ON_BUTTON_PIN) == HIGH) && (smooth_voltage < MIN_ALLOWED_OFF)) {
      permanent_off = true;
    }
  }

  Serial.print("MODE: ");
  Serial.println(mode); 
}
