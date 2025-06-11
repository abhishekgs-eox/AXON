from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os


PATH = "F:\Driver\chromedriver.exe"
URL="https://deq.nd.gov/FOIA/UST-LUST-DataExport/UST-Tank-Download.aspx"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "F:\\Axon\\NorthDakota\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="ButtonExportExcel"]')))
driver.find_element(By.XPATH,'//*[@id="ButtonExportExcel"]').click()

while len(os.listdir(r'F:\Axon\NorthDakota\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')

print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'F:\Axon\NorthDakota\Input'):
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

for file in os.listdir(r'F:\Axon\NorthDakota\Input'):
    DownloadedFile = file

# Reading the csv file
df_csv = pd.read_csv("F:\\Axon\\NorthDakota\\Input\\"+str(DownloadedFile), on_bad_lines='skip')
df_csv.reset_index()
csv = df_csv.reset_index()
df_csv['temp'] = ''
csv.columns = df_csv.columns
del csv['temp']
# coverting to excel
csv.to_excel(r'F:\Axon\NorthDakota\Output\UST-Tank.xlsx', index=False)

dfNDmap = pd.read_excel("F:\\Axon\\NorthDakota\\Required\\NorthDakotaMapping.xlsx",)
print('Reading the NorthDakota Mapping file....')
dfNDmap = dfNDmap[:0]    

dfNDfile=pd.read_excel("F:\\Axon\\NorthDakota\\Output\\UST-Tank.xlsx")
print('Reading the ust-facility_and_tank-details file....')

NDmap = dfNDfile[['FacilityID',' tnkNumber',' facAddress',' facCity',' facZip',' tnkDateInstalled',' tnkTotalCapacity',' tnkMaterial',' tcoPipeMaterial',' tcoSubstance',' facName',' facCounty',' tnkStatus']]
NDmap.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','Year Installed','Tank Size','tank construction','piping construction_refined','content description','Facility Name','county','tank status']

print('Merging UST-Tank file with North Dakota Mapping file and writing to excel')
NDmerge = pd.concat([dfNDmap,NDmap])
NDmerge['State'] = 'North Dakota'
NDmerge['state_name'] = 'ND'
NDmerge['UST or AST'] = 'UST'
NDmerge['Secondary Containment (AST)'] = 'No'
NDmerge['Tank Tightness'] = 'No'
NDmerge.to_excel(r'F:\Axon\NorthDakota\Output\NorthDakotaFinal.xlsx', index = False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("F:\\Axon\\NorthDakota\\Required\\LustDataAllStates.xlsx")
ND=LustData[LustData['State Name'] == 'North Dakota']

print('writing NorthDakota Lower underground storage tank data....')
ND.to_excel(r'F:\Axon\NorthDakota\Required\NorthDakotaLustData.xlsx',index = False)

print('Reading NorthDakota Final data....')
NDFinal =pd.read_excel( r'F:\Axon\NorthDakota\Output\NorthDakotaFinal.xlsx')

print('Reading NorthDakota Lust Data....')
NDLust=pd.read_excel(r'F:\Axon\NorthDakota\Required\NorthDakotaLustData.xlsx')

NDLust['location_city'] = NDLust['Address'] + '_' + NDLust['City']
NDFinal['location_city'] = NDFinal['Tank Location'] + '_' + NDFinal['City']
NDLust['location_city'] = NDLust['location_city'].str.upper()
NDFinal['location_city'] = NDFinal['location_city'].str.upper()
NDLustUnique = NDLust.drop_duplicates(subset = 'location_city',keep='first')

NDFinalMerged = pd.merge(NDFinal,NDLustUnique, on='location_city',how='left')
NDFinal['lust'] = NDFinalMerged['Address'] + '_' + NDFinalMerged['City_y']
NDFinal['lust status'] = NDFinalMerged['Status']
del NDFinal['location_city']
NDFinal['Year Installed'] = pd.to_datetime(NDFinal['Year Installed'])

print('Merging NorthDakota Final and NorthDakota L-UST data')
NDFinal.to_excel(r'F:\Axon\NorthDakota\Output\NorthDakotaFinalMerged.xlsx', index=False)

print('Completed....') 












