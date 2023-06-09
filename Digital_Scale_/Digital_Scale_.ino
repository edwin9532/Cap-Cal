#include <HX711_ADC.h> // https://github.com/olkal/HX711_ADC
#include <Wire.h>
#include <LiquidCrystal_I2C.h> // LiquidCrystal_I2C library
HX711_ADC LoadCell(4, 5); // dt pin, sck pin
LiquidCrystal_I2C lcd(0x3F, 16, 2); // LCD HEX address 0x27


void setup() {

  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  // pinMode (taree, INPUT_PULLUP);
  LoadCell.begin(); // start connection to HX711
  LoadCell.start(1000); // load cells gets 1000ms of time to stabilize

  /////////////////////////////////////
  LoadCell.setCalFactor(2437.11); // Calibarate your LOAD CELL with 100g weight, and change the value according to readings
  /////////////////////////////////////
  
  lcd.init(); // begins connection to the LCD module
  lcd.backlight(); // turns on the backlight
  lcd.setCursor(1, 0); // set cursor to first row
  lcd.print("---------------"); // print out to LCD
  lcd.setCursor(0, 1); // set cursor to first row
  lcd.print("..............."); // print out to LCD

delay(3000);
lcd.clear();
}




void loop() { 
  lcd.setCursor(1, 0); // set cursor to first row
  lcd.print("Digital Scale "); // print out to LCD 
  LoadCell.update(); // retrieves data from the load cell
  float i = LoadCell.getData(); // get output value
  
  // In case of overload
  if (i>=1000)
  {
    i=0;
  lcd.setCursor(0, 0); // set cursor to secon row
  lcd.print("  Over Loaded   "); 
  lcd.setCursor(0, 1); // set cursor to secon row
  lcd.print("!!!!!!!!!!!!!!!!"); 
  delay(200);
  }

  lcd.setCursor(1, 1); // set cursor to second row
  lcd.print(i, 1); // print out the retrieved value to the second row
  lcd.print("g ");

  Serial.println(i);
  
  //###########################################################
  lcd.clear();
  delay(10);  // delay in between reads for stability




}
