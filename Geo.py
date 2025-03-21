# -*- coding: utf-8 -*-
"""
Created on Mon May  31 17:08:29 2022

@author: Dario Ledesma
"""
import math
import pandas as pd
import numpy as np


class Geo:
    
    def __init__(self, range_dates,  lat, long, gmt, alt, beta ):
        self.gmt = gmt
        self.lat = lat
        self.long = long
        self.altura = alt
        self.df = pd.DataFrame()
        
        """
        genera las filas para todo el df
        dado fechade de inicio y fin espaciado por freq cant de tiempo
        """
        #self.df['Fecha'] =  pd.date_range(start=desde+' 00:00:00', end=hasta+' 23:59:00', freq= freq+' min')
        self.df['date'] = range_dates
        """
        #el desplamiento para realizar 
        #el cálculo en el centro del invervalo
        """
        #self.df['Fecha'] =  self.df['Fecha']
        self.df['N'] = self.df['date'].dt.day_of_year
        self.df['M'] = self.df['date'].dt.month
        self.df['Y'] = self.df['date'].dt.year
        self.df['E'] = list(map(self.getE, self.df['N'], self.df['Y']))

        self.df['HR'] = self.df['date'].dt.hour + (self.df['date'].dt.minute) /60 + (self.df['date'].dt.second)/3600
        self.df['HS'] = self.getHS()

        self.df['deltaRad'] = list(map( self.delta, self.df.N, self.df.Y ))
        self.df['delta'] = self.df['deltaRad'].apply(math.degrees)
        
        
        self.df['ws'] = self.df['deltaRad'].apply(self.getWs)
        self.df['Fn'] = list(map(self.Fn, self.df.N, self.df.Y))
        
        
          
        self.df['w'] = 15 * (12 - self.df['HS'])    
        self.df['wRad'] = self.df['w'].apply(math.radians)


        self.df['lat'] = self.lat
        self.df['CTZ'] = list(map(self.getCTZ, self.df.deltaRad, self.df.wRad))
        #self.df['CTZ'] =  self.df.apply(lambda r: self.getCTZ(r['delta rad'], self.lat, r['w rad']), axis=1)

        self.df['TZ'] = self.df['CTZ'].apply(math.acos)
        self.df['SZA'] = self.df['CTZ'].apply(math.acos).apply(math.degrees)
        #self.df['Ys'] = list(map(self.getYs, self.df.w, self.df.CTZ, self.df.TZ, self.df.deltaRad))
        #self.df['Ys'] = self.df.apply(lambda r: self.Ys(r['w'], r['CTZ'], r['TZ'], r['deltaRad']), axis=1)
        
        # self.df['CT'] = np.where(self.df.CTZ>0, self.df.CTZ * math.cos(math.radians(beta)) + self.df.TZ.apply(math.sin) * math.sin(math.radians(beta)) * self.df.Ys.apply(math.cos), 0)
        
        # self.df['Ys'] = self.df.apply(lambda r: self.Ys(r['w'], r['CTZ'], r['TZ'], r['delta rad']), axis=1)
        self.df['alphaS'] = self.df['CTZ'].apply(math.asin).apply(math.degrees)
        self.df['E0'] = list(map(self.getE0, self.df.N, self.df.Y))
        self.df['TOA'] = list(map(self.TOA, self.df.E0, self.df.CTZ))
        # self.df['I0'] = self.df.apply(lambda r: 
        #                               self.TOADiaria(
        #                                   r['E0'],
        #                                   r['delta'],
        #                                   r['CTZ'],
        #                                   r['ws']
        #                                               ), axis=1)
        # #self.df['Ma'] = self.generateMa()
        # #self.df['Ma2'] = self.getMA(self.df['CTZ'])
        
        # ##ARGPV1
        # ##Masa de aire de casten, es la que se utiliza
        self.df['Mak'] = list(map(self.Mak, self.df.CTZ, self.df.TZ))
        
        
        #self.ktrp = self.getKtrp()
        
        
        self.ktrp = self.getKtrp()
        
        self.ktrp2 = 0.649 + 0.02 * self.altura ** 0.28
        
        self.df['GHIargp'] = list(map(self.generateGHIargp, self.df.TOA, self.df.Mak))
        self.df['GHIargp2'] = self.generateGHIargp_2(self.df)
        
        
        
        self.df['HS_GOES'] = list(map(self.HS_goes16, self.df.HS))
        self.df['CZ_goes16'] = list(map(self.CZ_goes16, self.df.delta, self.df.HS_GOES, self.df.ws))
        self.df['SZA_GOES'] = self.df['CZ_goes16']
        self.df['SZA_GOES'] = np.clip(self.df['SZA_GOES'], -1.0, 1.0)
        self.df['SZA_GOES'] = np.arccos(self.df['SZA_GOES'])
        
    def getKtrp(self):
        if(self.altura>1000):
            return 0.7 + 1.6391 * 10**-3 * self.altura ** 0.5500 
        else:
            return 0.7570 + 1.0112 * 10**-5 * self.altura ** 1.1067
        
    #Ecuación de tiempo
    #dado dia ordinal 
    #devuelve valor ecuación del tiempo en minutos
    def getE(self,n,y):
        
        
       
        if(y%4) == 0:
            gamma = 2 * math.pi * (n-1)/366
        else:
            gamma = 2 * math.pi * (n-1)/365
        
        
        cosg = math.cos(gamma) 
        sing = math.sin(gamma)
        
        cos2g = math.cos(2*gamma)
        sin2g = math.sin(2*gamma)
        
        
        E = 229.18 * (0.000075+ 0.001868 * cosg - 0.032077*sing - 0.014615*cos2g - 0.04089* sin2g )
        return E

    def Fn(self, n, y):
            
        if(y%4) == 0:
            gamma = 2 * math.pi * (n-1)/366
        else:
            gamma = 2 * math.pi * (n-1)/365
            
        fn = 1.000110 + 0.034221*math.cos(gamma) + 0.001280*math.sin(gamma) + 0.000719*math.cos(2*gamma) + 0.000077*math.sin(2*gamma)
        return fn
    
    #Hora solar 
    #devuelve valor hora solar
    #recorre cada fila del df
    def getHS(self):
        A = 1
        if self.gmt<=0:
            A = -1
        return self.df['HR'] + (4 * ((A * 15 * self.gmt)- (A*self.long))+ self.df['E'])/60
    
  
    
    #Declinación solar
    #dado dia ordinal
    #devuelve declinacion en radianes
    def delta(self, n, y):
        
        if(y%4) == 0:
            gamma = 2 * math.pi * (n-1)/366
        else:
            gamma = 2 * math.pi * (n-1)/365
            
        delta = 0.006918 - 0.399912 * math.cos(gamma) + 0.070257 * math.sin(gamma) - 0.006758 * math.cos(2*gamma) + 0.000907*math.sin(2*gamma) - 0.002697*math.cos(3*gamma)+ 0.00148*math.sin(3*gamma)
        return delta
    
    #CTZ
    #dado decliancio, lat y angulo horario
    #devuelve cos tita z en radianes
    def getCTZ(self, delta, omega):
        latR = math.radians(self.lat)    
        return (math.cos(latR) * math.cos(delta)* math.cos(omega)) + (math.sin(latR)*math.sin(delta))
        #return math.sin(delta) * math.sin(math.radians(lat)) + math.cos(delta) * math.cos(math.radians(lat))* math.cos(omega)


    def getWs(self, delta):
        return math.acos(-math.tan(delta) * (math.tan(math.radians(self.lat))))


    #E0
    #dado dia ordinal
    #devuelve factor de correción orbital
    def getE0(self, N, y):
        if(y%4) == 0:
            return 1+0.033* math.cos(2* math.pi * N /366)
        else:
            return 1+0.033* math.cos(2* math.pi * N /365)
            
        
        
    
    #T0A
    #dado fac. corr. orb. y ctz
    #devuelve irrad. solar extr. expr en whm2
    def TOA(self, E0, CTZ):
        if CTZ<0:
            return 0
        else:
            return 1361 * E0 * CTZ
        
        
    ##Ys
    def getYs(self, omega, CTZ, TZ, d):
        
        
        sinTitaZ = math.sin(TZ)
        sinLat = math.sin(math.radians(self.lat))
        cosLat = math.cos(math.radians(self.lat))
        signow = 1
        
        if(omega<0):
            signow = 1
        
        
        #ys = math.acos((math.sin(d) - CTZ * math.sin(math.radians(self.lat))) / (sinTitaZ * math.cos(math.radians(self.lat))))
        
        ys = math.acos((CTZ * sinLat - math.sin(d)) / (sinTitaZ * cosLat ) )
        
        #ACOS((O2*SENO(C2)-SENO(L2))/(SENO(P2)*COS(C2)))
        
        return signow * abs(ys)
    
    
    def Ys(self, omega, CTZ, TZ, d):
        
        
        sinTitaZ = math.sin(TZ)
        sinLat = math.sin(math.radians(self.lat))
        cosLat = math.cos(math.radians(self.lat))
        signow = 1
        
        if(omega<0):
            signow = -1
        
        
        #ys = math.acos((math.sin(d) - CTZ * math.sin(math.radians(self.lat))) / (sinTitaZ * math.cos(math.radians(self.lat))))
        
        ys = math.acos((CTZ * sinLat - math.sin(d)) / (sinTitaZ * cosLat ) )
        
        #ACOS((O2*SENO(C2)-SENO(L2))/(SENO(P2)*COS(C2)))
        
        return signow * abs(ys)
    
    #T0A
    #dado fac. corr. orb. y ctz
    #devuelve irrad. solar extr. expr en whm2
    def TOADiaria(self, E0, dlt, CTZ, ws ):
    
        # E0 = data['E0']
        cosDelta = math.cos(dlt)
        sinDelta = math.sin(dlt)
        cosLatR = math.cos(math.radians(self.lat))    
        sinLatR = math.sin(math.radians(self.lat))   
        sinWs = math.sin(ws)
        
        if CTZ>0:
            return abs(24/math.pi *1361*E0 * (cosDelta * cosLatR * sinWs + ws * sinDelta * sinLatR))
        else:
            return 0
        
        
    def getMA(self,CTZs):
        result = []
        for ctz in CTZs:
            try:
                valor1 = 1.002432 * ctz**2 + 0.148386*ctz + 0.0096
                valor2 = ctz**3 + 0.149864*ctz**2 + 0.0102963*ctz + 0.000303978
                result.append(valor1/valor2)
            except Exception:
                result.append(0)
        return result
    
    
    def Mak(self, CTZ, TZ):
        
        
        presion = 101355* (288.15/(288.15 - 0.0065 * self.altura)) ** -5.255877
        Amk = 1/ (CTZ + 0.15*(93.885 - TZ)**-1.253)
        return Amk * (presion / 101355)
        
    
    def Mak2(self, CTZ, TZ):
        presion = 101355* (288.15/(288.15 - 0.0065 * self.altura)) ** -5.255877
        
        
        
        
        Amk = 1/ (CTZ + 0.15*(93.885 - TZ)**-1.253)
        
        return Amk * (presion/101355)
    
    
    def generateMa(self):
        
        cosTZ = self.df['CTZ'].tolist()
        tz = self.df['TZ'].tolist()
           
        
        
        
        presion =  math.pow(288.15/(288.15 - 0.0065 * 1150), -5.255877);
        results = []
        
        for i, val in enumerate(cosTZ):
            
            try:
                calc = 1/(val + 0.15 * math.pow((93.885-  tz[i]), -1.253));
                results.append(calc * presion)
            except Exception:
                results.append(0)        
        return results
    
    
    
    def generateGHIargp(self, TOA, AM):
        
        
        try:
            return TOA * math.pow(self.ktrp, math.pow(AM, 0.678))
        except Exception:
            return 0
        
        
        
    
    
    def generateGHIargp_2(self, data):
        GHI = data['TOA'].tolist()
        AM = data['Mak'].tolist()
    
    
    
        result = []
        for i, val in enumerate(GHI):
            try:
                result.append(GHI[i] * math.pow( self.ktrp2 ,math.pow(AM[i], 0.678)))
            except Exception:
                result.append(0)
        return result
    
    
    def HS_goes16(self, HS):
    	sat_lon = -75
    	return np.radians( 15 * (HS - sat_lon / 15))
    	
    
    def CZ_goes16(self, delta, hour_angle_satellite, ws):
    	
    	lat_rad = np.radians(self.lat)
    	
    	return (
        np.sin(lat_rad) * np.sin(delta) +
        np.cos(lat_rad) * np.cos(delta) *
        (np.cos(ws) - np.cos(hour_angle_satellite)))
    
   
    
    def to_csv(self, name):
        self.df.to_csv(name+".csv")


#full = pd.date_range(
#     start="2018/01/01 00:00", 
#     end="2018/12/31 23:59",
#     freq="10 min")


#dfGeo = Geo(full, 
#         lat=-24.7, 
#         long= -65.4, 
#         gmt = 0,
#         alt = 3487, beta = 0).df
         
 
