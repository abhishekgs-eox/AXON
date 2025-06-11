from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os

PATH = "F:\Driver\chromedriver.exe"
URL="https://mydatcp.wi.gov/Home/ServiceDetails/4a171523-04c7-e611-80f6-0050568c4f26?Key=Services_Group"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "F:\\Axon\\Wisconsin\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="strtnewapp"]/fieldset/div/font/b/a')))
driver.find_element(By.XPATH,'//*[@id="strtnewapp"]/fieldset/div/font/b/a').click()

while len(os.listdir(r'F:\Axon\Wisconsin\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')

print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'F:\Axon\Wisconsin\Input'):
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

for file in os.listdir(r'F:\Axon\Wisconsin\Input'):
    DownloadedFile = file
   
dfWImap = pd.read_excel("F:\\Axon\\Wisconsin\\Required\\WisconsinMapping.xlsx")
print('Reading the Wisconsin Mapping file....')
dfWImap = dfWImap[:0]

dfcsv = pd.read_csv("F:\\Axon\\Wisconsin\\Input\\"+str(DownloadedFile))
dfcsv.to_excel("F:\\Axon\\Wisconsin\\Output\\WisconsinStateFile.xlsx", index=False)

print('Reading the Wisconsin State file....')
dfWI = pd.read_excel("F:\\Axon\\Wisconsin\\Output\\WisconsinStateFile.xlsx")

WImap = dfWI[['FacilityReferenceNumber','TankID','PropertyAddress','PropertyCity','PropertyZip','TankType','Capacity','ConstructionMaterial','PipeConstructionMaterial','TankContents','FacilityName','PropertyCounty','TankStatus']]
WImap.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','UST or AST','Tank Size','tank construction','piping construction_refined','content description','Facility Name','county','tank status']

print('Merging the UST_List file with Wisconsin Mapping file and writing to excel')
WImerge = pd.concat([dfWImap,WImap])
WImerge['State'] = 'Wisconsin'
WImerge['state_name'] = 'WI'
WImerge['Tank Tightness'] = 'No'
WImerge['tank construction rating model'] = 'No'
WImerge.to_excel(r'F:\Axon\Wisconsin\Output\WisconsinFinal.xlsx', index = False)


print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("F:\\Axon\\Wisconsin\\Required\\LustDataAllStates.xlsx")
WI=LustData[LustData['State Name'] == 'Wisconsin']

print('writing Wisconsin Lower underground storage tank data....')
WI.to_excel(r'F:\Axon\Wisconsin\Required\WisconsinLustData.xlsx',index = False)

print('Reading WisconsinFinal data....')
WIFinal =pd.read_excel("F:\\Axon\\Wisconsin\\Output\\WisconsinFinal.xlsx")

print('Reading Wisconsin Lust Data....')
WILust=pd.read_excel("F:\\Axon\\Wisconsin\\Required\\WisconsinLustData.xlsx")

WILust['location_city'] = WILust['Address'] + '_' + WILust['City']
WILust['location_city'] = WILust['location_city'].str.upper()
WIFinal['location_city'] = WIFinal['Tank Location'] + '_' + WIFinal['City']
WIFinal['location_city'] = WIFinal['location_city'].str.upper()
WILustUnique = WILust.drop_duplicates(subset = 'location_city', keep='first')

WIFinalMerged = pd.merge(WIFinal,WILustUnique, on='location_city',how='left')
WIFinal['lust'] = WIFinalMerged['Address'] + '_' + WIFinalMerged['City_y']
WIFinal['lust status'] = WIFinalMerged['Status']
del WIFinal['location_city']

print('Merging Wisconsin Final and Wisconsin L-UST data')
WIFinal.to_excel(r'F:\Axon\Wisconsin\Output\WisconsinFinalMerged.xlsx', index=False)

print('Completed....')
