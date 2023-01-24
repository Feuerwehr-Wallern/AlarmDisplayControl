#include <SoftwareSerial.h>

#define BwgPin 4
#define BwgPin2 5
#define AlarmPin 2
#define AusgerPin 3
#define LedPin 13

SoftwareSerial TVSerial(10, 11); // RX, TX

int TvOnTime=300; // in Sekunden

int BwgVal = 0;
int BwgVal2 = 0;
int AlarmVal = 0;
int AusgerVal = 0;
int cnt =0; // 3600=1h
boolean TvPreState = false;

void setup() {
TVSerial.begin(9600);
Serial.begin(115200);

pinMode(BwgPin, INPUT);
pinMode(BwgPin2, INPUT);
digitalWrite(BwgPin, LOW);
digitalWrite(BwgPin2, LOW);
pinMode(AlarmPin, INPUT);
digitalWrite(AlarmPin, LOW);
pinMode(AusgerPin, INPUT);
digitalWrite(AusgerPin, LOW);
pinMode(LedPin, OUTPUT);

TvPreState = false;
Serial.println("Setup done");
}

void loop() {
  BwgVal = digitalRead(BwgPin);
  BwgVal2 = digitalRead(BwgPin2);
  AlarmVal = digitalRead(AlarmPin);
  AusgerVal = digitalRead(AusgerPin);
  byte message_TV_on[]  = {0x6B, 0x61, 0x20, 0x30, 0x30, 0x20, 0x30, 0x31, 0x0D};
  byte message_TV_off[] = {0x6B, 0x61, 0x20, 0x30, 0x30, 0x20, 0x30, 0x30, 0x0D};
  
  if ((BwgVal == HIGH or BwgVal2 == HIGH or AlarmVal==HIGH or AusgerVal==HIGH) and TvPreState==false) {
    //Einschalten
    TVSerial.write(message_TV_on, sizeof(message_TV_on));
    Serial.println("TV - EIN");
    TvPreState = true; // TV Status : EIN
  } 
  else if ((BwgVal == HIGH or BwgVal2 == HIGH or AlarmVal==HIGH or AusgerVal==HIGH) and TvPreState==true) {
    cnt=0;
    //Serial.println("Counter Reset");
  }
  if ((BwgVal == LOW and BwgVal2 == LOW and AlarmVal==LOW and AusgerVal==LOW) and TvPreState==true){
    delay(1000);
    cnt=cnt+1;
    Serial.println("Counter: " + String(cnt));
  
    if (cnt>=TvOnTime) { //Nachlaufschleife beenden wenn Max. Zeit erreicht
      //Ausschalten
      TVSerial.write(message_TV_off, sizeof(message_TV_off));
      Serial.println("TV - OFF");
      TvPreState = false; // TV Status : AUS
      cnt=0;
    }
  }
  if (BwgVal == HIGH or BwgVal2 == HIGH) {
    digitalWrite(LedPin, HIGH);
  } else {
    digitalWrite(LedPin, LOW);
  }
  }
