#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x3F,16,2);


void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
}

// void loop() {

//   if(Serial.available()){  
//     delay(100);
//     lcd.clear();
//     lcd.setCursor(0,1);

//     while(Serial.available() > 0){
//       msg = Serial.readString();
//       if (msg == "now"){
//         uint8_t data[17];
//         msg.StringToCharArray(data,17)
//         lcd.write(data);
//       }
//       // lcd.write()
//     }
//   }
// }

void loop() {
  if (Serial.available() > 0) {
    String message = Serial.readString();
    if (message == "now") {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print(message);
    }
  }
}
