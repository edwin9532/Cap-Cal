# -*- coding: utf-8 -*-
"""
Created on Sun Jun 11 09:37:57 2023

@author: elave
"""

import serial
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


# Set up for the data
filename = 'data.csv'

ser = serial.Serial('COM3', 9600)
print('Connection established')
file = open(filename, "w")
print('Data file created')


# Setting up the molar masses

symbols = ['Al','Cu','Fe']
materials = ['Aluminio','Cobre','Hierro']
mol_masses = [26.98153860, 63.546, 55.845]

while True:
    print('Por favor escriba el simbolo atómico del material de la muestra que desea utilizar:')
    symbol = input()
    if symbol in symbols:
      ind = symbols.index(symbol)
      ma1, material = mol_masses[ind], materials[ind]
      print(f'Se ha seleccionado el elemento {material} ({symbol}) con éxito')
      ser.write('sample_set'.encode())      
      break
    else:
      print('Lo que ha introducido no es válido, o el elemento no está disponible')
      continue

# ---------------------------------- CONSTANTS ----------------------------------

L = 199 # Latent heat of N [J/g]
TN = 77 # N temperature [K]
T0 = 296.15 # Ambient temp [K]
R = 8.31446261815324 # [J/(K mol)]
DeltaT = T0 - TN # temperature's difference

err_mass = 0.1
err_T = 1

# High number to avoid problems
p_sample_down = 10000



# ---------------------------------- FUNCTIONS ----------------------------------

# Calculate derivatives
def central_diff(x, y):
    d = (y[2:] - y[:-2])/(x[2:] - x[:-2])
    return d

# Find time of Leidenfrost
def Leiden(d):
    if (-0.125 < d[-1] < 0 and -0.125 < d[-2] < 0 and -0.125 < d[-3] < 0 and -0.125 < d[-4] < 0 and -0.125 < d[-5] < 0 ): # Small range around the expected value
        leiden = True
    else:
        leiden = False
    return leiden

# Finds when the slopes are high, for knowing when the mass entered
def slope_change(d):
    if (d[-1] > 0.3 and d[-2] > 0.3 and d[-3] > 0.3):
        return True
    else: return False

# Linear function
def linearf(x, a, b):
    y = a + b*x
    return y

# Evaluate the linear regression at point x
def fopt(x,popt):
    return popt[0] + popt[1]*x

# Generate a plot with all the collected data and the regressions
def final_plot(t,m,popt1,popt2,c,delta_c):
    plt.plot(t_array[::4],m_array[::4],'ko',label="Datos Experimentales",mfc="white")
    plt.grid()
    plt.minorticks_on()
    ax1 = plt.gca()
    fig1 = plt.gcf()
    
    # Fits
    ax1.plot(t_array[::4],fopt(t_array[::4],popt1),'b--',label = 'Ajuste lineal $t\leq ${} s \n$R^2$ = {:.4f}'.format(t_sample_in,R2_1))
    ax1.plot(t_array[::4],fopt(t_array[::4],popt2),'r--',label = 'Ajuste lineal $t\geq ${} s \n$R^2$ = {:.4f}'.format(t_leiden,R2_2))
    
    # Arrow for t_avg
    down = (fopt(t_avg,popt2)-m_array[p_leiden:].min()+1)/(m_array.max()+2-m_array[p_leiden:].min())
    up = (fopt(t_avg,popt1)-m_array[p_leiden:].min()+1)/(m_array.max()+2-m_array[p_leiden:].min())
    
    
    ax1.set_xlim(0,t[-1]+1)
    ax1.set_ylim(min(m_array)-1, max(m_array)+1)
    ax1.fill_betweenx([m_array.min()-5, m_array.max()+5], t_sample_in, t_leiden, alpha=.2, color='gray', linewidth=0)
    ax1.axvline(x = t_sample_in, color = 'gray')
    ax1.axvline(x = t_leiden, color = 'gray')
    ax1.axvline(x = t_avg, ymin = down, ymax = up, color = 'g',label="$\langle t \\rangle$")
    ax1.arrow(t_avg,fopt(t_avg,popt2),0,m_array[p_leiden:].min()-1-fopt(t_avg,popt2), length_includes_head=True, head_width=5, head_length=1, color='g', linewidth=1)
    
    lg=ax1.legend(bbox_to_anchor=(0, -0.20), loc='upper left')
    ax1.set_xlabel("Tiempo [s]", fontsize = 14)
    ax1.set_ylabel("Masa [g]",fontsize = 14)
    ax1.set_title(f'Muestra de {material}, Capacidad Calorífica: c = {round(c,2)}$\pm${round(delta_c,2)}')
    
    plt.savefig('data.pdf',dpi=400,bbox_inches='tight')
    plt.show()

