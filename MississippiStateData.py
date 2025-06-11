from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from zipfile import ZipFile
import os

PATH = "C:\\Users\\Administrator\\Desktop\\axon_states\\Drivers\\chromedriver_win32\\chromedriver.exe"
URL="https://www.mdeq.ms.gov/water/groundwater-assessment-and-remediation/underground-storage-tanks/musterweb/"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Mississippi\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'/html/body/main/div[3]/div/div/div/main/article/div/div[1]/div/div[2]/div/form[3]/p[2]/span/a')))
driver.find_element(By.XPATH,'/html/body/main/div[3]/div/div/div/main/article/div/div[1]/div/div[2]/div/form[3]/p[2]/span/a').click()

while len(os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Mississippi\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')

print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Mississippi\Input'):
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

for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Mississippi\Input'):
    DownloadedFile = file
    
print('Unzipping the file....')

zfile = r'C:\Users\Administrator\Desktop\axon_states\states\Mississippi\Input\\'+str(DownloadedFile)
with ZipFile(zfile) as zipObj:
    zipObj.printdir()
    zipObj.extractall(path="C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Mississippi\\Input") 
    
dfMSmap = pd.read_excel("C:\\Users\Administrator\\Desktop\\axon_states\\states\\Mississippi\\Required\\MississippiMapping.xlsx")
print('Reading the Mississippi Mapping file....')
dfMSmap = dfMSmap[:0]

print('Reading the Mississippi State file....')
dfcsv = pd.read_csv("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Mississippi\\Input\\USTinfo.csv", encoding= 'unicode_escape')

dfcsv.to_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Mississippi\\Output\\MississippiStateFile.xlsx")

dfMS = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Mississippi\\Output\\MississippiStateFile.xlsx")

MSmap = dfMS[['FACILITY_ID','TANK_ID','LocAddr','LocCity','LocZip','DATEINSTALLEDTANK','TANKCAPACITY','TankMatDesc','pipeMatDesc','Substance','FacName','County','TankStatus']]
MSmap.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','Year Installed','Tank Size','tank construction','piping construction_refined','content description','Facility Name','county','tank status']

print('Merging the UST_List file with Mississippi Mapping file and writing to excel')
MSmerge = pd.concat([dfMSmap,MSmap])
MSmerge['State'] = 'Mississippi'
MSmerge['state_name'] = 'MS'
MSmerge['UST or AST'] = 'UST'
MSmerge['Tank Tightness'] = 'No'
MSmerge['tank construction rating model'] = 'No'
MSmerge.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Mississippi\Output\MississippiFinal.xlsx', index = False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\L-UST_Data\\LustDataAllStates.xlsx")
MS=LustData[LustData['State Name'] == 'Mississippi']

print('writing Mississippi Lower underground storage tank data....')
MS.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Mississippi\Required\MississippiLustData.xlsx',index = False)

print('Reading MississippiFinal data....')
MSFinal =pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\states\\Mississippi\\Output\\MississippiFinal.xlsx")

print('Reading Mississippi Lust Data....')
MSLust=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Mississippi\\Required\\MississippiLustData.xlsx")

MSLust['location_city'] = MSLust['Address'] + '_' + MSLust['City']
MSLust['location_city'] = MSLust['location_city'].str.upper()
MSFinal['location_city'] = MSFinal['Tank Location'] + '_' + MSFinal['City']
MSFinal['location_city'] = MSFinal['location_city'].str.upper()
MSLustUnique = MSLust.drop_duplicates(subset = 'location_city', keep='first')

MSFinalMerged = pd.merge(MSFinal,MSLustUnique, on='location_city',how='left')
MSFinal['lust'] = MSFinalMerged['Address'] + '_' + MSFinalMerged['City_y']
MSFinal['lust status'] = MSFinalMerged['Status']
del MSFinal['location_city']
MSFinal['Year Installed'] = pd.to_datetime(MSFinal['Year Installed'])

print('Merging Mississippi Final and Mississippi L-UST data')
MSFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Mississippi\Output\MississippiFinalMerged.xlsx', index=False)

print('Completed....')