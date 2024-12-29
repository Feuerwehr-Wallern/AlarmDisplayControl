// Freiwillige Feuerwehr Wallern
// Infopoint Monitorsteuerung
// Date 02/2023
// Author HBM Stefan Schneebauer
// Author HBM Stefan Pflüglmayer

#include <SoftwareSerial.h>

// ## Defines #####################################################
#define AUSGER_PIN 2
#define ALARM_PIN 3
#define BWG1_PIN 4
#define BWG2_PIN 5
#define BWG3_PIN 6
#define USERLED1_PIN 12   // ext.
#define USERLED2_PIN 13   // int

#define CYCLE_TIME 200       // Schleifenzeit in ms
#define TV_OVERRUN_TIME 600  // Nachlaufzeit in s  600
#define TV_ON_BLOCK_TIME 10  // Wiedereinschalten blockieren in s

// ## Global Variables ############################################
SoftwareSerial TVSerial(10, 11); // RX, TX (shield, do not cross!)

byte message_TV1_on[]  = {0x6B, 0x61, 0x20, 0x30, 0x31, 0x20, 0x30, 0x31, 0x0D};
byte message_TV2_on[]  = {0x6B, 0x61, 0x20, 0x30, 0x32, 0x20, 0x30, 0x31, 0x0D};
byte message_TV1_off[] = {0x6B, 0x61, 0x20, 0x30, 0x31, 0x20, 0x30, 0x30, 0x0D};
byte message_TV2_off[] = {0x6B, 0x61, 0x20, 0x30, 0x32, 0x20, 0x30, 0x30, 0x0D};

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
  pinMode(BWG3_PIN, INPUT);
  pinMode(USERLED1_PIN, OUTPUT);
  pinMode(USERLED2_PIN, OUTPUT);
  
  //digitalWrite(ALARM_PIN, LOW);
  //digitalWrite(AUSGER_PIN, LOW);
  digitalWrite(BWG1_PIN, LOW);
  digitalWrite(BWG2_PIN, LOW);
  digitalWrite(BWG2_PIN, LOW);
  digitalWrite(USERLED1_PIN, HIGH);
  digitalWrite(USERLED2_PIN, HIGH);
  delay(500);
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
  motionDetected = digitalRead(BWG1_PIN) or digitalRead(BWG2_PIN) or digitalRead(BWG3_PIN);
  //readRS232Data("Allg.");

  if (!tvState and !blocked and (motionDetected or alarmVal or ausgerVal)) {      // TV Einschalten
    TVSerial.write(message_TV1_on, sizeof(message_TV1_on));
    //readRS232Data("TV1-ON");
    delay(300);
    TVSerial.write(message_TV2_on, sizeof(message_TV2_on));
    //readRS232Data("TV2-ON");
    Serial.println("TV - ON");
    tvState = true;
    startTime = actTime;
  
  } else if (tvState and !blocked and (motionDetected or alarmVal or ausgerVal)) {
    startTime = actTime;
  }
  
  /*if (digitalRead(BWG1_PIN)==1){
    Serial.println("Melder 1: Bewegung erkannt");
  }
  if (digitalRead(BWG2_PIN)==1){
    Serial.println("Melder 2: Bewegung erkannt");
  }
  if (digitalRead(BWG3_PIN)==1){
    Serial.println("Melder 3: Bewegung erkannt");
  }
  if (digitalRead(ALARM_PIN)==1){
    Serial.println("Status: Alarmiert");
  }
  if (digitalRead(AUSGER_PIN)==1){
    Serial.println("Status: Ausgerueckt");
  }*/
  

  if (tvState and (actTime - startTime >= (unsigned long) TV_OVERRUN_TIME * 1000)) {   // TV Ausschalten
      TVSerial.write(message_TV1_off, sizeof(message_TV1_off));
      //readRS232Data("TV1-OFF");
      delay(300);
      TVSerial.write(message_TV2_off, sizeof(message_TV2_off));
      //readRS232Data("TV2-OFF");
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

void readRS232Data(String TVChan) {
  const int BUFFER_SIZE = 100;
  
  delay(300);
  if(TVSerial.available()){
    byte buf[BUFFER_SIZE];
    int rlen = TVSerial.readBytes(buf, BUFFER_SIZE);
    Serial.print("Received [HEX]: ");
    for(int i=0; i<rlen; i++){
      Serial.print("0x");
      Serial.print(buf[i],HEX);
      Serial.print(", ");
    }
    Serial.print(" --> ");
    Serial.print(rlen);
    Serial.println(" Bytes empfangen!");
  }
}
