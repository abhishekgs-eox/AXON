from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os

PATH = "C:\\Users\\Administrator\\Desktop\\axon_states\\Drivers\\chromedriver_win32\\chromedriver.exe"
URL="https://data.colorado.gov/Energy/Regulated-Storage-Tanks-in-Colorado-Oil-Public-Saf/qszy-xfii"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Colorado\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/button')))
driver.find_element(By.XPATH,'//*[@id="app"]/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/button').click()
time.sleep(5)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'/html/body/main/div/div[1]/div/div[2]/div/div/div[1]/div/div[2]/div/div[2]/div/section/ul/li[1]/a')))
driver.find_element(By.XPATH,'/html/body/main/div/div[1]/div/div[2]/div/div/div[1]/div/div[2]/div/div[2]/div/section/ul/li[1]/a').click()

while len(os.listdir(r"C:\Users\Administrator\Desktop\axon_states\states\Colorado\Input")) < 1:
    time.sleep(0.2)
    print('waiting to download...')

print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Colorado\Input'):
        filesList.append(file)
        filesExtensions = [x.split('.')[-1] for x in filesList]
        print(filesExtensions)
    if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
        time.sleep(3)
        Check_File_Status()
    else:
        pass

Check_File_Status()

driver.quit()

print('....Downloaded....')

for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Colorado\Input'):
    DownloadedFile = file

#Reading csv file     
dfcsv = pd.read_csv("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Colorado\\Input\\"+str(DownloadedFile))

#Converting csv to excel
dfcsv.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Colorado\Output\Colorado_Tanks.xlsx', index=False)

dfCOmap = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Colorado\\Required\\ColoradoMapping.xlsx")
print('Reading the Colorado Mapping file....')
dfCOmap = dfCOmap[:0]

print('Reading Colorado State file')
dfCO = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Colorado\\Output\\Colorado_Tanks.xlsx")

COmap = dfCO[['Facility ID','Tank Name','Address','City','Zip Code','Tank Type','Installation Date','Capacity (gallons)','Tank Material','Piping Material','Product','Facility Name','County','Tank Status']]
COmap.columns = ['Facility ID','Tank ID ','Tank Location','City','Zip Code','UST or AST','Year Installed','Tank Size ','tank construction','piping construction_refined','content description','Facility Name','County','Tank Status']

print('Merging the Colorado State tank file with Colorado Mapping file and writing to excel')
COmerge = pd.concat([dfCOmap,COmap])
COmerge['State'] = 'Colorado'
COmerge['state_name'] = 'CO'
COmerge['Tank Tightness'] = 'No'
COmerge['Secondary Containment (AST)'] = 'No'
COmerge['tank construction rating model'] = 'No'
COmerge.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Colorado\Output\ColoradoFinal.xlsx', index = False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("C:\\Users\Administrator\\Desktop\\axon_states\\L-UST_Data\\LustDataAllStates.xlsx")
CO=LustData[LustData['State Name'] == 'Colorado']

print('writing Colorado Lower underground storage tank data....')
CO.to_excel(r'C:\Users\Administrator\Desktop\axon_states\L-UST_Data\LustDataAllStates.xlsx',index = False)

print('Reading Colorado Final data....')
COFinal =pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Colorado\Output\ColoradoFinal.xlsx')

print('Reading Colorado Lust Data....')
COLust=pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\L-UST_Data\LustDataAllStates.xlsx')

COLust['location_city'] = COLust['Address'] + '_' + COLust['City']
COFinal['location_city'] = COFinal['Tank Location'] + '_' + COFinal['City']
COLust['location_city'] = COLust['location_city'].str.upper()
COFinal['location_city'] = COFinal['location_city'].str.upper()
COLustUnique = COLust.drop_duplicates(subset = 'location_city',keep='first')

COFinalMerged = pd.merge(COFinal,COLustUnique, on='location_city',how='left')
COFinal['lust'] = COFinalMerged['Address'] + '_' + COFinalMerged['City_y']
COFinal['lust_status'] = COFinalMerged['Status']
del COFinal['location_city']
COFinal['Year Installed'] = pd.to_datetime(COFinal['Year Installed'])

print('Merging Colorado Final and Colorado L-UST data')
COFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Colorado\Output\ColoradoFinalMerged.xlsx', index=False)

print('Completed....')

 
  
    
    
    
    
    
    
    
    
    
    