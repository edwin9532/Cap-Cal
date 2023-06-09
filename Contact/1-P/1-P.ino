#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x3F,16,2);

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
}

void loop() {

  if(Serial.available()){  
    delay(100);
    lcd.clear();
    lcd.setCursor(0,1);

    while(Serial.available() > 0){
      lcd.write(Serial.read());
    }
  }
}
