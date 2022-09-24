// use as portas D1 e D3 para o motor A, e D2 e D4 para o motor B.
#include <ESP8266WiFi.h> // Used for the soft AP
#include <WiFiUdp.h> // used for UDP comms.

int motorA_EN = D1;
int motorA_DIR = D3;

int motorB_EN = D2;
int motorB_DIR = D4;

int volante = 127;
int rodaEsquerda = 0;
int rodaDireita = 0;
int velocidadeMaxima = 600;

int velocid = 0;
bool giradOUe = false;

enum estadoAndar {
  andar,
  andando,
  parado
};

estadoAndar estadoAtualFrente = parado;
estadoAndar estadoAtualTras = parado;
estadoAndar estadoGirando = parado;

void initMotor();
void andarFrente();
void andarTras();

WiFiUDP Udp;

//*** Soft Ap variables ***
const char *APssid = "CARRINHOMILGRAU";
const char *APpassword = ""; // Sem senha
IPAddress APlocal_IP(192, 168, 4, 1);
IPAddress APgateway(192, 168, 4, 1);
IPAddress APsubnet(255, 255, 255, 0);

//***UDP Variables***
unsigned int localUdpPort = 12340;
char incomingPacket[255];
char replyPacket[] = "Respondendo!!";

void setup() {
 Serial.begin(115200); 
 
 WiFi.mode(WIFI_AP);
 
 Serial.println("ESP8266 AP & Station & UDP System test");
 // Configure the Soft Access Point. Somewhat verbosely... (for completeness sake)
 Serial.print("Soft-AP configuration ... ");
 Serial.println(WiFi.softAPConfig(APlocal_IP, APgateway, APsubnet) ? "OK" : "Failed!"); // configure network
 Serial.print("Setting soft-AP ... ");
 Serial.println(WiFi.softAP(APssid, APpassword) ? "OK" : "Failed!"); // Setup the Access Point
 Serial.print("Soft-AP IP address = ");
 Serial.println(WiFi.softAPIP()); // Confirm AP IP address

 // Setup the UDP port
 Serial.println("begin UDP port");
 Udp.begin(localUdpPort);
 Serial.print("local UDP port: ");
 Serial.println(localUdpPort );

 initMotor();
}

void loop() {
 andarFrente();
 andarTras();
 girar();

 int packetSize = Udp.parsePacket();
 if (packetSize)
 {
   // receive incoming UDP packets
   //Serial.printf("Received %d bytes from %s, port %d\n", packetSize, Udp.remoteIP().toString().c_str(), Udp.remotePort());
   int len = Udp.read(incomingPacket, 255);
   if (len > 0)
   {
   incomingPacket[len] = 0;
   }
   Serial.printf("UDP packet contents: %s\n", incomingPacket);

   String message = String(incomingPacket);
 
    if(message.startsWith("motor")){
      message = message.substring(5);
      if(message.startsWith("frente")){
        estadoAtualFrente = andar;
        message = message.substring(6);
      }else if(message.startsWith("tras")){
        estadoAtualTras = andar;
        message = message.substring(4);
      }
    }
    if(message.startsWith("servo")){
    
     int velocidadeReferencia = 1023; //255;
     volante = map((message.substring(5)).toInt(),36,120,0,velocidadeReferencia);
    
     int controleTipo = 1;

     int diferencialMaximo = 1023.0; // antigo 255.0
     if(controleTipo == 1){
       if(volante  > (diferencialMaximo/2)){
          Serial.print("Direita1");
          int novoVolante = volante - (diferencialMaximo/2);
          rodaDireita = diferencialMaximo;// 
          rodaEsquerda = map(volante, diferencialMaximo /2, diferencialMaximo, diferencialMaximo, 0);
     }else if(volante  <= (diferencialMaximo/2)){
          Serial.print("Esquerda2");
          rodaDireita = map(volante, 0, diferencialMaximo /2, 0, diferencialMaximo);
          rodaEsquerda = diferencialMaximo;// 
       } 
     } else if (controleTipo == 2){
        if(volante  > (255.0/2)){
          Serial.print("Direita3");
          int novoVolante = volante - (255.0/2);
          rodaEsquerda = 255.0 * (((255.0/2) - novoVolante)/(255.0/2));
          rodaDireita = 255 - rodaEsquerda;
       }else if(volante  <= (255.0/2)){
          Serial.print("Esquerda4");
          rodaDireita = 255.0 * (volante/(255.0/2));
          rodaEsquerda = 255.0 - rodaDireita;// * (volante/(255.0/2));
       }   
     }
     
     if(rodaDireita > velocidadeMaxima) rodaDireita = velocidadeMaxima;
     if(rodaEsquerda > velocidadeMaxima) rodaEsquerda = velocidadeMaxima;

     Serial.print(" volante:");
     Serial.print(volante);
     Serial.print(" esquerda: ");
     Serial.print(rodaEsquerda);
     Serial.print(" direita: ");
     Serial.println(rodaDireita);
    }

    if(message.startsWith("girad")){
     giradOUe = false;
     velocid = message.substring(5).toInt();
     estadoGirando = andar;
    }
    if(message.startsWith("girae")){
     giradOUe = true;
     velocid = message.substring(5).toInt();
     estadoGirando = andar;
    }
  
   // send back a reply, to the IP address and port we got the packet from
   Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
   Udp.write(replyPacket);
   Udp.endPacket();
 }
}

