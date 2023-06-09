#include <HX711_ADC.h> // https://github.com/olkal/HX711_ADC


int analogPin = 3;     
// int data = 0;           
char userInput;
// char msg = "go";

HX711_ADC LoadCell(4, 5); // dt pin, sck pin

void setup(){
  LoadCell.begin(); // start connection to HX711
  LoadCell.start(1000); // load cells gets 1000ms of time to stabilize

  LoadCell.setCalFactor(2435.09); // Calibarate your LOAD CELL with 100g weight, and change the value according to readings

  Serial.begin(9600);                        //  setup serial
}

void loop(){

if(Serial.available()){ 
    
    userInput = Serial.read();               // read user input

    LoadCell.update(); // retrieves data from the load cell
    float data = LoadCell.getData(); // get output value

    // data = analogRead(analogPin);    // read the input pin
    Serial.println(data);            
    delay(10);  // delay in between reads for stability
            
  } // Serial.available
} // Void Loop