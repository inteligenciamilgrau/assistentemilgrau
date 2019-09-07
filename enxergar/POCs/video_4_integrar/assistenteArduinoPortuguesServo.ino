#include <Servo.h>

#define pinoLampada 8

String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete

int posicaoServo = 90;

Servo meuServo;

void setup() {
  // initialize serial:
  Serial.begin(115200);
  // reserve 200 bytes for the inputString:
  inputString.reserve(200);
  
  pinMode(pinoLampada, OUTPUT);
  pinMode(LED_BUILTIN,OUTPUT);

  meuServo.attach(9);
  meuServo.write(posicaoServo);
}

void loop() {
  // print the string when a newline arrives:
  if (stringComplete) {
    // clear the string:
    if(inputString.startsWith("ligar")){
      //digitalWrite(pinoLampada, !digitalRead(LED_BUILTIN));// toggle
      digitalWrite(pinoLampada, HIGH);
      Serial.print("Assistente Mil Grau. Luz ligada!!");
    }else if(inputString.startsWith("desligar")){
      digitalWrite(pinoLampada, LOW);
      Serial.print("Assistente Mil Grau. Luz desligada!!");
    }else if(inputString.startsWith("servo")){
      
      digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));

      int moveCamera = inputString.substring(5).toInt();

      if(moveCamera >= 1) moveCamera = 1;
      else if(moveCamera <= -1) moveCamera = -1;
      
      posicaoServo += moveCamera;
      
      if(posicaoServo > 180) posicaoServo = 180;
      else if(posicaoServo <=0) posicaoServo = 0;
      
      meuServo.write(posicaoServo);
    } else{
      Serial.print(inputString);
    }
     
    inputString = "";
    stringComplete = false;
  }
}

/*
  SerialEvent occurs whenever a new data comes in the hardware serial RX. This
  routine is run between each time loop() runs, so using delay inside loop can
  delay response. Multiple bytes of data may be available.
*/
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}
