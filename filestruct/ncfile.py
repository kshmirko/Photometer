# -*- coding: utf-8 -*-
"""
Created on Fri May 17 12:38:23 2013

@author: kshmirko
"""

from netCDF4 import Dataset, date2num, datetime
import numpy as np

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

CHT = np.dtype(DTYPE_CH)

def createEmptyFile(fname):
    """
    create empty netcdf structured file to save photometer raw data
    
    """
    
    F = Dataset(fname,'w', format='NETCDF4')
    
    # переменные запихиваем в атрибуты
    F.latitude= 43.1
    F.longitude=131.9
    F.pressure = 102300.0
    F.a1 = 0.0
    F.a2 = 0.0
    F.a3 = 0.0
    F.a4 = 0.0
    F.w1 = 0.0
    F.w2 = 0.0
    F.ich870 = 0
    F.ich940 = 0

    dim0 = F.createDimension('time',None)
    dim1 = F.createDimension('nchans',16)

    time = F.createVariable('time','f4',('time',))
    time.units = 'days since 1984-02-08 00:00:00'
    time.calendar = 'standard'
    
    CHT_t = F.createCompoundType(CHT,'channel_t')
    opts_cal = F.createVariable('chan_sett',CHT_t,('nchans'))
    #opts_cal.match = [307,322,343,368,1242,1557,2139,411,439,500,870,936,1042,549,672,775.0]
    
    # Unlimited value for time    
    
    data = F.createVariable('data','f4',('time','nchans'))
#    data_I307 = data_grp.createVariable('I307','f4',('time',))
#    data_I322 = data_grp.createVariable('I322','f4',('time',))
#    data_I343 = data_grp.createVariable('I343','f4',('time',))
#    data_I368 = data_grp.createVariable('I368','f4',('time',))
#    data_I1242 = data_grp.createVariable('I1242','f4',('time',))
#    data_I1557 = data_grp.createVariable('I1557','f4',('time',))
#    data_I2139 = data_grp.createVariable('I2139','f4',('time',))
#    data_I411 = data_grp.createVariable('I411','f4',('time',))
#    data_I439 = data_grp.createVariable('I439','f4',('time',))
#    data_I500= data_grp.createVariable('I500','f4',('time',))
#    data_I870 = data_grp.createVariable('I870','f4',('time',))
#    data_I936 = data_grp.createVariable('I936','f4',('time',))
#    data_I1042= data_grp.createVariable('I1042','f4',('time',))
#    data_I549= data_grp.createVariable('I549','f4',('time',))
#    data_I672 = data_grp.createVariable('I672','f4',('time',))
#    data_I775= data_grp.createVariable('I775','f4',('time',))
    
    
    F.close()
    
    
def putdata(fname, data, calibr):
    """
    Writes data to ncfile
    """
    createEmptyFile(fname)
    F=Dataset(fname,'r+',format='NETCDF4')
    
    tmp = np.array([date2num(data.index[i], units=F.variables['time'].units, calendar=F.variables['time'].calendar) for i in range(len(data))])
#    print tmp
    F.variables['time'][:] = tmp
    F.variables['data'][:,0] = data['K1'].values
    F.variables['data'][:,1] = data['K2'].values
    F.variables['data'][:,2] = data['K3'].values
    F.variables['data'][:,3] = data['K4'].values
    F.variables['data'][:,4] = data['K5'].values
    F.variables['data'][:,5] = data['K6'].values
    F.variables['data'][:,6] = data['K7'].values
    F.variables['data'][:,7] = data['K8'].values
    F.variables['data'][:,8] = data['K9'].values
    F.variables['data'][:,9] = data['K10'].values
    F.variables['data'][:,10] = data['K11'].values
    F.variables['data'][:,11] = data['K12'].values
    F.variables['data'][:,12] = data['K13'].values
    F.variables['data'][:,13] = data['K15'].values
    F.variables['data'][:,14] = data['K16'].values
    F.variables['data'][:,15] = data['K17'].values
    
    F.latitude = calibr['location_settings']['lat']
    F.longitude = calibr['location_settings']['lon']
    F.pressure = 101300.0
    
    F.a1 = calibr['wc_settings']['a1']
    F.a2 = calibr['wc_settings']['a2']
    F.a3 = calibr['wc_settings']['a3']
    F.a4 = calibr['wc_settings']['a4']
    F.w1 = calibr['wc_settings']['w1']
    F.w2 = calibr['wc_settings']['w2']
    F.ich870 = calibr['wc_settings']['ch870']
    F.ich940 = calibr['wc_settings']['ch940']

    idx = 0    
    for item in calibr['channel_settings']:
        F.variables['chan_sett'][idx] = item
        idx=idx+1
    
    F.close()
    