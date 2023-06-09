# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 10:05:52 2023

@author: elave
"""

import serial

filename = 'data.csv'

ser = serial.Serial('COM3',9600)
print('Connection established')
file = open(filename, "w")
print('Data file created')

while True:
    signal = str(ser.readline())[2:-5]
    if signal == "start":
        print('Commencing data gathering...')
        
        signal = str(ser.readline())[2:-5]
        while signal != "end":
            data = signal
            print(data)
            
            file = open(filename, "a")
            
            file.write(data + "\n")
            
            signal = str(ser.readline())[2:-5]
        
        ser.close()
        file.close()
        print('The data has been collected.')
        break
    break
