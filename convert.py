# -*- coding: utf-8 -*-
"""
 <Program description>
 Copyright (C) Tue Apr 23 11:06:04 2013 Ph.D. Shmirko Konstantin Alexandrovich

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

import pandas as pds
from pandas.io.date_converters import _maybe_cast
import pandas.lib as lib
import numpy as np
from datetime import datetime, timedelta
from photo.calibrationfile import readCalibration


def parser_fast(DD,MM,YY,HH,NN,SS):
    """
    Another datetime parser
    """
    YY = _maybe_cast(YY)
    MM = _maybe_cast(MM)
    DD = _maybe_cast(DD)
    HH = _maybe_cast(HH)
    NN = _maybe_cast(NN)
    SS = _maybe_cast(SS)
    return lib.try_parse_datetime_components(YY+2000, MM, DD,
                                             HH, NN, SS)
def datetime2matlabdn(dt):
   mdn = dt + timedelta(days = 366)
   frac_seconds = (dt-datetime(dt.year,dt.month,dt.day,0,0,0)).seconds / (24.0 * 60.0 * 60.0)
   frac_microseconds = dt.microsecond / (24.0 * 60.0 * 60.0 * 1000000.0)
   return mdn.toordinal() + frac_seconds + frac_microseconds

    
def convert(dt):
    return np.array([datetime2matlabdn(x) for x in dt])
    
def main(fnames):
    import scipy.io as sio
    Data={}
    keys=['Y2010','Y2011','Y2012','Y2013']
    idx=0
    for fname in fnames:    
    
        data = pds.read_table(fname, delimiter=' ', skipinitialspace=True,\
                parse_dates={'datetime':[0,1,2,3,4,5]}, date_parser=parser_fast, \
                index_col = 'datetime')
        
        
        print data.index[0]
        buf={}
        buf['datetime']=convert(data.index)
        buf['I307'] = data['K1']
        buf['I322'] = data['K2']
        buf['I343'] = data['K3']
        buf['I368'] = data['K4']
        buf['I1242'] = data['K5']
        buf['I1557'] = data['K6']
        buf['I2139'] = data['K7']
        buf['I411'] = data['K8']
        buf['I439'] = data['K9']
        buf['I500'] = data['K10']
        buf['I870'] = data['K11']
        buf['I936'] = data['K12']        
        buf['I1042'] = data['K13']
        buf['I549'] = data['K15']        
        buf['I672'] = data['K16']
        buf['I775'] = data['K17']
        
        Data[keys[idx]] = buf
        idx = idx + 1
    Data['calibration'] = readCalibration('photo/calcSP9iapu')
    sio.savemat('test.mat',Data, do_compression=True, oned_as='row')
    
if __name__=='__main__':
    main(['data/signals-2010a.txt','data/signals-2011a.txt','data/signals-2012a.txt','data/signals-2013a.txt'])
    
    