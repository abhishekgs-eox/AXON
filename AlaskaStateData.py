from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import time
import pandas as pd
import os
from selenium.webdriver import ActionChains
from msedge.selenium_tools import Edge, EdgeOptions


#PATH = r'C:\Users\Administrator\Desktop\axon_states\Drivers\New folder\chromedriver_win32\chromedriver.exe'

#URL="https://dec.alaska.gov/Applications/SPAR/PublicUST/USTSearch/"


#options = EdgeOptions()
#options.use_chromium = True
#options.add_experimental_option("prefs", {"download.default_directory": r"C:\Users\Administrator\Desktop\axon_states\states\Alaska\Input"})
#options.add_argument("user-data-dir=C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Alaska\\chromedata")
#driver = Edge(executable_path=r"C:\Users\Administrator\Desktop\axon_states\Drivers\New folder\edgedriver_win64 (4)\msedgedriver.exe", options=options)
#driver.maximize_window()
#driver.get(URL)
#WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="content"]/div[1]/div[1]/p[4]/a')))
#driver.find_element(By.XPATH,'//*[@id="content"]/div[1]/div[1]/p[4]/a').click()

while len(os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Alaska\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')

print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Alaska\Input'):
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

for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Alaska\Input'):
    DownloadedFile = file

dfAKmap = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Alaska\\Required\\AlaskaMapping.xlsx",)
print('Reading the Alaska Mapping file....')
dfAKmap = dfAKmap[:0]

dfAKfile=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Alaska\\Input\\"+str(DownloadedFile))
# Assign row as column headers
dfAKfile.columns = dfAKfile.iloc[0]
# delete a single row by index value
dfAKfile = dfAKfile.drop(labels=0, axis=0)
print('Reading the Ust all facilities file....')

AKmap = dfAKfile[['Facility ID','Tank ID','Address','City','Zip','Date Installed','Tank Capacity','Substance','Facility Name','Tank Status Desc']]
AKmap.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','Year Installed','Tank Size','content description','Facility Name','tank status']

print('Merging the UST_List file with Alaska Mapping file and writing to excel')
AKmerge = pd.concat([dfAKmap,AKmap])
AKmerge['State'] = 'Alaska'
AKmerge['state_name'] = 'AK'
AKmerge['UST or AST'] = 'UST'
AKmerge['Secondary Containment (AST)'] = 'No'
AKmerge['Tank Tightness'] = 'No'
AKmerge.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Alaska\Output\AlaskaFinal.xlsx', index = False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\L-UST_Data\\LustDataAllStates.xlsx")
AK=LustData[LustData['State Name'] == 'Alaska']

print('writing Alaska Lower underground storage tank data....')
AK.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Alaska\Required\AlaskaLustData.xlsx',index = False)

print('Reading Alaska Final data....')
AKFinal =pd.read_excel( r'C:\Users\Administrator\Desktop\axon_states\states\Alaska\Output\AlaskaFinal.xlsx')

print('Reading Alaska Lust Data....')
AKLust=pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Alaska\Required\AlaskaLustData.xlsx')

AKLust['location_city'] = AKLust['Address'] + '_' + AKLust['City']
AKFinal['location_city'] = AKFinal['Tank Location'] + '_' + AKFinal['City']
AKLust['location_city'] = AKLust['location_city'].str.upper()
AKFinal['location_city'] = AKFinal['location_city'].str.upper()
AKLustUnique = AKLust.drop_duplicates(subset = 'location_city',keep='first')

AKFinalMerged = pd.merge(AKFinal,AKLustUnique, on='location_city',how='left')
AKFinal['lust'] = AKFinalMerged['Address'] + '_' + AKFinalMerged['City_y']
AKFinal['lust status'] = AKFinalMerged['Status']
del AKFinal['location_city']

print('Merging Alaska Final and Alaska L-UST data')
AKFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Alaska\Output\AlaskaFinalMerged.xlsx', index=False)

print('Completed....')











    
    

