# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 17:22:30 2023

@author: elave
"""

import numpy as np
from scipy.optimize import curve_fit



dfma = np.linspace(10,10) ##### DATA HERE ############## [t,m]


def central_diff(x, y):
    d = (y[2:] - y[:-2])/(x[2:] - x[:-2])
    return d

d = central_diff(dfma[:,0],dfma[:,1])


# Finding Leiden
def Leiden(d):
    # Positions of a and b
    p1, p2 = 0, 0
    
    # Mass enters N
    for i in range(len(d)):
      if (d[i] <= -0.11 and d[i+2] < -0.11 and d[i+4] < -0.11):
        p1 = i 
        break
    # Leiden
    for i in range(len(d[p1:])):
      if (-0.11 < d[p1+i] < 0 and -0.11 < d[p1+i+2] < 0 and -0.11 < d[p1+i+4] < 0):
        p2 = p1+i
        break

    # Values of mass-lowering and Leiden
    a = dfma[:,0][p1]
    b = dfma[:,0][p2]
    
    return a, b

















##### Cálculo de la capacidad Calorífica


#Constants


m1 = 9.8      # masa [g]
ma1 = 112.4110 # masa molar [g/mol]

L = 199 # Calor latente del Nit. J/g
TN = 77 # Temp del Nit. K
T0 = 296.15 # Temp ambiente K 
R = 8.31446261815324 # J/(K mol)
DeltaT = T0 - TN # temperature's difference

err_mass = 0.1
err_T = 1




# Linear function
def linearf(x, a, b):
    y = a + b*x
    return y

# Fit 1
popt1, pcov1 = curve_fit(linearf, xdata = t[:p_sample_down+1], ydata = m[:p_sample_down+1])

# Evaluate the linear regression at point x
def fopt(x,popt):
    return popt[0] + popt[1]*x

perr1 = np.sqrt(np.diag(pcov1))
# R2_1 = 1-((np.sum((fopt1_1(df1_1[:,0])-df1_1[:,1])**2))/(np.var(df1_1[:,1])*df1_1.shape[0])) If we want this, modify df1

# Fit 2
popt2, pcov2 = curve_fit(linearf, xdata = t[p_leiden:], ydata = m[p_leiden:])

perr2 = np.sqrt(np.diag(pcov2))
# R2_2 = 1-((np.sum((fopt1_2(df1_2[:,0])-df1_2[:,1])**2))/(np.var(df1_2[:,1])*df1_2.shape[0])) If we want this, modify df1

t_avg = 0.5*(t_sample_down + t_leiden) 


# heat capacity
deltaM = fopt(t_avg,popt1)-fopt(t_avg,popt2)
err_deltaM = (perr1[0]+perr1[1]*t_avg)+(perr2[0]+perr2[1]*t_avg)
#print('Delta M = {:.2f} +- {:.2f} [g]'.format(deltaM,err_deltaM))
c = (deltaM * L)/(sample_mass/ma1 * DeltaT)
delta_c = c*(err_deltaM/deltaM + err_mass/sample_mass + err_T/DeltaT)
#print('El calor específico de la muestra, c = {:.3f} +- {:.3f} [J/(mol K)]'.format(c,delta_c))

