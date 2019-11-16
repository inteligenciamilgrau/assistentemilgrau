int motorA_EN = D1;
int motorA_DIR = D3;

int motorB_EN = D2;
int motorB_DIR = D4;

void setup() {
  Serial.begin(115200);

  Serial.println("");
  Serial.println("Carrinho Mil Grau Iniciando!!");
  
  pinMode(motorA_EN, OUTPUT);
  pinMode(motorA_DIR, OUTPUT);
  pinMode(motorB_EN, OUTPUT);
  pinMode(motorB_DIR, OUTPUT);
}

void loop() {
  if(Serial.available()){
    char ler = Serial.read();

    if(ler == 'f'){
      digitalWrite(motorA_EN,HIGH);
      digitalWrite(motorA_DIR,HIGH);
    
      digitalWrite(motorB_EN,HIGH);
      digitalWrite(motorB_DIR,HIGH);
    
      delay(1000);
    
      digitalWrite(motorA_EN,LOW);
      digitalWrite(motorB_EN,LOW);
    }
    else if(ler == 't'){
      digitalWrite(motorA_EN,HIGH);
      digitalWrite(motorA_DIR,LOW);
    
      digitalWrite(motorB_EN,HIGH);
      digitalWrite(motorB_DIR,LOW);
    
      delay(1000);
    
      digitalWrite(motorA_EN,LOW);
      digitalWrite(motorB_EN,LOW);
    }
  }
  
}
