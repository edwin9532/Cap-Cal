#include <HX711_ADC.h> // https://github.com/olkal/HX711_ADC
#include <Wire.h>
#include <LiquidCrystal_I2C.h> // LiquidCrystal_I2C library

HX711_ADC LoadCell(4, 5); // dt pin, sck pin
LiquidCrystal_I2C lcd(0x3F, 16, 2); // LCD HEX address 0x27

int button = 7;
int buttonval;
int prev_buttonval;
bool measuring = false;
unsigned long previousMillis;

void setup() {

  Serial.begin(9600);
  LoadCell.begin(); // start connection to HX711
  LoadCell.start(1000); // load cells gets 1000ms of time to stabilize

  LoadCell.setCalFactor(2435.09);

  pinMode(button, INPUT_PULLUP);
  
  lcd.init(); // begins connection to the LCD module
  lcd.backlight(); // turns on the backlight
  lcd.setCursor(2, 0); // set cursor to first row
  lcd.print("Experimento"); // print out to LCD
  lcd.setCursor(0, 1); // set cursor to first row
  lcd.print("Cap. Calorifica"); // print out to LCD

delay(3000);
lcd.clear();
}


void loop() {
  
  LoadCell.update(); // retrieves data from the load cell
  float data = LoadCell.getData(); // get output value

  buttonval = digitalRead(button);

  if (buttonval == 0 && prev_buttonval==1 && measuring==false){
    
    lcd.setCursor(2, 0);
    lcd.print("Iniciando la");
    
    lcd.setCursor(0, 1);
    lcd.print("toma de datos.");
    delay(400);
    lcd.setCursor(0, 1);
    lcd.print("toma de datos..");
    delay(400);
    lcd.setCursor(0, 1);
    lcd.print("toma de datos...");
    delay(2000);

    lcd.clear();
    Serial.println("start");
    previousMillis = millis();
    measuring = true;
  }

  unsigned long currentMillis = millis();
  
  if (buttonval == 0 && prev_buttonval==1 && measuring==true && currentMillis > previousMillis+4000){
    Serial.println("end");
    measuring = false;

    lcd.setCursor(2, 0);
    lcd.print("Finalizando");
    lcd.setCursor(6, 1);
    lcd.print(".");
    delay(400);
    lcd.setCursor(6, 1);
    lcd.print("..");
    delay(400);
    lcd.setCursor(6, 1);
    lcd.print("...");
    delay(1500);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Se tomaron");
    
    lcd.setCursor(0, 1);
    lcd.print("datos por ");
    lcd.print(((float)currentMillis-(float)previousMillis)/1000, 1);
    lcd.print("s");

    delay(3000);
    lcd.clear();
  }


  // In case of overload
  if (data>=1000)
  {
    data=0;
  lcd.setCursor(0, 0);
  lcd.print("  Over Loaded   "); 
  lcd.setCursor(0, 1);
  lcd.print("!!!!!!!!!!!!!!!!"); 
  delay(200);
  }

  if (measuring){
    lcd.setCursor(0, 0);
    lcd.print(" Tiempo:  Masa:");

    lcd.setCursor(2, 1);
    lcd.print(((float)currentMillis-(float)previousMillis)/1000,1);
    lcd.print("s   ");
    lcd.print(data, 1);
    lcd.print("g");
    
    Serial.print(((float)currentMillis-(float)previousMillis)/1000,1);
    Serial.print(",");
    Serial.println(data);
  }
  else{
    lcd.setCursor(5, 0);
    lcd.print("Masa:");

    lcd.setCursor(5, 1);
    lcd.print(data, 1);
    lcd.print("g ");

  }

  prev_buttonval = buttonval;
  
  delay(100);
  lcd.clear();
}
