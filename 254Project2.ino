#include <LiquidCrystal.h>

// LCD pin configuration: (RS, EN, D4, D5, D6, D7)
LiquidCrystal lcd(12, 11, 5, 4, 3, 6);

// PIR sensor
int pirPin = 2;
int motionState = LOW;
int PASSIVE_BUZZER = 7;

// Buzzer pins
#define BLUE_BUZZER 13
#define RED_BUZZER 10


void setup() {
  
  pinMode(pirPin, INPUT);
  pinMode(BLUE_BUZZER, OUTPUT);
  pinMode(RED_BUZZER, OUTPUT);
  pinMode(PASSIVE_BUZZER, OUTPUT);

  lcd.begin(16, 2); // Set LCD size
  Serial.begin(9600);

  lcd.print("System Armed...");
  delay(2000);
  lcd.clear();
}

void loop() {
  int pirVal = digitalRead(pirPin);

  // Handle PIR motion detection
  if (pirVal == HIGH && motionState == LOW) {
    motionState = HIGH;
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("INTRUDER ALERT!");
    Serial.println("INTRUDER ALERT!");
  }
  else if (pirVal == LOW && motionState == HIGH) {
    motionState = LOW;
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("All Clear");
    Serial.println("All Clear");
  }

  // Handle face recognition signal from Python
  if (Serial.available() > 0) {
    char receivedChar = Serial.read();

    if (receivedChar == 'B') {
      // Recognized face → Blue buzzer ON, Red OFF
      digitalWrite(RED_BUZZER, LOW);
      digitalWrite(BLUE_BUZZER, HIGH);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Face Recognized");
    
    }
    else if (receivedChar == 'R') {
      // Unrecognized face → Red buzzer ON, Blue OFF
      digitalWrite(BLUE_BUZZER, LOW);
      digitalWrite(RED_BUZZER, HIGH);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Unknown Face!");
      
      for( int i = 1 ; i <= 4; i++) {
      tone(PASSIVE_BUZZER, 300);
      delay(100);
      tone(PASSIVE_BUZZER, 100);
      }
     
    }
  }

  delay(100); // Prevent overload
}