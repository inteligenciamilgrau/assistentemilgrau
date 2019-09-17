#include <Servo.h>

String fraseRecebida = ""; // a String to hold incoming data
bool fraseCompleta = false;  // whether the string is complete

int posicaoBase = 90; // posicao inicial 
int posicaoSobeDesce = 140; // posicao inicial 
int posicaoFrenteTras = 20; // posicao inicial 
int posicaoGarra = 100; // posicao inicial 

Servo motorBase;
Servo motorSobeDesce;
Servo motorFrenteTras;
Servo motorGarra;

void statusMotores(){
    Serial.print("Base: ");
    Serial.print(posicaoBase);
    Serial.print("  Sobe/Desce: ");
    Serial.print(posicaoSobeDesce);
    Serial.print("  Frente/Tras: ");
    Serial.print(posicaoFrenteTras);
    Serial.print("  Garra: ");
    Serial.println(posicaoGarra);
}

void ligarTudo(){
  motorBase.attach(D5);
  motorSobeDesce.attach(D6);
  motorFrenteTras.attach(D7);
  motorGarra.attach(D8);
}

void desligarTudo(){
  motorBase.detach();
  motorSobeDesce.detach();
  motorFrenteTras.detach();
  motorGarra.detach();
}

void setup() {
  // initialize serial:
  Serial.begin(115200);
  // reserve 200 bytes for the inputString:
  fraseRecebida.reserve(200);

  desligarTudo();
    
  motorBase.write(posicaoBase);
  motorSobeDesce.write(posicaoSobeDesce);
  motorFrenteTras.write(posicaoFrenteTras);
  motorGarra.write(posicaoGarra);

  Serial.println("...");
  Serial.println("Começou");
  statusMotores();
}

void loop() {
  // print the string when a newline arrives:
  if (fraseCompleta) {
    if(fraseRecebida.startsWith("base")){
      posicaoBase = fraseRecebida.substring(4).toInt();

      // limita o servo a ter de 0 a 180 graus
      if(posicaoBase > 180) posicaoBase = 180;
      else if(posicaoBase <=0) posicaoBase = 0;

      //Serial.println(posicaoBase);

      // move o servo
      motorBase.write(posicaoBase);
      
    } else if(fraseRecebida.startsWith("sobe")){
      posicaoSobeDesce = fraseRecebida.substring(4).toInt();

      // limita o servo a ter de 0 a 180 graus
      if(posicaoSobeDesce > 180) posicaoSobeDesce = 180;
      else if(posicaoSobeDesce <=0) posicaoSobeDesce = 0;

      //Serial.println(posicaoSobeDesce);

      // move o servo
      motorSobeDesce.write(posicaoSobeDesce);
      
    }else if(fraseRecebida.startsWith("frente")){
      posicaoFrenteTras = fraseRecebida.substring(6).toInt();

      // limita o servo a ter de 0 a 180 graus
      if(posicaoFrenteTras > 180) posicaoFrenteTras = 180;
      else if(posicaoFrenteTras <=0) posicaoFrenteTras = 0;

      //Serial.println(posicaoFrenteTras);

      // move o servo
      motorFrenteTras.write(posicaoFrenteTras);
      
    }else if(fraseRecebida.startsWith("garra")){
      posicaoGarra = fraseRecebida.substring(5).toInt();

      // limita o servo a ter de 0 a 180 graus
      if(posicaoGarra > 180) posicaoGarra = 180;
      else if(posicaoGarra <=0) posicaoGarra = 0;

      //Serial.println(posicaoGarra);

      // move o servo
      motorGarra.write(posicaoGarra);
    }else if(fraseRecebida.startsWith("ligar")){
      ligarTudo();
    }else if(fraseRecebida.startsWith("desligar")){
      desligarTudo();
    }
    
    statusMotores();
     
    fraseRecebida = "";
    fraseCompleta = false;
  }

  while(Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    fraseRecebida += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      fraseCompleta = true;
    }
  }
}
