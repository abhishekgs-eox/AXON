from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os

PATH = r"C:\Users\Administrator\Desktop\axon_states\Drivers\New folder\chromedriver_win32\chromedriver.exe"
URL="https://legacy.azdeq.gov/databases/ustsearch_drupal.html"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Arizona\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'/html/body/table/tbody/tr/td[2]/table[2]/tbody/tr/td/a')))
driver.find_element(By.XPATH,'/html/body/table/tbody/tr/td[2]/table[2]/tbody/tr/td/a').click()

while len(os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Arizona\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')

def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Arizona\Input'):
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
print('Reading Arizona mapping file....')
dfAZmap = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Arizona\\Required\\ArizonaMapping.xlsx",)
print('Reading the Arizona Mapping file....')
dfAZmap = dfAZmap[:0]

dfUSTList=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Arizona\\Input\\ust_list.xlsx", sheet_name="All USTs")
print(dfUSTList)
#Assign row as column headers
dfUSTList.columns = dfUSTList.iloc[0]
#delete a single row by index value
dfUSTList = dfUSTList.drop(labels=0, axis=0)
print('Reading the UST_List file....')

AZmap = dfUSTList[['UST_FACILITY_ID','TANK_NUM','ADDRESS','CITY','ZIP','TANK_INSTALL_DT','COMP_CAPACITY','TANK_MATRL','PIPE_MATRL','COMP_PRODUCT','FACILITY_NAME','COUNTY','COMP_STATUS']]
AZmap.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','Year Installed','Tank Size','tank construction','piping construction_refined','content description','Facility Name','county','tank status']

print('Merging the UST_List file with Arizona Mapping file and writing to excel')
AZmerge = pd.concat([dfAZmap,AZmap])
AZmerge['State'] = 'Arizona'
AZmerge['state_name'] = 'AZ'
AZmerge['UST or AST'] = 'UST'
AZmerge['Secondary Containment (AST)'] = 'No'
AZmerge['Tank Tightness'] = 'No'
AZmerge['size range'] = 'N/A'
AZmerge.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Arizona\Output\ArizonaFinal.xlsx', index = False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("C:\\Users\Administrator\\Desktop\\axon_states\\L-UST_Data\\LustDataAllStates.xlsx")
AZ=LustData[LustData['State Name'] == 'Arizona']

print('writing Arizona Lower underground storage tank data....')
AZ.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Arizona\Required\ArizonaLustData.xlsx',index = False)

print('Reading Arizona Final data....')
AZFinal =pd.read_excel( r'C:\Users\Administrator\Desktop\axon_states\states\Arizona\Output\ArizonaFinal.xlsx')

print('Reading Arizona Lust Data....')
AZLust=pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Arizona\Required\ArizonaLustData.xlsx')

AZLust['location_city'] = AZLust['Address'] + '_' + AZLust['City']
AZLust['location_city'] = AZLust['location_city'].str.upper()
AZFinal['location_city'] = AZFinal['Tank Location'] + '_' + AZFinal['City']
AZFinal['location_city'] = AZFinal['location_city'].str.upper()
AZLustUnique = AZLust.drop_duplicates(subset = 'location_city',keep='first')

AZFinalMerged = pd.merge(AZFinal,AZLustUnique, on='location_city',how='left')
AZFinal['lust'] = AZFinalMerged['Address'] + '_' + AZFinalMerged['City_y']
AZFinal['lust status'] = AZFinalMerged['Status']
del AZFinal['location_city']

print('Merging Arizona Final and Arizona L-UST data')
AZFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Arizona\Output\ArizonaFinalMerged.xlsx', index=False)

print('Completed....')





















