# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 14:47:24 2013

@author: kshmirko
"""

__all__=['getairmass']

import sunpos as spa
import numpy as np
from datetime import datetime, timedelta

def getairmass(datetime, location):
    """
    calculates airmass and zenith angle for specific date and coordinates
    time should be in UTC
    >> datetime = datetime(YYYY,MM,DD,HH,mm,SS)
    >> location = (LON, LAT)
    >> airm = getairmass(datetime, location)
    >> 
    """
    time=spa.cTime()
    time.iYear  =   datetime.year
    time.iMonth =   datetime.month
    time.iDay   =   datetime.day
    time.dHours =   datetime.hour
    time.dMinutes = datetime.minute
    time.dSeconds = datetime.second
    
    loc = spa.cLocation()
    loc.dLongitude = loc[0]
    loc.dLatitude = loc[1]
    
    ret = spa.sunposf(time, loc)
    airm =  1.0/np.cos(np.deg2gad(ret.dZenithAngle))
    return airm
    
def getEarth2SunDistance(JD):
    """
    calculates earth to sun distance for specific date
    >> JD = datetime(2010,10,13,23,22,11)
    >> getEarth2SunDistance(JD)
    """
    JD0=datetime(2000,1,1,12,0,0)
    D = (JD-JD0).total_seconds()/24/3600
    g = 357.529+0.98560028*D
    g_rad = np.deg2rad(g)
    R = 1.00014-0.01671*np.cos(g_rad)-0.00014*np.cos(2*g_rad)
    return R
    
def getRayleigh(wl, P0, T0):
    