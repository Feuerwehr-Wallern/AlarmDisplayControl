#include <SoftwareSerial.h>

SoftwareSerial TVSerial(10, 11); // RX, TX

void setup() {
TVSerial.begin(9600);
//Serial.begin(9600);
}
  

void loop() {
  //Serial.println("Schleife Start");
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
  
  // Warten
  delay(15000);

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
  //Serial.println("Schleife Ende");
  delay(15000);
}
