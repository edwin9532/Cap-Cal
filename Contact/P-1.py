import serial

port = 'COM3'
baud_rate = 9600

Arduino = serial.Serial(port,baud_rate,timeout=1)

while True:
    #msg = input().encode()
    if input() == 'a':
        print('try')
        Arduino.write("now".encode())
        print('sent')
    #c = 20
    #delta_c = 4
    #Arduino.write(f'{c}+-{delta_c}'.encode())
    #Arduino.write('leiden'.encode())