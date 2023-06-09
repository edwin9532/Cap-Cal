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
t=0


while t < 3000:
    data = str(ser.readline())
    data = data[2:][:-5]
    print(data)
    
    file = open(filename, "a")
    
    file.write(data + "\n")
    
    t+=1

print('3 minutes of data have been colected')
