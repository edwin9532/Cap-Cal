import serial

port = 'COM3'
baud_rate = 9600

Arduino = serial.Serial(port,baud_rate,timeout=1)

while True:
    msg = input().encode()
    Arduino.write(msg)