# Plot set up
fig, ax = plt.subplots(figsize=(9, 6))
line, = ax.plot([], [], 'ko', mfc='white')

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_xlabel('Tiempo [s]', fontsize = 14)
ax.set_ylabel('Masa [g]', fontsize = 14)
ax.set_title(f'Muestra de {material}')
ax.grid()
ax.minorticks_on()

plt.ion()  # Turn on interactive mode

t, m = [], [] # Lists for the sensor data
find_leiden = False # Bool to know when to start searching for Leiden
done = False # Bool for knowing if the data has been modified by the sample mass


#p_leiden = 750


# ---------------------------------- MAIN LOOP ----------------------------------
while True:
    signal = ser.readline().decode().strip()
    # Get the sample mass that is sent from the arduino
    if signal == 'sample':
        sample_mass = float(ser.readline().decode().strip())
        
    if signal == 'start':
        data = ser.readline().decode().strip()
        while data != 'end':
            
            # Add the sample mass to the data previous to the sample entering the N
            if len(t) > 10:
                if np.array(t)[-1]>20:
                    t_array = np.array(t)
                    m_array = np.array(m)
                    d = central_diff(t_array[-20::4],m_array[-20::4]) # Calculate derivatives of the data
                    if slope_change(d) and not done:
                        done = True
                        p_sample_in = len(t)-16
                        t_sample_in = t[-16]
                        for ts in range(p_sample_in+1):
                            m[ts] = m[ts] + sample_mass
            
            # Sample has gone in
            if data == 'in': # Signal for when the mass is submerged / motor has finished turning
                #print('Sample in')
                find_leiden = True # Activates Leiden search
                p_sample_down = len(t) - 1 # Saves position at which this happened
                t_sample_down = t[-1] # Saves time at which this happened ~
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
            if (find_leiden and len(t) > p_sample_down + 100): # At least 10 seconds after the sample went in (??)
                t_array = np.array(t)
                m_array = np.array(m)
                d = central_diff(t_array[p_sample_down::4],m_array[p_sample_down::4]) # Calculate derivatives of the data
                if Leiden(d): # Leiden happens
                    p_leiden = len(t) - 4 # position on t at which it happened
                    t_leiden = t[-4] # t value at which it happened
                    find_leiden = False
                    print('Leidenfrost moment detected')
                    ser.write('leiden'.encode()) # Tell arduino it has happened
            
            # Plot
            line.set_data(t[::4], m[::4])  # Update the line with new data
            ax.set_xlim(0,t[-1]+.5)
            ax.set_ylim(max(0,min(m)-5), max(m)+5)
            plt.pause(0.01)  # Pause for a short interval to allow the plot to update

            data = ser.readline().decode().strip()
            print(data)

        t_array = np.array(t)
        m_array = np.array(m)
        
        
        
            
        # Data gathering has ended now. Calculate heat capacity
        
        # Linear fit for zone 1
        popt1, pcov1 = curve_fit(linearf, xdata = t_array[:p_sample_in+1], ydata = m_array[:p_sample_in+1])
        perr1 = np.sqrt(np.diag(pcov1))
        R2_1 = 1-((np.sum((fopt(t_array[:p_sample_in],popt1)-m_array[:p_sample_in])**2))/(np.var(m_array[:p_sample_in])*m_array[:p_sample_in].shape[0])) #If we want this, modify df1
        
        # Linear fit for zone 3
        popt2, pcov2 = curve_fit(linearf, xdata = t_array[p_leiden:], ydata = m_array[p_leiden:])
        perr2 = np.sqrt(np.diag(pcov2))
        R2_2 = 1-((np.sum((fopt(t_array[p_leiden:],popt2)-m_array[p_leiden:])**2))/(np.var(m_array[p_leiden:])*m_array[p_leiden:].shape[0])) #If we want this, modify df1
        
        # Midpoint of zone 2
        t_avg = 0.5*(t_sample_in + t_leiden)
        
        # Change in mass
        deltaM = fopt(t_avg,popt1)-fopt(t_avg,popt2)
        err_deltaM = (perr1[0]+perr1[1]*t_avg)+(perr2[0]+perr2[1]*t_avg)
        # Heat capacity
        c = (deltaM * L)/(sample_mass/ma1 * DeltaT)
        delta_c = c*(err_deltaM/deltaM + err_mass/sample_mass + err_T/DeltaT)
        
        # Send the c value to the arduino
        ser.write((str(round(c,2))+'+-'+str(round(delta_c,2))).encode())
        
        final_plot(t,m,popt1,popt2,c,delta_c)
        #while True:
        #    data = ser.readline().decode().strip()
        #    if data == 'plot':
        #        
                # Plot graph with all the fancy stuff
        #        final_plot(t,m,popt1,popt2,c,delta_c)
    
        break


ser.close()
file.close()

plt.ioff()  # Turn off interactive mode
plt.show()
