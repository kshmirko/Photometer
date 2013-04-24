# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 11:33:55 2013

@author: kshmirko
"""



import sunpos as sun
import numpy as np

__all__ = ['calcAirMass']

def _calcAirMassForScalar(dt, loc):
    """
    calcAirMassForScalar(dt, loc) -> airmass approximation sec(SolarZenithAngle)
    Расчет массы атмосферы
    dt - datetime, UTC
    lon - tuple(longitude, latitude)    
    """
    
    time = sun.cTime()
    pos = sun.cLocation()

    pos.dLongitude = loc[0]
    pos.dLatitude = loc[1]
    
    time.dHours = dt.hour
    time.dMinutes = dt.minute
    time.dSeconds = dt.second
    time.iYear = dt.year
    time.iMonth = dt.month
    time.iDay = dt.day
    
    ret = sun.sunposf(time, pos)
    ret = 1.0/np.cos(ret.dZenithAngle*np.pi/180.0)
    return ret


def _calcAirMassForArray(dates, loc):
    """
    calcAirMassForArray(dates, loc) -> list of airmasses
    Расчет атмосферной массы для массива временных отсчетов
    dates - array or list of datetimes
    loc - tuple (longitude, latitude)
    """        
    ret = [_calcAirMassForScalar(dt, loc) for dt in dates]    
    return ret

def calcAirMass(dt, loc):
    """
    calcAirMass(dt, loc) -> array or scalar value of airmasses
    dt - array or scalar value of datetime, UTC
    loc - tuple(longitude, latitude)
    """
    if hasattr(dt, '__iter__'):
        return _calcAirMassForArray(dt, loc)
    return _calcAirMassForScalar(dt, loc)

if __name__=='__main__':
    from datetime import datetime
    dt0 = datetime.utcnow()
    dt1 = datetime.utcnow()    
    
    loc = (131.2, 43.1)
    
    print "===>TestScalar"
    print calcAirMass(dt0, loc)
    print "===>Test array"
    print calcAirMass([dt0, dt1], loc)
    