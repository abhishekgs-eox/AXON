from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os


PATH = "C:\\Users\\Administrator\\Desktop\\axon_states\\Drivers\\chromedriver_win32\\chromedriver.exe"
URL="https://health.hawaii.gov/shwb/ustlust-data/"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Hawaii\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="content_wrapper"]/div[2]/p[4]/a')))
driver.find_element(By.XPATH,'//*[@id="content_wrapper"]/div[2]/p[4]/a').click()

while len(os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Hawaii\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')

print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Hawaii\Input'):
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

for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Hawaii\Input'):
    DownloadedFile = file
    
dfHImap = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Hawaii\\Required\\HawaiiMapping.xlsx")
print('Reading the Hawaii Mapping file....')
dfHImap = dfHImap[:0]

print('Reading the Hawaii State file....')
dfHI = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Hawaii\\Input\\"+str(DownloadedFile), sheet_name='2018 08 ust listing')

HImap = dfHI[['AltFacilityID','AltTankID','Street Address','City','ZIP Code','InstalledDate','TankCapacity','SubstanceDesc','Facility Name','TankStatusDesc']]
HImap.columns = ['Facility Id','Tank ID ','Tank Location','City','Zipcode','Year Installed','Tank Size ','content description','Facility Name','tank status'] 

print('Merging the UST_List file with Hawaii Mapping file and writing to excel')
HImerge = pd.concat([dfHImap,HImap])
HImerge['State'] = 'Hawaii'
HImerge['state_name'] = 'HI'
HImerge['UST or AST'] = 'UST'
HImerge['Tank Tightness'] = 'No'
HImerge['tank construction rating model'] = 'No'
HImerge.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Hawaii\Output\HawaiiFinal.xlsx', index = False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\L-UST_Data\\LustDataAllStates.xlsx")
HI=LustData[LustData['State Name'] == 'Hawaii']

print('writing Hawaii Lower underground storage tank data....')
HI.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Hawaii\Required\HawaiiLustData.xlsx',index = False)

print('Reading Hawaii Final data....')
HIFinal =pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Hawaii\Output\HawaiiFinal.xlsx')

print('Reading Hawaii Lust Data....')
HILust=pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Hawaii\Required\HawaiiLustData.xlsx')

HILust['location_city'] = HILust['Address'] + '_' + HILust['City']
HIFinal['location_city'] = HIFinal['Tank Location'] + '_' + HIFinal['City']
HILust['location_city'] = HILust['location_city'].str.upper()
HIFinal['location_city'] = HIFinal['location_city'].str.upper()
HILustUnique = HILust.drop_duplicates(subset = 'location_city',keep='first')

HIFinalMerged = pd.merge(HIFinal,HILustUnique, on='location_city',how='left')
HIFinal['lust'] = HIFinalMerged['Address'] + '_' + HIFinalMerged['City_y']
HIFinal['lust_status'] = HIFinalMerged['Status']
del HIFinal['location_city']
HIFinal['Year Installed'] = pd.to_datetime(HIFinal['Year Installed'])

print('Merging Hawaii Final and Hawaii L-UST data')
HIFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Hawaii\Output\HawaiiFinalMerged.xlsx', index=False)

print('Completed....') 

  
    
    
    
    
    
    
    
