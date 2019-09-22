#include <Servo.h>
#include <ESP8266WiFi.h>//Biblioteca do WiFi.
#include <WiFiUdp.h>//Biblioteca do UDP.
 
WiFiUDP Udp;//Cria um objeto da classe UDP.

//*** Soft Ap variables ***
const char *APssid = "Robo Mil Grau";
const char *APpassword = ""; // No password for the AP
IPAddress APlocal_IP(192, 168, 4, 1);
IPAddress APgateway(192, 168, 4, 1);
IPAddress APsubnet(255, 255, 255, 0);

//***UDP Variables***
unsigned int localUdpPort = 1234;
char recebidoUDP[255];
char respostaUDP[] = "Recebi uma mensagem :-)";

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

void iniciaWifi(){
  WiFi.mode(WIFI_AP);//Define o ESP8266 como Acess Point.
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
}

void controlaRobo(){
  // print the string when a newline arrives:
  if (fraseCompleta) {
    if(fraseRecebida.startsWith("base")){
      posicaoBase = fraseRecebida.substring(4).toInt();

      // limita o servo a ter de 0 a 180 graus
      if(posicaoBase > 180) posicaoBase = 180;
      else if(posicaoBase <=0) posicaoBase = 0;

      // move o servo
      motorBase.write(posicaoBase);
      
    } else if(fraseRecebida.startsWith("sobe")){
      posicaoSobeDesce = fraseRecebida.substring(4).toInt();

      // limita o servo a ter de 0 a 180 graus
      if(posicaoSobeDesce > 180) posicaoSobeDesce = 180;
      else if(posicaoSobeDesce <=0) posicaoSobeDesce = 0;

      // move o servo
      motorSobeDesce.write(posicaoSobeDesce);
      
    }else if(fraseRecebida.startsWith("frente")){
      posicaoFrenteTras = fraseRecebida.substring(6).toInt();

      // limita o servo a ter de 0 a 180 graus
      if(posicaoFrenteTras > 180) posicaoFrenteTras = 180;
      else if(posicaoFrenteTras <=0) posicaoFrenteTras = 0;

      // move o servo
      motorFrenteTras.write(posicaoFrenteTras);
      
    }else if(fraseRecebida.startsWith("garra")){
      posicaoGarra = fraseRecebida.substring(5).toInt();

      // limita o servo a ter de 0 a 180 graus
      if(posicaoGarra > 180) posicaoGarra = 180;
      else if(posicaoGarra <=0) posicaoGarra = 0;

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
}

void verificaMensagensSerial(){
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

void verificaMensagensWifi(){
  int packetSize = Udp.parsePacket();
   if (packetSize)
   {
     // receive incoming UDP packets
     //Serial.printf("Received %d bytes from %s, port %d\n", packetSize, Udp.remoteIP().toString().c_str(), Udp.remotePort());
     int len = Udp.read(recebidoUDP, 255);
     if (len > 0)
     {
     recebidoUDP[len] = 0;
     }
     Serial.printf("UDP packet contents: %s\n", recebidoUDP);
  
     String message = String(recebidoUDP);
     fraseRecebida = message;
    
     // send back a reply, to the IP address and port we got the packet from
     Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
     Udp.write(respostaUDP);
     Udp.endPacket();

     fraseCompleta = true;
   }
}

void setup() {
  // initialize serial:
  Serial.begin(115200);

  iniciaWifi();
  
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
  verificaMensagensWifi();
  verificaMensagensSerial();
  controlaRobo();
}
