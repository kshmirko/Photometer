# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 14:47:24 2013

@author: kshmirko
"""

__all__=['getairmass']

import sunpos as spa
import numpy as np
from datetime import datetime, timedelta

    
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
    