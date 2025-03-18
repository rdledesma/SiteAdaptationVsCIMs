#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 09:56:04 2023

@author: dario
"""
import numpy as np
class QC:
    def __init__(self, df ):
        
        df['filtro0'] = df.SZA<90
        df['filtro1'] = np.where(
            df.SZA < 90, df.ghi < 1.5 * 1361.7* df.CTZ**1.2 + 100, True)
        
        df['filtro2'] = np.where(
            df.SZA > 90, df.ghi > (6.5331 - 0.065502 * df.TZ + 1.8312E-4 * df.TZ ** 2) /
            (1 + 0.01113 * df.TZ), True)
        
        
        df['kt'] = np.where(df.TOA>0, df.ghi / df.TOA, 0)
        
        df['filtro3'] = (df.kt<1.4) & (df.kt>0)
        
        df['Acepted'] = np.where(df.filtro0 & df.filtro1 & df.filtro2 & df.filtro3, True, False)
        
