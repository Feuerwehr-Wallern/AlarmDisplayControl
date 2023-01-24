#include <SoftwareSerial.h>

#define BwgPin 7
#define AlarmPin 8

SoftwareSerial TVSerial(10, 11); // RX, TX

int BwgVal = 0;
int AlarmVal = 0;
int cnt =0; // 3600=1h
boolean state = false;

void setup() {
TVSerial.begin(9600);
pinMode(BwgPin, INPUT);
pinMode(AlarmPin, INPUT);
}

void loop() {
  BwgVal = digitalRead(BwgPin);
  AlarmVal = digitalRead(AlarmPin);
  
  if ((BwgVal == HIGH or AlarmVal==HIGH) and state==false) {
    //Einschalten
    TVSerial.write(0x6B); //t
    TVSerial.write(0x61); //r
    TVSerial.write(0x20); //SPACE
    TVSerial.write(0x30); //00 - alle Monitore
    TVSerial.write(0x30); 
    TVSerial.write(0x20); //SPACE
    TVSerial.write(0x30); //01 Standby, 02 Einschalten
    TVSerial.write(0x31); 
    TVSerial.write(0x0D); //CR - Zeilenumsprung
    state = true; // Verriegelung, dass nicht ständig 'Ein-Signal' gesendet wird
  } 
  else if ((BwgVal == HIGH or AlarmVal==HIGH) and state==true) {
    cnt=0;
  }
  if ((BwgVal == LOW and AlarmVal==LOW) and state==true){
  delay(1000); //1Sek. warten und Nachlaufschleife um 1 erhöhen
  cnt=cnt+1;
  
    if (cnt==15) { //Nachlaufschleife beenden wenn Max. Zeit erreicht
      //Ausschalten
      TVSerial.write(0x6B); //t
      TVSerial.write(0x61); //r
      TVSerial.write(0x20); //SPACE
      TVSerial.write(0x30); //00 - alle Monitore
      TVSerial.write(0x30); 
      TVSerial.write(0x20); //SPACE
      TVSerial.write(0x30); //01 Standby, 02 Einschalten
      TVSerial.write(0x30);
      TVSerial.write(0x0D); //CR - Zeilenumsprung
      state = false; // Verriegelung aufheben
      cnt=0;
    }
  }
}
