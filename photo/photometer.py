# -*- coding: utf-8 -*-
"""
<Program description>
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
__all__ = ['SP9']

import pandas as pds
from pandas.io.date_converters import _maybe_cast
import pandas.lib as lib
import numpy as np
from scipy import interpolate
from datetime import datetime, timedelta
from device.calibrationfile import readCalibration   
import spamodule as spa
import re


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


def parser(DD,MM,YY,HH,NN,SS):
    """
    Datetime parser
    """
    dt = datetime(2000+int(YY), int(MM), int(DD), int(HH), int(NN), int(SS))
#    print dt
    return dt
    

class Photometer(object):
    """
    Abstract class for photometer data
    """
    def __init__(self,*args):
        self.isLog = False
        self.isAOT = False
                
        pass
    
    def loadcoefs(self):
        """
        Initializes dictionary I0 [chnum].
        """      
        raise NotImplementedError("Call of an abstract method")
        
    
    def loadmeasurements(self, fname):
        """
        Reads the measurement from a file.
        """
        raise NotImplementedError("Call of an abstract method")
        
    def calc(self, mode='log'):
        """
        Calculates optical parameters
        """
        raise NotImplementedError("Call of an abstract method")
        
    def getozone(lat, month):
        """
        Calculate ozone content
        """
        pass
        


class SP9(Photometer):
    """
    Photometer SP9 model
    """
    
    def __init__(self, *args):
        
        super(SP9, self).__init__()
        self.loadcoefs()
        self.loadozone()
        if len(args)==1:
            #Згружаем файлы с данными
            self.loadmeasurements(args[0])
                
            
    
    def loadcoefs(self):
        """
        Load calibration parameters from specific file.
        
        """
        self.calibrationdata = readCalibration('device/calcSP9iapu')
        


    def loadmeasurements(self, fname):
        """
        Import photometer measurements data with following format:
        DD  MM YY HH MM SS NS Lat     EW       Lon  K1     K2     K3     K4     K5     K6     K7     K8     K9    K10    K11    K12    K13    K14    K15    K16    K17   Pres    Tpr    Hum    Thm   Tbrd  Ubat
        Data stored in a table
        DD MM YY HH MM SS - 6 coumnt with datetime
        NS LAT - literal direction and latitude
        EW LON - literal direction and longitude
        K1-K17 - channels
        
        """
        self.data = pds.read_table(fname, delimiter=' ', skipinitialspace=True,\
            parse_dates={'datetime':[0,1,2,3,4,5]}, date_parser=parser_fast, \
            index_col = 'datetime')

        #UTC to Local time
        self.data.index = self.data.index.shift(1, freq=timedelta(hours=11)) 
        self.KS = ['K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'K9', 'K10', 'K11', 'K13', 'K15', 'K16', 'K17']
        self.WL = [341, 368, 1242, 1557, 2139, 411, 439, 500, 870, 1042, 549, 672, 775]
        self.outfname=fname.replace('signals','aot')
        
        #find dates of sun photometer measurements
#        self.years = self.data.index.year
#        self.months= self.data.index.month
#        self.days  = self.data.index.day
#        self.dates = []
#        
#        for y in range(min(self.years), max(self.years)+1):
#            for m in range(min(self.months), max(self.months)+1):
#                for d in range(min(self.days), max(self.days)+1):
#                    if (y in self.years) and (m in self.months) and (d in self.days):
#                        self.dates.append((y,m,d,))


    def loadozone(self):
        
        O3 = np.loadtxt('O3-HI-SE.DAT')
        month = O3[1:,0]
        lat = O3[0,1:]
        O3 = O3[1:,1:]
        
        self.O3 = interpolate.interp2d(lat, month, O3)
        
    def getozone(self, lat, month):
        return self.O3(lat, month).T[0]
        
        
    def calc(self, mode='log', dt0=-timedelta(hours=0, minutes=55)):
        """
        Retrieves optical parameters of the Atmosphere (AOT, total water content) 
        from sun-photometer measurements.
        
        Firs, we calculate airmass MA for the specific datetime according to sun 
        position algorithm (SPA) \cite{...}. After that we find Earth-Sun distance correction
        coefficient
        
        AM = 0.03351*\cos(0.52925*(month+day/31)-0.35149)+0.99964.
        
        Next step is to calculate Pressure correction. It impacts molecular optical 
        thickness and new value of \tau_{m} is
        
        \tau_{m}(P)= \tau_{m}(P_{0})PA
        PA=\frac{P}{P_{0}}
        
        Before processing sun photemeter data it is necessary to substract shaddow signal 
        and correct result to Earth-Sun distance.
        
        I[i] = (I[i]-I_{shaddow}[i])/AM
        where I[i] - sun intensity for i-th channel
        I_{shaddow}[i] - shaddow intensity for i-th channel
        
        Next step is water content calculation. Water content can be calculated if w1 
        coefficient has non zero value and ch_870 and ch_940 are specified. And both
        I[ch_870] and I[ch_940] are positive. Where ch_870 and ch_936 are ids of 870 nm 
        and 936 nm channels.
        
        So we can write 
        
        ltw = \log(\frac{I[ch_940]}{I[ch_870]}) - w1 - w2
        xw = a1+a2*ltw+a3*ltw^2+a4*ltw^3
        WaterContent = \frac{xw^2}{MA}
        
        To calculate water one-way transmittance we should use following equation
        
        T_{water} = \exp(-water1*(xw*MA)^{water2}) or 
        \tau_{water}=water1*(xw*MA)^{water2}
        
        ozone one-way transmittance is
        
        T_{ozone} = \exp(ozon1*(xoz*MA)^{ozone2}) or
        \tau_{ozone} = ozon1*(xoz*MA)^{ozone2}
        
        anoter one for gazes
        
        T_{gaz} = \exp(gazes1*(MA)^{gazes2}) or
        \tau_{gaz} = gazes1*(MA)^{gazes2}
        
        and for rayleigh
        
        T_{m} = \exp(log(reley1)*(MA)*PA*MA) or
        \tau_{m} = log(reley1)*(MA)*PA*MA

        T_{total} = T_{water} T_{ozone} T_{gaz} T_{m}
        
        AOT calculations are based on a following equation
        
        
        \tau_{a} = -\frac{(log \frac{I}{T_{total}} - log I0)}{M}, where M - mass of the atmosphere,
        
        I0 - top of the atmosphere solar radiation, I - solar radiation measured 
        at the Earth.
        
        wc = \dots
        
        Input parameters:
            mode - can take one of following values 'log' and 'aot'. In the first
            case it calculates logarithm of solar radiation, in the 
            second case it evaluates aerosol optical thickness for given channels 
            and do Rayleigh scattering and gases absorbtion correction.
            
        """
        
        if (mode is 'log') and (not self.isLog):
            # Runs through all the columns with names K\d*.
            self.logs = pds.DataFrame(index=self.data.index)
            # 1.  Adjusts the distance from the earth to the sun.
            self.AM = np.array([0.03351*np.cos(0.52925*(t.month+t.day/31.0)-0.35149)+0.99964 for t in self.data.index])
            self.logs['AM']=self.AM
            
            for key in self.data.columns:
                tmp = re.search('[Kk]\d*', key)
                if not tmp is None:
                    idx = tmp.string[tmp.start():tmp.end()]                    
                    self.logs[idx] = np.log(self.data[idx]/self.AM)
                    
            self.isLog = True
        LAT = 43.0
        if (mode is 'aot') and (not self.isAOT) and (self.isLog):
            # Calculates the atmotpheric mass.
            MA = np.array([spa.spacalc(t+dt0, 11)[1] for t in self.data.index])
            Zen= np.array([spa.spacalc(t+dt0, 11)[0] for t in self.data.index])
#            self.data['Zen'] = np.array([(180.0-spa.spacalc(t, 11)[0])/90*3000 for t in self.data.index])
            self.aots = pds.DataFrame(index=self.data.index)
            self.aots['MA'] = MA
            self.aots['ZEN'] = Zen
            print self.aots.index.month
            # Runs through all the columns with names K\d*.           
            for key in self.data.columns:
                tmp = re.search('[Kk]\d*', key)
                if not tmp is None:
                    idx = tmp.string[tmp.start():tmp.end()]
                    
                    
                    # Calculates the water content in the atmosphere.
                    wc_params = self.calibrationdata['wc_settings']
                    
                    if (wc_params['w1']>0) and (wc_params['ch940']>=0) and (wc_params['ch870']>=0):
                        #номера каало
                        k940="K%d"%(wc_params['ch940']+1)
                        k870="K%d"%(wc_params['ch870']+1)
                        
                        ltw=self.logs[k940]-self.logs[k870]-wc_params['w1']-wc_params['w2']
                        xw = wc_params['a1']+wc_params['a2']*ltw+wc_params['a3']*ltw*ltw+wc_params['a4']*ltw*ltw*ltw
                        self.aots['xw'] = xw*xw/self.aots['MA']
                    
                    if idx in self.calibrationdata['channel_settings'].keys():
                        reley = np.log(self.calibrationdata['channel_settings'][idx]['reley'])
                        water = self.calibrationdata['channel_settings'][idx]['water1']*np.power(self.aots['MA']*self.aots['xw'], \
                                self.calibrationdata['channel_settings'][idx]['water2']) / self.aots['MA']
                        ozon  = self.calibrationdata['channel_settings'][idx]['ozon1']*np.power(self.aots['MA']*self.getozone(LAT, self.aots.index.month), \
                                self.calibrationdata['channel_settings'][idx]['ozon2']) / self.aots['MA']
                        gas = self.calibrationdata['channel_settings'][idx]['gazes1']*np.power(self.aots['MA'], \
                                self.calibrationdata['channel_settings'][idx]['gazes2']) / self.aots['MA']
                        

                        
                        self.aots[idx] = -(self.logs[idx] - self.calibrationdata['channel_settings'][idx]['i0']) / self.aots['MA']+ reley - water - gas - ozon
                        
                        self.aots.where(self.aots>0,other=np.nan, inplace=True)
                        self.aots.index.name='datetime'
                        self.aots.to_csv(self.outfname)
                        
            self.isAOT = True
                    
        
        