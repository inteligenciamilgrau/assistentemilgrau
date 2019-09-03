#include <Servo.h>

String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete

int posicaoServo = 90; // posicao inicial em 90 graus (meio)

Servo meuServo;

void setup() {
  // initialize serial:
  Serial.begin(115200);
  // reserve 200 bytes for the inputString:
  inputString.reserve(200);

  meuServo.attach(9);
  meuServo.write(posicaoServo);
}

void loop() {
  // print the string when a newline arrives:
  if (stringComplete) {
    if(inputString.startsWith("servo")){
      int moveCamera = inputString.substring(5).toInt();

      // limita o movimento em apenas 1 grau
      if(moveCamera >= 1) moveCamera = 1;
      else if(moveCamera <= -1) moveCamera = -1;

      // atualiza a posição do servo
      posicaoServo += moveCamera;

      // limita o servo a ter de 0 a 180 graus
      if(posicaoServo > 180) posicaoServo = 180;
      else if(posicaoServo <=0) posicaoServo = 0;

      // move o servo
      meuServo.write(posicaoServo);
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
