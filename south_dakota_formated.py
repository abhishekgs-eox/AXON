# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 11:01:59 2022

@author: shrihari
"""

import pandas as pd
import numpy as np

df = pd.read_csv(r"D:\Axon\TankFacilities_NR42-8_10_2022.csv")

facilityID = []
facilityName = []
address = []
city = []
zipcode = []
ownerName = []
df2 = pd.DataFrame(index=df['FacID/Tnk#'],
                   columns = ['Facility ID','Tank ID',
                              'Facility Name','Tank Status',
                              'Address','Product',
                              'City','Volume','Zipcode',
                              'Year Installed','TankConst',
                              'Num Comp','Owner Name',
                              'PipeMat','PipeType',
                              'TankLD','PipeLD','SpillPrev','Overfill'])

for i in range(len(df)):
    
    if '-'  in df['FacID/Tnk#'][i]:
        facilityID.append(df['FacID/Tnk#'][i])
        facilityName.append(df['FacName/TankStatus'][i])
        address.append(df['Product'][i])
        city.append(df['Volume'][i])
        zipcode.append(df['YearInst'][i])
        ownerName.append(df['OwnerName/#Comp'][i])
    if '-' not in df['FacID/Tnk#'][i]:
        df2['Facility ID'][i] = facilityID[-1]
        df2['Facility Name'][i] = facilityName[-1]
        df2['Address'][i] = address[-1]
        df2['City'][i] = city[-1]
        df2['Zipcode'][i] = zipcode[-1]
        df2['Owner Name'][i] = ownerName[-1]
        df2['Tank ID'][i] = df['FacID/Tnk#'][i]
        df2['Tank Status'][i] = df['FacName/TankStatus'][i]
        df2['Product'][i] = df['Product'][i]
        df2['Volume'][i] = df['Volume'][i]
        df2['Year Installed'][i] = df['YearInst'][i]
        df2['TankConst'][i] = df['TankConst'][i]
        df2['Num Comp'][i] = df['OwnerName/#Comp'][i]
        df2['PipeMat'][i] = df['PipeMat'][i]
        df2['PipeType'][i] = df['PipeType'][i]
        df2['TankLD'][i] = df['TankLD'][i]
        df2['PipeLD'][i] = df['PipeLD'][i]
        df2['SpillPrev'][i] = df['SpillPrev'][i]
        df2['Overfill'][i] = df['Overfill'][i]
        
        

df3 = df2.reset_index()
del df3['FacID/Tnk#']

df3.replace('',np.nan,inplace=True)
df4 = df3.dropna(how='all')
df4.to_excel(r"D:\Axon\south_dakota_formated.xlsx",index=False)