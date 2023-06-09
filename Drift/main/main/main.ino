#include <HX711_ADC.h> // https://github.com/olkal/HX711_ADC
#include <Wire.h>
#include <LiquidCrystal_I2C.h> // LiquidCrystal_I2C library

void lcd_print(char text[17], int column, int row, bool clear = false);

HX711_ADC LoadCell(4, 5); // dt pin, sck pin
LiquidCrystal_I2C lcd(0x3F, 16, 2); // LCD HEX address 0x27

int button = 8;
int buttonval;
int prev_buttonval;
bool measuring = false;
unsigned long initMillis;
float sample_mass;
bool start = true;

void setup() {

  Serial.begin(9600);
  LoadCell.begin(); // start connection to HX711
  LoadCell.start(1000); // load cells gets 1000ms of time to stabilize

  LoadCell.setCalFactor(2435.09);

  pinMode(button, INPUT_PULLUP);
  
  lcd.init();
  lcd.backlight();

  lcd_print("Experimento",2,0);
  lcd_print("Cap. Calorifica",0,1);

delay(3000);
lcd.clear();
}

// Función para reducir los comandos del lcd
void lcd_print(char text[17], int column, int row, bool clear = false){
  if (clear){
  lcd.clear();
  }
  lcd.setCursor(column, row);
  lcd.print(text);
}

// Función de 'set-up', empieza el exp.
float init_(){
  float data_prev = 200;
  char datat[7];
  // Obteniendo masa de la muestra
  while (true){
    LoadCell.update();
    float data = LoadCell.getData();
    if (data < 10){
      lcd_print("Colocar muestra",0,0);
      lcd_print("sobre la balanza",0,1);
    }
    else if (data > 10 && data == data_prev){
      lcd_print("Masa de muestra:",0,0,true);
      dtostrf(data, 4, 1, datat);
      lcd_print(datat,6,1);
      lcd.print("g");
      sample_mass = data;
      delay(3000);
      break;
    }
    data_prev = data;
    delay(100);
  }

  // Subiendo la muestra
  while (true){
    lcd_print("Presione el",2,0,true);
    lcd_print("boton",5,1);

    buttonval = digitalRead(button);
    if (buttonval==0 && prev_buttonval==1){
      lcd_print("Subiendo muestra",0,0,true);
      // Función que hace que el motor se mueva
      delay(2000);
      break;
    }
    prev_buttonval = buttonval;
    delay(100);
  }

  //Colocando el nitrógeno
  while (true){
    LoadCell.update();
    float data = LoadCell.getData();
    if (data < 200){
      lcd_print("Colocar nitrogeno",0,0,true);
      lcd_print("sobre la balanza",0,1);
    }
    else if (data > 200 && (data <= data_prev) ){ //detecta si el N ya está sobre la balanza
      lcd_print("Nitrogeno",3,0,true);
      lcd_print("Detectado ",0,1);
      lcd.print(data,1);
      lcd.print("g");
      delay(3000);
      break;
    }
    data_prev = data;
    delay(200);
  }

  while (true){
    lcd_print("Presionar boton",0,0,true);
    lcd_print("para iniciar",2,1);

    buttonval = digitalRead(button);
    if (buttonval==0 && prev_buttonval==1){
      lcd_print("Iniciando...",0,0,true);
      delay(3000);
      break;
    }
    prev_buttonval = buttonval;
    delay(100);
  }
  return sample_mass;
}


void loop() {
  if (start){
    float sample_mass = init_();
    initMillis = millis();
    start = false;
  }

  LoadCell.update();
  float data = LoadCell.getData();
  unsigned long currentMillis = millis();

  lcd_print("Tiempo: Masa:",0,1,true);
  float time = ((float)currentMillis-(float)initMillis)/1000;
  lcd.setCursor(2, 1);
  lcd.print(time,0);
  lcd.print("s");
  lcd.setCursor(9, 1);
  lcd.print(data, 1);
  lcd.print("g");
  
  Serial.print(time,1);
  Serial.print(",");
  Serial.println(data);

  delay(100);
}
