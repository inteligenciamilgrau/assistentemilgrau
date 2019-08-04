String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete

#define pinoLampada 8

void setup() {
  // initialize serial:
  Serial.begin(115200);
  // reserve 200 bytes for the inputString:
  inputString.reserve(200);
  
  pinMode(pinoLampada, OUTPUT);
}

void loop() {
  // print the string when a newline arrives:
  if (stringComplete) {
    // clear the string:
    if(inputString.startsWith("ligar")){
      //digitalWrite(pinoLampada, !digitalRead(LED_BUILTIN));// toggle
      digitalWrite(pinoLampada, HIGH);
      Serial.print("Assistente Mil Grau. Luz ligada.");
    }else if(inputString.startsWith("desligar")){
      digitalWrite(pinoLampada, LOW);
      Serial.print("Assistente Mil Grau. Luz desligada.");
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
