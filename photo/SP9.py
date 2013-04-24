# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 12:35:51 2013

@author: kshmirko
"""

from photo.calibrationFile import readCalibration

class BasePhoto(object):
    """
    Ancestor for all sun photometer devices
    defines common interface for sun photometer
    """
    def __init__(self, fname=None):
        self._fname = fname
    
    
    def _readCalibration(self, fname=None):
        self.calibrCoefs = readCalibration(fname)
        
    def _correctTime(self):
        pass
    
    def _calcLogarithms(self):
        pass
        



class SP9(BasePhoto):
    
    def _readCalibration(self, fname='sp9iapu'):
        super(SP9,self)._readCalibration(fname)



class SPM(BasePhoto):
    
    def _readCalibration(self, fname='spmpoi'):
        super(SPM,self)._readCalibration(fname)
    