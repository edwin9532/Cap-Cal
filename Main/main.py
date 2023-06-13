# -*- coding: utf-8 -*-
"""
Created on Sun Jun 11 09:37:57 2023

@author: elave
"""

import serial
import matplotlib.pyplot as plt


# Set up for the data
filename = 'data5.csv'

ser = serial.Serial('COM3', 9600)
print('Connection established')
file = open(filename, "w")
print('Data file created')

# Set up for heat capacity

ma1 = 112.4110 # masa molar [g/mol]

L = 199 # Latent heat of N [J/g]
TN = 77 # N temperature [K]
T0 = 296.15 # Ambient temp [K]
R = 8.31446261815324 # [J/(K mol)]
DeltaT = T0 - TN # temperature's difference

err_mass = 0.1
err_T = 1



# ---------------------------------- FUNCTIONS ----------------------------------

# Calculate derivatives
def central_diff(x, y):
    d = (y[2:] - y[:-2])/(x[2:] - x[:-2])
    return d

# Find time of Leidenfrost
def Leiden(d):
    # Maybe make the -0.11 value a variable? depending on the actual behaviour we see on the tests
    # Leiden
    if (-0.11 < d[-1] < 0 and -0.11 < d[-2] < 0 and -0.11 < d[-3] < 0):
        leiden = True
    else:
        leiden = False        
    return leiden

# Linear function
def linearf(x, a, b):
    y = a + b*x
    return y

# Evaluate the linear regression at point x
def fopt(x,popt):
    return popt[0] + popt[1]*x



# Plot set up
# This as a function?
fig, ax = plt.subplots(figsize=(10, 6))
line, = ax.plot([], [], 'ko', mfc='white')

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_xlabel('Tiempo [s]')
ax.set_ylabel('Masa [g]')
ax.grid()
ax.minorticks_on()

plt.ion()  # Turn on interactive mode




t, m = [], [] # Lists for the sensor data
find_leiden = False # Bool to know when to start searching for Leiden

# ---------------------------------- MAIN LOOP ----------------------------------
while True:
    signal = ser.readline().decode().strip()
    # Get the sample mass that is sent from the arduino
    if signal == 'sample':
        sample_mass = ser.readline().decode().strip()
        
    if signal == 'start':
        data = ser.readline().decode().strip()
        while data != 'end':
            
            # Sample has gone in
            if data == 'in': # Signal for when the mass is submerged
                find_leiden = True # Activates Leiden search
                p_sample_down = len(t) - 1 # Saves position at which this happened ###########################
                t_sample_down = t[-1] # Saves time at which this happened
                data = ser.readline().decode().strip()
                continue
            
            file = open(filename, "a")
            file.write(data + "\n") # Save data to the csv
            
            newt = float(data[:data.find(',')])
            newm = float(data[data.find(',') + 1:])
            
            # Data
            t.append(newt)
            m.append(newm)
            
            # Leidenfrost moment
            if (find_leiden and len(t) > p_sample_down + 9): # At least a second after the sample went in (??)
                d = central_diff(t[p_sample_down:],m[p_sample_down:]) # Calculate derivatives of the data
                if Leiden(d): # Leiden happens
                    p_leiden = len(t) - 4 # position on t at which it happened
                    t_leiden = t[-4] # t value at which it happened
                    find_leiden = False
                    serial.write('leiden'.encode()) # Tell arduino it has happened
            
            # Plot
            line.set_data(t[::4], m[::4])  # Update the line with new data
            ax.set_xlim(0,t[-1]+.5)
            ax.set_ylim(max(0,min(m)-5), max(m)+5)
            plt.pause(0.01)  # Pause for a short interval to allow the plot to update

            data = ser.readline().decode().strip()
            print(data)
            
        # Data gathering has ended now. Calculate heat capacity
        
        # Linear fit for zone 1
        popt1, pcov1 = curve_fit(linearf, xdata = t[:p_sample_down+1], ydata = m[:p_sample_down+1])
        perr1 = np.sqrt(np.diag(pcov1))
        # R2_1 = 1-((np.sum((fopt1_1(df1_1[:,0])-df1_1[:,1])**2))/(np.var(df1_1[:,1])*df1_1.shape[0])) If we want this, modify df1
        
        # Linear fit for zone 3
        popt2, pcov2 = curve_fit(linearf, xdata = t[p_leiden:], ydata = m[p_leiden:])
        perr2 = np.sqrt(np.diag(pcov2))
        # R2_2 = 1-((np.sum((fopt1_2(df1_2[:,0])-df1_2[:,1])**2))/(np.var(df1_2[:,1])*df1_2.shape[0])) If we want this, modify df1
        
        # Midpoint of zone 2
        t_avg = 0.5*(t_sample_down + t_leiden) 
        
        # Change in mass
        deltaM = fopt(t_avg,popt1)-fopt(t_avg,popt2)
        err_deltaM = (perr1[0]+perr1[1]*t_avg)+(perr2[0]+perr2[1]*t_avg)
        # Heat capacity
        c = (deltaM * L)/(sample_mass/ma1 * DeltaT)
        delta_c = c*(err_deltaM/deltaM + err_mass/sample_mass + err_T/DeltaT)
        
        serial.write(str(c)+'+-'+str(delta_c))
        
    break


ser.close()
file.close()

plt.ioff()  # Turn off interactive mode
plt.show()
