// cd miniconda3/envs/dig/cap-cal/

#include <HX711_ADC.h> // https://github.com/olkal/HX711_ADC
#include <Wire.h>
#include <LiquidCrystal_I2C.h> // LiquidCrystal_I2C library
#include <Stepper.h>

HX711_ADC LoadCell(4, 5); // dt pin, sck pin
LiquidCrystal_I2C lcd(0x3F, 16, 2); // LCD HEX address 0x27

int button = 7; // Button pin
int buttonval; // To store state of the button
int prev_buttonval; // To store state of the button

unsigned long initMillis; // to store initial time
unsigned long tstop = 100000; // 30 * 60 * 1000; // large time to avoid the data meas. to stop
unsigned long dT = 10000; // time for zone 1 and 3

float sample_mass;
bool start = true; // Gives set-up condition
bool sample_up = true; // Tells if the sample is above(true) or below(false)
bool Leidenfrost = false; // To be removed - maybe
bool d = false; // To be removed

int stepsPerRevolution = 2048;
int motSpeed = 16; // rpm
int stepper = 13; // Pin for connecting or not the stepper
Stepper myStepper(stepsPerRevolution,8,10,9,11);

// Declare functions to have the default parameters
void lcd_print(char text[17], int column, int row, bool clear = false);
void stepper_move(int dir, int revs = 6, bool data = false);


void setup() {
  Serial.begin(9600);
  LoadCell.begin(); // start connection to HX711
  LoadCell.start(1000); // load cells gets 1000ms of time to stabilize

  LoadCell.setCalFactor(2435.09); // Calibration factor previously determined
  myStepper.setSpeed(motSpeed); // Set motor speed

  pinMode(button, INPUT_PULLUP); // Establish button pin
  pinMode(stepper, OUTPUT); // Setting stepper pin as output
  
  lcd.init();
  lcd.backlight();

  lcd_print("Experimento",2,0);
  lcd_print("Cap. Calorifica",0,1);

  delay(3000);
  lcd.clear();
}

// Function to reduce lcd commands
void lcd_print(char text[17], int column, int row, bool clear = false){
  if (clear){lcd.clear();}
  lcd.setCursor(column, row);
  lcd.print(text);
}

// Function that will print the data on both the lcd and the serial
void print_data(){
  LoadCell.update();
  float data = LoadCell.getData();
  unsigned long currentMillis = millis();

  if (sample_up){
    data = data + sample_mass;
  }

  lcd_print("Tiempo: Masa:",0,0,true);
  float time = ((float)currentMillis-(float)initMillis)/1000; // Elpased time since beginning of the exp.
  lcd.setCursor(2, 1);
  lcd.print(time,0);
  lcd.print("s");
  lcd.setCursor(9, 1);
  lcd.print(data,1);
  lcd.print("g");
  
  Serial.print(time,1);
  Serial.print(",");
  Serial.println(data,1);
}

// Function that moves the stepper motor
void stepper_move(int dir, int revs = 6, bool data = false){
  digitalWrite(stepper,1);
  int total_steps = revs * stepsPerRevolution; // total steps to be taken
  int tiny_step = 48; // "step quanta", divide the full revs in tiny steps to allow for other tasks, while keeping the stepper movement continuous

  if (data){ // This is to allow the option for the stepper to turn a high number of times, without stopping the printing of data
    int step_packet = total_steps / tiny_step; // amount of tiny_steps that will be taken
    for (int i = 1; i <= step_packet; i++){
      unsigned long t_ = millis();
      myStepper.step(dir * tiny_step);
      print_data();
      unsigned long t = millis(); //130ms
    }
  }
  else{
    myStepper.step(dir * total_steps);
  }
  digitalWrite(stepper,0);
}

