from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from zipfile import ZipFile
import time
import pandas as pd
import os

PATH = "F:\Driver\chromedriver.exe"
URL ="https://com.ohio.gov/divisions-and-programs/state-fire-marshal/underground-storage-tanks-bustr/release-prevention-inspections/guides-and-resources/list-of-active-usts"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "F:\\Axon\\Ohio\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="odx-main-content"]/article/div/div[2]/aside/section[1]/div/a')))
driver.find_element(By.XPATH,'//*[@id="odx-main-content"]/article/div/div[2]/aside/section[1]/div/a').click()

while len(os.listdir(r'F:\Axon\Ohio\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')

print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'F:\Axon\Ohio\Input'):
        filesList.append(file)
        filesExtensions = [x.split('.')[-1] for x in filesList]
        print(filesExtensions)
    if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
        time.sleep(3)
        Check_File_Status()
    else:
        pass

Check_File_Status()

#driver.quit()

print('....Downloaded....')

for file in os.listdir(r'F:\Axon\Ohio\Input'):
    DownloadedFile = file
    
print('Unzipping the file....')

zfile = r'F:\Axon\Ohio\Input\\'+str(DownloadedFile)
with ZipFile(zfile) as zipObj:
    zipObj.printdir()
    zipObj.extractall(path="F:\Axon\Ohio\Input")
    
dfOHmap = pd.read_excel("F:\\Axon\\Ohio\\Required\\OhioMapping.xlsx")
print('Reading the Ohio Mapping file....')
dfOHmap = dfOHmap[:0]

print('converting csv to excel')
dfcsv = pd.read_csv("F:\\Axon\\Ohio\\Input\\WebUSTList.csv", encoding='unicode_escape', warn_bad_lines=True, error_bad_lines=False)
dfcsv.to_excel("F:\\Axon\\Ohio\\Input\\OhioFile.xlsx", index=False)

print('reading Ohio state file')
dfOH = pd.read_excel("F:\\Axon\\Ohio\\Input\\OhioFile.xlsx")

OHmap = dfOH[['FacilityNumber','TankNumber','Address','City','Zip','UST','Installation_Date','USTCapacity','Construction','PipingConstructions','TankContent','FacilityName','CountyName','Status']]
OHmap.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','UST or AST','Year Installed','Tank Size','tank construction','piping construction_refined','content description','Facility Name','county','tank status']

print('Merging the ohio UST_List file with Ohio Mapping file and writing to excel')
OHmerge = pd.concat([dfOHmap,OHmap])
OHmerge['State'] = 'Ohio'
OHmerge['state_name'] = 'OH'
OHmerge.to_excel(r'F:\Axon\Ohio\Output\OhioFinal.xlsx', index = False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("F:\\Axon\\Ohio\\Required\\LustDataAllStates.xlsx")
OH=LustData[LustData['State Name'] == 'Ohio']

print('writing Ohio Lower underground storage tank data....')
OH.to_excel(r'F:\Axon\Ohio\Required\OhioLustData.xlsx',index = False)

print('Reading OhioFinal data....')
OHFinal =pd.read_excel("F:\\Axon\\Ohio\\Output\\OhioFinal.xlsx")

print('Reading Ohio Lust Data....')
OHLust=pd.read_excel("F:\\Axon\\Ohio\\Required\\OhioLustData.xlsx")

OHLust['Address']  = OHLust['Address'].astype(str)
OHLust['City'] = OHLust['City'].astype(str) 
OHLust['location_city'] = OHLust['Address'] + '_' + OHLust['City']
OHLust['location_city'] = OHLust['location_city'].str.upper()
OHFinal['location_city'] = OHFinal['Tank Location'] + '_' + OHFinal['City']
OHFinal['location_city'] = OHFinal['location_city'].str.upper()
OHLustUnique = OHLust.drop_duplicates(subset = 'location_city', keep='first')

OHFinalMerged = pd.merge(OHFinal,OHLustUnique, on='location_city',how='left')
OHFinal['lust'] = OHFinalMerged['Address'] + '_' + OHFinalMerged['City_y']
OHFinal['lust status'] = OHFinalMerged['Status']
del OHFinal['location_city']
OHFinal['Year Installed'] = pd.to_datetime(OHFinal['Year Installed'])

print('Merging Ohio Final and Ohio L-UST data')
OHFinal.to_excel(r'F:\Axon\Ohio\Output\OhioFinalMerged.xlsx', index=False)

print('Completed....')
