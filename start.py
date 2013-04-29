# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 23:51:40 2013

@author: kshmirko
"""

import locale
locale.setlocale(locale.LC_TIME,'ru_RU.UTF-8')
from matplotlib import rc
import matplotlib

FONTNAME = 'DejaVu Serif'

font = {'family' : FONTNAME,
        'weight' : 'normal',
        'size'   : 14}

rc('font', **font)

matplotlib.use('TkAgg')


import pylab as plt
import numpy as np
import sunpos
from datetime import datetime, timedelta

t0 = datetime(2013,4,1,10,0,0)
t1 = datetime(2013,4,1,19,0,0)
dt = timedelta(minutes=1)
dt0=timedelta(hours=11)
t0=t0-dt0
t1=t1-dt0

loc=sunpos.cLocation()
loc.dLatitude = 43.1
loc.dLongitude = 131.9

time= sunpos.cTime()

I0=1.0
ret =sunpos.cSunCoordinates()
T=[]
I=[]
while t0<t1:
    time.iYear = t0.year
    time.iMonth = t0.month
    time.iDay = t0.day
    
    time.dHours = t0.hour
    time.dMinutes = t0.minute
    time.dSeconds = t0.second
    sunpos.sunpos(time, loc, ret)

    #ret.dZenithAngle
    
    m = 1.0/np.cos(np.deg2rad(ret.dZenithAngle))
    
    I.append(I0*np.exp(-m*0.1))
    T.append(t0+dt0)
    t0=t0+dt

ax = plt.figure().add_subplot(111)

plt.plot(T, I)
plt.grid()
plt.show()