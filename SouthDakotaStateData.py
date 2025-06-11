from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os
import numpy as np

PATH = "F:\Driver\chromedriver.exe"
URL="https://apps.sd.gov/NR42InteractiveMap"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "F:\\Axon\\SouthDakota\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(10)

WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,'//*[@id="accept"]')))
driver.find_element(By.XPATH,'//*[@id="accept"]').click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="tanksCheckbox"]')))
driver.find_element(By.XPATH,'//*[@id="tanksCheckbox"]').click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="BOTH"]')))
driver.find_element(By.XPATH,'//*[@id="BOTH"]').click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="both"]')))
driver.find_element(By.XPATH,'//*[@id="both"]').click()

time.sleep(60)# time provided for view results button to get enabled

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="openGrid"]')))
driver.find_element(By.XPATH,'//*[@id="openGrid"]').click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="tankFacilitiesCount"]')))
driver.find_element(By.XPATH,'//*[@id="tankFacilitiesCount"]').click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="exportTankResults"]')))
driver.find_element(By.XPATH,'//*[@id="exportTankResults"]').click()

while len(os.listdir(r'F:\Axon\SouthDakota\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')

print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'F:\Axon\SouthDakota\Input'):
        filesList.append(file)
        filesExtensions = [x.split('.')[-1] for x in filesList]
        print(filesExtensions)
    if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
        time.sleep(3)
        Check_File_Status()
    else:
        pass

Check_File_Status()

# driver.quit()

print('....Downloaded....')

for file in os.listdir(r'F:\Axon\SouthDakota\Input'):
    DownloadedFile = file    

print('Formatting each column and segregating the required data and placing in the correct columns')    

df = pd.read_csv("F:\\Axon\\SouthDakota\\Input\\"+str(DownloadedFile))


facilityID = []
facilityName = []
address = []
city = []
zipcode = []
ownerName = []
tankStatusList = ['Removed',
 'Current',
 'Temporary Closure',
 'Abandoned in Place',
 'Permanently Out Of Use',
 'Temporarily Out Of Use','nan']

df2 = pd.DataFrame(index=df['FacID/Tnk#'],
                   columns = ['Facility ID','Tank ID',
                              'Facility Name','Tank Status',
                              'Address','Product',
                              'City','Volume','Zipcode',
                              'Year Installed','TankConst',
                              'Num Comp','Owner Name',
                              'PipeMat','PipeType',
                              'TankLD','PipeLD','SpillPrev','Overfill'])


def Add_Facility_Details(i):
    facilityID.append(df['FacID/Tnk#'][i])
    facilityName.append(df['FacName/TankStatus'][i])
    address.append(df['Product'][i])
    city.append(df['Volume'][i])
    zipcode.append(df['YearInst'][i])
    ownerName.append(df['OwnerName/#Comp'][i])
    
    
def Add_Tank_Details(i):
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
    
for i in range(len(df)):
    
    if '-'  in df['FacID/Tnk#'][i] or str(df['FacName/TankStatus'][i]) not in tankStatusList:  
        Add_Facility_Details(i)
        
    if '-' not in df['FacID/Tnk#'][i] and str(df['FacName/TankStatus'][i]) in tankStatusList:
        Add_Tank_Details(i)
        
        

df3 = df2.reset_index()
del df3['FacID/Tnk#']

df3.replace('',np.nan,inplace=True)
df4 = df3.dropna(how='all')
df4.to_excel(r"F:\Axon\SouthDakota\Output\south_dakota_formated.xlsx",index=False)

dfSDmap = pd.read_excel("F:\\Axon\\SouthDakota\\Required\\SouthDakotaMapping.xlsx",)
print('Reading the SouthDakota Mapping file....')
dfSDmap = dfSDmap[:0]

print('Reading the SouthDakota State file....')
dfSD = pd.read_excel("F:\\Axon\\SouthDakota\\Output\\south_dakota_formated.xlsx")

SDmap = dfSD[['Facility ID','Tank ID','Address','City','Zipcode','Year Installed','Volume','TankConst','PipeMat','Num Comp','Product','Facility Name','Tank Status']]   
SDmap.columns = ['Facility Id','Tank ID ','Tank Location','City','Zip Code','Year Installed','Tank Size ','tank construction','piping construction_refined','Secondary Containment (AST)','content description','Facility Name','tank status']

print('Merging the UST_List file with SouthDakota Mapping file and writing to excel')
SDmerge = pd.concat([dfSDmap,SDmap])
SDmerge['State'] = 'South Dakota'
SDmerge['state_name'] = 'SD'
SDmerge.to_excel(r'F:\Axon\SouthDakota\Output\SouthDakotaFinal.xlsx', index = False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("F:\\Axon\\SouthDakota\\Required\\LustDataAllStates.xlsx")
SD=LustData[LustData['State Name'] == 'South Dakota']

print('writing SouthDakota Lower underground storage tank data....')
SD.to_excel(r'F:\Axon\SouthDakota\Required\SouthDakotaLustData.xlsx',index = False)

print('Reading SouthDakota Final data....')
SDFinal =pd.read_excel(r'F:\Axon\SouthDakota\Output\SouthDakotaFinal.xlsx')

print('Reading SouthDakota Lust Data....')
SDLust=pd.read_excel(r'F:\Axon\SouthDakota\Required\SouthDakotaLustData.xlsx')

SDLust['location_city'] = SDLust['Address'] + '_' + SDLust['City']
SDFinal['location_city'] = SDFinal['Tank Location'] + '_' + SDFinal['City']
SDLust['location_city'] = SDLust['location_city'].str.upper()
SDFinal['location_city'] = SDFinal['location_city'].str.upper()
SDLustUnique = SDLust.drop_duplicates(subset = 'location_city',keep='first')

SDFinalMerged = pd.merge(SDFinal,SDLustUnique, on='location_city',how='left')
SDFinal['lust'] = SDFinalMerged['Address'] + '_' + SDFinalMerged['City_y']
SDFinal['lust_status'] = SDFinalMerged['Status']
del SDFinal['location_city']

print('Merging SouthDakota Final and SouthDakota L-UST data')
SDFinal.to_excel(r'F:\Axon\SouthDakota\Output\SouthDakotaFinalMerged.xlsx', index=False)

print('Completed....')