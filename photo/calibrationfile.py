# -*- coding: utf-8 -*-
"""
 This module contains subroutines for reading sun photometer calibration file.
 Copyright (C) Fri Jan 18 16:40:46 2013 Ph.D. Shmirko Konstantin Alexandrovich

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__all__=['readCalibration']


import numpy as np
import re

# Describes the structure of the calibration file.
DTYPE_CH=[ \
    ('wavelen', '>f8'),\
    ('i0', '>f8'),\
    ('reley', '>f8'),\
    ('water1', '>f8'),\
    ('water2', '>f8'),\
    ('ozon1', '>f8'),\
    ('ozon2', '>f8'),\
    ('gazes1', '>f8'),\
    ('gazes2', '>f8'),\
    ('shadow_signal', '>f8'),\
    ('additional', '>f8'),\
]

DTYPE_GIG=[\
    ('a1','>f8'),\
    ('a2','>f8'),\
    ('a3','>f8'),\
    ('a4','>f8'),\
    ('w1','>f8'),\
    ('w2','>f8'),\
    ('ch870','>i4'),\
    ('ch940','>i4'),\
]

DTYPE_PRS=[\
    ('readmode','>i4'),\
    ('value', '>f8'),\
]

DTYPE_CRD=[
    ('readmode', '>i4'),\
    ('lat', '>f8'),\
    ('lon', '>f8'),\
    ('fivedigs','u4')\
]

def readCalibration(fname):
    """
    Read file with calibration constants
    Input:
        fname - Input filename
    Output:
        ret   - dict of calibration file blocks
        
    >>> ret = readCalibration('calcSP9iapu')
    """    
    with open(fname, 'rb') as f:
        CH_count = np.fromfile(f, dtype='>i4', count=1)[0]        
#        names,chans=__readCahnels(f, CH_count)
        chans=__readCahnels(f, CH_count)

        gigdata = np.fromfile(f, dtype=DTYPE_GIG, count=1)[0]
        
        prsfname, prscolname, prsdt = __readPrs(f)

        crddt = np.fromfile(f, dtype = DTYPE_CRD, count=1)[0]
    
    #==> Gets a dictionary of bcalibration file locks  
    ret = {'channel_settings':chans, \
            'wc_settings':gigdata, \
            'pressure_fname':prsfname, \
            'pressure_colname': prscolname, \
            'pressure_settings': prsdt,\
            'location_settings':crddt}

    return ret


def __readCahnels(f,Nch):
    """
    Reads the channel setting.
    """
    ret = {}
    names=None
    
    for i in range(Nch):
        name_len = np.fromfile(f, '>i4', 1)[0]
        #transform the two-byte string in single-byte
        names = re.sub('\x00','',f.read(name_len)).upper()
        ret[names] = np.fromfile(f, dtype=DTYPE_CH, count=1)[0]
        
    return ret
        
        
def __readPrs(f):
    """
    Reads the presseure settings
    """
    ret = np.fromfile(f, dtype=DTYPE_PRS, count=1)[0]    
    
    name_len = np.fromfile(f, '>i4', 1)[0]
    #transform the two-byte string in single-byte
    filename = re.sub('\x00','',f.read(name_len))
    
    name_len = np.fromfile(f, '>i4', 1)[0]
    #transform the two-byte string in single-byte
    columnname = re.sub('\x00','',f.read(name_len))
    
    return filename, columnname, ret
    