void initMotor(){
  pinMode(motorA_EN,OUTPUT);
  pinMode(motorA_DIR,OUTPUT);

  pinMode(motorB_EN,OUTPUT);
  pinMode(motorB_DIR,OUTPUT);

  digitalWrite(motorA_EN,LOW);
  digitalWrite(motorB_EN,LOW);
}

static unsigned long tempoOffsetS = 200;

void andarFrente(){

  static unsigned long tempoAtualFrente = 0;
  static unsigned long tempoOffsetFrente = tempoOffsetS;
  
  switch (estadoAtualFrente) {
    case parado:
      break;
    case andar:
      analogWrite(motorA_EN,rodaEsquerda);
      digitalWrite(motorA_DIR,HIGH);

      analogWrite(motorB_EN,rodaDireita);
      digitalWrite(motorB_DIR,HIGH);

      tempoAtualFrente = millis();
      estadoAtualFrente = andando;
      break;
    case andando:
       if(millis() > tempoAtualFrente + tempoOffsetFrente){
        analogWrite(motorA_EN,0);
        analogWrite(motorB_EN,0);
        estadoAtualFrente = parado;
       }
      break;
  }
}

void andarTras(){
  static unsigned long tempoAtualTras = 0;
  static unsigned long tempoOffsetTras = tempoOffsetS;//200;
  
  switch (estadoAtualTras) {
    case parado:
      
      break;
    case andar:
      analogWrite(motorA_EN, rodaEsquerda);
      digitalWrite(motorA_DIR,LOW);

      analogWrite(motorB_EN, rodaDireita);
      digitalWrite(motorB_DIR,LOW);
      
      tempoAtualTras = millis();
      estadoAtualTras = andando;
      break;
    case andando:
       if(millis() > tempoAtualTras + tempoOffsetTras){
        analogWrite(motorA_EN,0);
        analogWrite(motorB_EN,0);
        estadoAtualTras = parado;
       }
      break;
  }
}

void girar(){
  static unsigned long tempoAtualGira = 0;
  static unsigned long tempoOffsetGira = tempoOffsetS;//200;
  
  switch (estadoGirando) {
    case parado:
      
      break;
    case andar:
      if(giradOUe){
          analogWrite(motorA_EN,velocid);
          digitalWrite(motorA_DIR,LOW);
    
          analogWrite(motorB_EN,velocid);
          digitalWrite(motorB_DIR,HIGH);
      }else{
          analogWrite(motorA_EN,velocid);
          digitalWrite(motorA_DIR,HIGH);
    
          analogWrite(motorB_EN,velocid);
          digitalWrite(motorB_DIR,LOW);
      }
      tempoAtualGira = millis();
      estadoGirando = andando;
      break;
    case andando:
       if(millis() > tempoAtualGira + tempoOffsetGira){
        analogWrite(motorA_EN,0);
        analogWrite(motorB_EN,0);
        estadoGirando = parado;
       }
      break;
  }
}