// Function to set-up the experiment
float init_(){
  float data_prev = 200;
  char datat[7];

  
  // lcd_print("¿De que material",0,0,true);
  // lcd_print("es la muestra?",1,1);

  // Obtain sample mass
  while (true){
    LoadCell.update();
    float data = LoadCell.getData();
    if (data < 10){
      lcd_print("Colocar muestra",0,0);
      lcd_print("sobre la balanza",0,1);
    }
    else if (data > 10 && data == data_prev){ // Detects if the sample is on the scale
      lcd_print("Masa de muestra:",0,0,true);
      dtostrf(data, 4, 1, datat);
      lcd_print(datat,6,1);
      lcd.print("g");
      sample_mass = data;
      Serial.println("sample"); // Tell py to listen for the sample mass
      Serial.println(sample_mass);
      delay(3000);
      break;
    }
    data_prev = data;
    delay(100);
  }

  // Lifting the sample
  while (true){
    lcd_print("Presione el",2,0,true);
    lcd_print("boton",5,1);

    buttonval = digitalRead(button);
    if (buttonval==0 && prev_buttonval==1){
      lcd_print("Subiendo muestra",0,0,true);
      stepper_move(1);
      break;
    }
    prev_buttonval = buttonval;
    delay(100);
  }

  // Placing Nitrogen on the scale
  while (true){
    LoadCell.update();
    float data = LoadCell.getData();
    if (data < 200){
      lcd_print("Colocar nitrogeno",0,0,true);
      lcd_print("sobre la balanza",0,1);
    }
    else if (data > 200 && (data <= data_prev) ){ // Detects if the N is on the scale
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

  // Starting the experiment
  while (true){
    lcd_print("Presionar boton",0,0,true);
    lcd_print("para iniciar",2,1);

    buttonval = digitalRead(button);
    if (buttonval==0 && prev_buttonval==1){
      lcd_print("Iniciando...",0,0,true); // To be removed? - maybe
      delay(3000);
      LoadCell.update();
      break;
    }
    prev_buttonval = buttonval;
    delay(100);
  }
  return sample_mass;
}

void loop() {
  unsigned long currentMillis = millis();

  // Goes to set-up the experiment
  if (start){
    float sample_mass = init_();
    initMillis = millis();
    start = false;
    Serial.println("start");
  }

  // Listens for when py sends the Leidenfrost signal
  if (Serial.available() > 0){
    String incoming = Serial.readString();
    if (incoming == "leiden") {
      tstop = currentMillis + dT; // If python detects Leidenfrost, take data for dT more seconds
    }
  }

  // Temporary -- to activate leiden signal 85 seconds in
  // if (currentMillis > 85000 && d==false){
  //   Leidenfrost = true;
  //   d = true;
  // }

  // // To be modified -- should activate when .py sends a leiden signal
  // if (Leidenfrost){
  //   tstop = currentMillis + dT;
  //   Leidenfrost = false;
  // }

  // Lowers the sample when dT seconds have passed (from when the exp. started)
  if (currentMillis > initMillis + dT && sample_up){
    stepper_move(-1,3,true); // ######## removing the sample_mass from the mass readings when halfway through the lowering (?) TBC #########################
    sample_up = false;       // ######## Maybe just add it on the last 2 revs? Maybe use a function? ############################3
    stepper_move(-1,3,true);
    Serial.println("in");    // Let py know the sample has been submerged
  }

  if (currentMillis < tstop){ // takes data
    print_data();
    delay(100);
  }
  else{
    Serial.println("end");
    lcd_print("La toma de datos",0,0,true);
    lcd_print("ha concluido",2,1);
    stepper_move(1);
    LoadCell.update();
    float mass = LoadCell.getData();
    while (mass>1){
    lcd_print("Por favor retire",0,0,true);
    lcd_print("el nitrogeno",2,1);
    delay(200);
    LoadCell.update();
    mass = LoadCell.getData();
    }
    stepper_move(-1);
    
    // Listens for py sending the calculated heat capacity
    if (Serial.available() > 0){
    String c = Serial.readString();
    while (true){
      lcd_print("Cap. calorifica:",0,0,true);
      lcd.setCursor(0, 1);
      lcd.print(c);
      }
    }
    // while (true){
    //   lcd_print(":)",7,1,true);
    // }
  }
}
