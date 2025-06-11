from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os

PATH = "C:\\Users\\Administrator\\Desktop\\axon_states\\Drivers\\chromedriver_win32\\chromedriver.exe"
URL="https://webapps.sfm.illinois.gov/ustsearch/"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\illinois\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="SearchDiv"]/div[4]/div[2]/span[1]/span[1]/span/ul/li[1]/span')))
driver.find_element(By.XPATH,'//*[@id="SearchDiv"]/div[4]/div[2]/span[1]/span[1]/span/ul/li[1]/span').click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="ctl00_MainContent_SearchButton"]')))
driver.find_element(By.XPATH,'//*[@id="ctl00_MainContent_SearchButton"]').click()
time.sleep(2)
driver.switch_to.alert.accept()

WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,'//*[@id="ctl00_MainContent_ExportToCSV"]')))
driver.find_element(By.XPATH,'//*[@id="ctl00_MainContent_ExportToCSV"]').click()

while len(os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\illinois\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')
    
    
print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\illinois\Input'):
        filesList.append(file)
        filesExtensions = [x.split('.')[-1] for x in filesList]
        print(filesExtensions)
    if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
        time.sleep(30)
        Check_File_Status()
    else:
        pass
    
Check_File_Status()

#driver.quit()

print('....Downloaded....')

for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\illinois\Input'):
    DownloadedFile = file

dfILmap = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\illinois\\Required\\IllinoisMapping.xlsx",)
print('Reading the Illinois Mapping file....')
dfILmap = dfILmap[:0]

print('reading csv and converting to excel')
dfILcsv = pd.read_csv(r'C:\Users\Administrator\Desktop\axon_states\states\illinois\Input\USTSearchResults.csv')
dfILcsv.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\illinois\Input\IllinoisUST.xlsx', index=False)

print('reading Illinois state file')
dfIL = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\illinois\\Input\\IllinoisUST.xlsx")

ILmap = dfIL[['Facility ID','Tank ID','Address','City','Zip','Date Installed','Tank Capacity','Equipment Type','Equipment','Product','Facility Name','County','Tank Status']]
ILmap.columns = ['Facility ID','Tank ID','Tank Location','City','Zipcode','Year Installed','Tank Size ','tank construction','piping construction_refined','content description','Facility Name','county','Tank Status']

print('Merging the Illinois UST_List file with Illinois Mapping file and writing to excel')
ILmerge = pd.concat([dfILmap,ILmap])
ILmerge['State'] = 'Illinois'
ILmerge['state_name'] = 'IL'
ILmerge['UST or AST'] = 'UST'
ILmerge.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\illinois\Output\IllinoisFinal.xlsx', index = False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\L-UST_Data\\LustDataAllStates.xlsx")
IL=LustData[LustData['State Name'] == 'Illinois']

print('writing Illinois Lower underground storage tank data....')
IL.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\illinois\Required\IllinoisLustData.xlsx',index = False)

print('Reading IllinoisFinal data....')
ILFinal =pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\illinois\\Output\\IllinoisFinal.xlsx")

print('Reading Illinois Lust Data....')
ILLust=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\illinois\\Required\\IllinoisLustData.xlsx")
 
ILLust['location_city'] = ILLust['Address'] + '_' + ILLust['City']
ILLust['location_city'] = ILLust['location_city'].str.upper()
ILFinal['Tank Location'] = ILFinal['Tank Location'].str.strip()
ILFinal['location_city'] = ILFinal['Tank Location'] + '_' + ILFinal['City']
ILFinal['location_city'] = ILFinal['location_city'].str.upper()
ILLustUnique = ILLust.drop_duplicates(subset = 'location_city', keep='first')

ILFinalMerged = pd.merge(ILFinal,ILLustUnique, on='location_city',how='left')
ILFinal['lust'] = ILFinalMerged['Address'] + '_' + ILFinalMerged['City_y']
ILFinal['lust_status'] = ILFinalMerged['Status']
del ILFinal['location_city']
ILFinal['Year Installed'] = pd.to_datetime(ILFinal['Year Installed'], errors = 'coerce')

print('Merging Illinois Final and Illinois L-UST data')
ILFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\illinois\Output\IllinoisFinalMerged.xlsx', index=False)

print('Completed....')
