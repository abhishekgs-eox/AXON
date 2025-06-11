from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os
import pyxlsb

# PATH = "C:\\Users\\Administrator\\Desktop\\axon_states\\Drivers\\chromedriver_win32\\chromedriver.exe"
# URL="https://www.michigan.gov/lara/bureau-list/bfs/storage-tanks/underground"

# chromeOptions = Options()
# chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Michigan\\Input"})
# driver =  webdriver.Chrome(PATH,options=chromeOptions)
# driver.maximize_window()
# driver.get(URL)
# driver.implicitly_wait(5)

# WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="pagebody"]/div[4]/div/ul/li[4]/div/a')))
# driver.find_element(By.XPATH,'//*[@id="pagebody"]/div[4]/div/ul/li[4]/div/a').click()

# while len(os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Michigan\Input')) < 1:
#     time.sleep(0.2)
#     print('waiting to download...')
    
    
# print('Downloading the files started....')
# def Check_File_Status():
#     filesExtensions = []
#     filesList = []
#     for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Michigan\Input'):
#         filesList.append(file)
#         filesExtensions = [x.split('.')[-1] for x in filesList]
#         print(filesExtensions)
#     if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
#         time.sleep(3)
#         Check_File_Status()
#     else:
#         pass
    
# Check_File_Status()

# #driver.quit()

# print('....Downloaded....')

for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Michigan\Input'):
 DownloadedFile = file

dfMImap = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Michigan\\Required\\MichiganMapping.xlsx",)
print('Reading the Michigan Mapping file....')
dfMImap = dfMImap[:0]

print('Reading the Michigan State file sheet_name=00000000-00015000....')
dfSheet1 = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Michigan\\Input\\"+str(DownloadedFile), sheet_name='00000000-00015000',engine='pyxlsb')
print('Reading the Michigan State file sheet_name=00015001-00030000....')
dfSheet2 = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Michigan\\Input\\"+str(DownloadedFile), sheet_name='00015001-00030000',engine='pyxlsb')
print('Reading the Michigan State file sheet_name=00030001-99999999....')
dfSheet3 = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Michigan\\Input\\"+str(DownloadedFile), sheet_name='00030001-99999999',engine='pyxlsb')

print('merging all the sheets into single master sheet and writing to excel...')
dfSheet1andSheet2 = pd.concat([dfSheet1,dfSheet2])
dfAllSheets = pd.concat([dfSheet1andSheet2,dfSheet3])
 # Convert nan/null to empty and to integer and to string
dfAllSheets['Facility Street Number'] = dfAllSheets['Facility Street Number'].fillna(1010101010)
dfAllSheets['Facility Street Number'] = dfAllSheets['Facility Street Number'].astype(int)
dfAllSheets['Facility Street Number'] = dfAllSheets['Facility Street Number'].astype(str)
dfAllSheets['Facility Direction'] = dfAllSheets['Facility Direction'].fillna('')
dfAllSheets['Facility Street Name'] = dfAllSheets['Facility Street Name'].fillna('')
dfAllSheets['Facility Suffix Type'] = dfAllSheets['Facility Suffix Type'].fillna('')
dfAllSheets['Tank Location'] = dfAllSheets['Facility Street Number'] + ' ' + dfAllSheets['Facility Direction'] + ' ' + dfAllSheets['Facility Street Name'] + ' ' + dfAllSheets['Facility Suffix Type']
dfAllSheets['Tank Location'] = dfAllSheets['Tank Location'].str.replace('1010101010','')
dfAllSheets['Tank Location'] = dfAllSheets['Tank Location'].str.strip()
dfAllSheets.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Michigan\Output\MichiganStateFile.xlsx', index=False)

print('Reading the Michigan State file....')
dfMI = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Michigan\\Output\\MichiganStateFile.xlsx")
#delete single row
dfMI = dfMI.drop(labels=0, axis=0)

MImap = dfMI[['Facility ID','New Tank ID Number','Tank Location','Facility City','Facility Zip','Tank Instal Date','Tank Capacity','Tank Construction ','Piping Material','Tank Compartments','Tank Content','Facility Name','Facility County','Facility Status']]
MImap.columns = ['Facility Id','Tank ID ','Tank Location','City','Zip Code','Year Installed','Tank Size ','tank construction','piping construction_refined','Secondary Containment (AST)','content description','Facility Name','county','tank status']

print('Merging the Michigan State file with Michigan Mapping file and writing to excel')
MImerge = pd.concat([dfMImap,MImap])
MImerge['State'] = 'Michigan'
MImerge['state_name'] = 'MI'
MImerge['UST or AST'] = 'UST'
MImerge['Tank Tightness'] = 'No'
MImerge['tank construction rating model'] = 'No'
MImerge.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Michigan\Output\MichiganFinal.xlsx', index = False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\L-UST_Data\\LustDataAllStates.xlsx")
MI=LustData[LustData['State Name'] == 'Michigan']

print('writing Michigan Lower underground storage tank data....')
MI.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Michigan\Required\MichiganLustData.xlsx',index = False)

print('Reading Michigan Final data....')
MIFinal =pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Michigan\Output\MichiganFinal.xlsx')

print('Reading Michigan Lust Data....')
MILust=pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Michigan\Required\MichiganLustData.xlsx')

MILust['location_city'] = MILust['Address'] + '_' + MILust['City']
MIFinal['location_city'] = MIFinal['Tank Location'] + '_' + MIFinal['City']
MILust['location_city'] = MILust['location_city'].str.upper()
MIFinal['location_city'] = MIFinal['location_city'].str.upper()
MILustUnique = MILust.drop_duplicates(subset = 'location_city',keep='first')

MIFinalMerged = pd.merge(MIFinal,MILustUnique, on='location_city',how='left')
MIFinal['lust'] = MIFinalMerged['Address'] + '_' + MIFinalMerged['City_y']
MIFinal['lust_status'] = MIFinalMerged['Status']
del MIFinal['location_city']
MIFinal['Year Installed'] = pd.to_datetime(MIFinal['Year Installed'])

print('Merging Michigan Final and Michigan L-UST data')
MIFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Michigan\Output\MichiganFinalMerged.xlsx', index=False)

print('Completed....')






    
