# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 09:33:02 2023

@author: elave
"""

import time
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation


print("Initializing...")

ser = serial.Serial("COM3", 9600)                       # Establish Serial object with COM port and BAUD rate to match Arduino Port/rate
print("Connection established")
time.sleep(2)                                           # Time delay for Arduino Serial initialization 
dataList = []                                           # Create empty list variable for later use

while True:
    ser.write('go'.encode())                                     # Transmit the char 'g' to receive the Arduino data point
    print("Message sent to arduino")
    arduinoData_string = ser.readline().decode()
    print("Data received")
    
    arduinoData_float = float(arduinoData_string)   # Convert to float
    dataList.append(arduinoData_float)
    
    print( dataList[-1])

ser.close()                                             # Close Serial connection when plot is closed
