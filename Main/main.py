# -*- coding: utf-8 -*-
"""
Created on Sun Jun 11 09:37:57 2023

@author: elave
"""

import serial
import matplotlib.pyplot as plt

filename = 'data5.csv'

ser = serial.Serial('COM3', 9600)
print('Connection established')
file = open(filename, "w")
print('Data file created')

fig, ax = plt.subplots(figsize=(10, 6))
line, = ax.plot([], [], 'ko', mfc='white')

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_xlabel('Tiempo [s]')
ax.set_ylabel('Masa [g]')
ax.grid()
ax.minorticks_on()

plt.ion()  # Turn on interactive mode

t, m = [], []

while True:
    signal = ser.readline().decode().strip()
    if signal == 'start':
        data = ser.readline().decode().strip()
        while data != 'end':
            print(data)
            
            file = open(filename, "a")
            file.write(data + "\n") # Save data to the csv
            
            newt = float(data[:data.find(',')])
            newm = float(data[data.find(',') + 1:])
            
            t.append(newt)
            m.append(newm)

            line.set_data(t[::4], m[::4])  # Update the line with new data
            ax.set_xlim(0,t[-1]+.5)
            ax.set_ylim(max(0,min(m)-5), max(m)+5)

            plt.pause(0.01)  # Pause for a short interval to allow the plot to update

            data = ser.readline().decode().strip()
    break


ser.close()
file.close()

plt.ioff()  # Turn off interactive mode
plt.show()
