// Freiwillige Feuerwehr Wallern
// Infopoint Monitorsteuerung
// Date 08/2022
// Author HBM Stefan Schneebauer
// Author HBM Stefan Pflüglmayer

#include <SoftwareSerial.h>

// ## Defines #####################################################
#define ALARM_PIN 2
#define AUSGER_PIN 3
#define BWG1_PIN 4
#define BWG2_PIN 5
#define USERLED1_PIN 13
#define USERLED2_PIN A0

#define CYCLE_TIME 200       // Schleifenzeit in ms
#define TV_OVERRUN_TIME 60  // Nachlaufzeit in s  600
#define TV_ON_BLOCK_TIME 10  // Wiedereinschalten blockieren in s

// ## Global Variables ############################################
SoftwareSerial TVSerial(10, 11); // RX, TX

byte message_TV_on[]  = {0x6B, 0x61, 0x20, 0x30, 0x30, 0x20, 0x30, 0x31, 0x0D};
byte message_TV_off[] = {0x6B, 0x61, 0x20, 0x30, 0x30, 0x20, 0x30, 0x30, 0x0D};

unsigned long startTime = 0;
unsigned long actTime = 0;
boolean tvState = false;
boolean blocked = false;

boolean motionDetected = false;
boolean alarmVal = false;
boolean ausgerVal = false;


// ################################################################
// ## Setup #######################################################
// ################################################################
void setup() {
  TVSerial.begin(9600);
  Serial.begin(9600);

  pinMode(ALARM_PIN, INPUT);
  pinMode(AUSGER_PIN, INPUT);
  pinMode(BWG1_PIN, INPUT);
  pinMode(BWG2_PIN, INPUT);
  pinMode(USERLED1_PIN, OUTPUT);
  pinMode(USERLED2_PIN, OUTPUT);
  
  digitalWrite(ALARM_PIN, LOW);
  digitalWrite(AUSGER_PIN, LOW);
  digitalWrite(BWG1_PIN, LOW);
  digitalWrite(BWG2_PIN, LOW);
  digitalWrite(USERLED1_PIN, LOW);
  digitalWrite(USERLED2_PIN, LOW);

  Serial.println("Setup done");
}


// ################################################################
// ## Loop ########################################################
// ################################################################
void loop() {
  actTime = millis();
  alarmVal = digitalRead(ALARM_PIN);
  ausgerVal = digitalRead(AUSGER_PIN);
  motionDetected = digitalRead(BWG1_PIN) or digitalRead(BWG2_PIN);

  if (!tvState and !blocked and (motionDetected or alarmVal or ausgerVal)) {      // TV Einschalten
    TVSerial.write(message_TV_on, sizeof(message_TV_on));
    Serial.println("TV - ON");
    tvState = true;
    startTime = actTime;
  
  } else if (tvState and !blocked and (motionDetected or alarmVal or ausgerVal)) {
    startTime = actTime;
  }

  if (tvState and (actTime - startTime >= (unsigned long) TV_OVERRUN_TIME * 1000)) {   // TV Ausschalten
      TVSerial.write(message_TV_off, sizeof(message_TV_off));
      Serial.println("TV - OFF");
      tvState = false;
      blocked = true;
      startTime = actTime;
  }

  if (blocked and (actTime - startTime >= (unsigned long) TV_ON_BLOCK_TIME * 1000)) {
    blocked = false;
  }

  /*Serial.print("StartTime: ");
  Serial.print(startTime);
  Serial.print(" Time: ");
  Serial.print(actTime);
  Serial.print(" DiffTime: ");
  Serial.print(actTime-startTime);
  Serial.print(" State: ");
  Serial.println(tvState);*/
  
  digitalWrite(USERLED2_PIN, motionDetected);
  digitalWrite(USERLED1_PIN, tvState);

  delay(CYCLE_TIME);
}
