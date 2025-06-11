from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os

PATH = "F:\Driver\chromedriver.exe"
URL="https://www.tn.gov/environment/program-areas/ust-underground-storage-tanks/data-reports.html"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "F:\\Axon\\Tennessee\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="main"]/div/div[2]/article/div[2]/div[2]/div/div/div/div/div[1]/div/div/a')))
driver.find_element(By.XPATH,'//*[@id="main"]/div/div[2]/article/div[2]/div[2]/div/div/div/div/div[1]/div/div/a').click()

while len(os.listdir(r'F:\Axon\Tennessee\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')

print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'F:\Axon\Tennessee\Input'):
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

for file in os.listdir(r'F:\Axon\Tennessee\Input'):
    DownloadedFile = file
    
dfTNmap = pd.read_excel("F:\\Axon\\Tennessee\\Required\\TennesseeMapping.xlsx")
print('Reading the Tennessee Mapping file....')
dfTNmap = dfTNmap[:0]

print('Reading the Tennessee State file....')
dfTN = pd.read_excel("F:\\Axon\\Tennessee\\Input\\"+str(DownloadedFile))

TNmap = dfTN[['FACILITY_ID_UST','TANK_NUMBER','FACILITY_ADDRESS1','FACILITY_CITY','FACILITY_ZIP','DATE_TANK_INSTALLED','COMPARTMENT_CAPACITY','TANK_MATERIAL','PIPE_MATERIAL','COMPARTMENT_ID','COMPARTMENT_SUBSTANCE','FACILITY_NAME','COMPARTMENT_OVERALL_STATUS']]
TNmap.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','Year Installed','Tank Size','tank construction','piping construction_refined','Secondary Containment (AST)','content description','Facility Name','tank status']

print('Merging the UST_List file with Tennessee Mapping file and writing to excel')
TNmerge = pd.concat([dfTNmap,TNmap])
TNmerge['State'] = 'Tennessee'
TNmerge['state_name'] = 'TN'
TNmerge['UST or AST'] = 'UST'
TNmerge['Tank Tightness'] = 'No'
TNmerge['tank construction rating model'] = 'No'
TNmerge.to_excel(r'F:\Axon\Tennessee\Output\TennesseeFinal.xlsx', index = False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("F:\\Axon\\Tennessee\\Required\\LustDataAllStates.xlsx")
TN=LustData[LustData['State Name'] == 'Tennessee']

print('writing Tennessee Lower underground storage tank data....')
TN.to_excel(r'F:\Axon\Tennessee\Required\TennesseeLustData.xlsx',index = False)

print('Reading TennesseeFinal data....')
TNFinal =pd.read_excel("F:\\Axon\\Tennessee\\Output\\TennesseeFinal.xlsx")

print('Reading Tennessee Lust Data....')
TNLust=pd.read_excel("F:\\Axon\\Tennessee\\Required\\TennesseeLustData.xlsx")

TNLust['location_city'] = TNLust['Address'] + '_' + TNLust['City']
TNLust['location_city'] = TNLust['location_city'].str.upper()
TNFinal['location_city'] = TNFinal['Tank Location'] + '_' + TNFinal['City']
TNFinal['location_city'] = TNFinal['location_city'].str.upper()
TNLustUnique = TNLust.drop_duplicates(subset = 'location_city', keep='first')

TNFinalMerged = pd.merge(TNFinal,TNLustUnique, on='location_city',how='left')
TNFinal['lust'] = TNFinalMerged['Address'] + '_' + TNFinalMerged['City_y']
TNFinal['lust status'] = TNFinalMerged['Status']
del TNFinal['location_city']

print('Merging Tennessee Final and Tennessee L-UST data')
TNFinal.to_excel(r'F:\Axon\Tennessee\Output\TennesseeFinalMerged.xlsx', index=False)

print('Completed....')

