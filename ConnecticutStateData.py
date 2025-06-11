from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os


PATH = "C:\\Users\\Administrator\\Desktop\\axon_states\\Drivers\\New folder\\chromedriver_win32\\chromedriver.exe"
URL="https://catalog.data.gov/dataset/underground-storage-tanks-usts-facility-and-tank-details/resource/5a58d5ee-eecb-4946-b52d-68762da9a5ca?inner_span=True|"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Connecticut\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="content"]/div[2]/section/div/div[1]/ul/li/a')))
driver.find_element(By.XPATH,'//*[@id="content"]/div[2]/section/div/div[1]/ul/li/a').click()

while len(os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Connecticut\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')

print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Connecticut\Input'):
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

for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Connecticut\Input'):
    DownloadedFile = file
    
# Reading the csv file
df_csv = pd.read_csv("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Connecticut\\Input\\"+str(DownloadedFile))
#coverting to excel
df_csv.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Connecticut\Output\ust-facility_and_tank-details.xlsx', index=False)

dfCTmap = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Connecticut\\Required\\ConnecticutMapping.xlsx",)
print('Reading the Connecticut Mapping file....')
dfCTmap = dfCTmap[:0]

dfCTfile=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Connecticut\\Output\\ust-facility_and_tank-details.xlsx")
print('Reading the ust-facility_and_tank-details file....')

CTmap =  dfCTfile[['UST Site ID Number','Tank No.','Site Address','Site City','Site Zip','Installation Date','Estimated Total Capacity (gallons)','Construction Type - Tank','Construction Type - Piping','Substance Currently Stored','Site Name','Status of Tank']]
CTmap.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','Year Installed','Tank Size','tank construction','piping construction_refined','content description','Facility Name','tank status']

print('Merging the ust-facility_and_tank-details file with Connecticut Mapping file and writing to excel')
CTmerge = pd.concat([dfCTmap,CTmap])
CTmerge['State'] = 'Connecticut'
CTmerge['state_name'] = 'CT'
CTmerge['UST or AST'] = 'UST'
CTmerge['Secondary Containment (AST)'] = 'No'
CTmerge['Tank Tightness'] = 'No'
CTmerge.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Connecticut\Output\ConnecticutFinal.xlsx', index = False)


print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\L-UST_Data\\LustDataAllStates.xlsx")
CT=LustData[LustData['State Name'] == 'Connecticut']

print('writing Connecticut Lower underground storage tank data....')
CT.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Connecticut\Required\ConnecticutLustData.xlsx',index = False)

print('Reading Connecticut Final data....')
CTFinal =pd.read_excel( r'C:\Users\Administrator\Desktop\axon_states\states\Connecticut\Output\ConnecticutFinal.xlsx')

print('Reading Connecticut Lust Data....')
CTLust=pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Connecticut\Required\ConnecticutLustData.xlsx')

CTLust['location_city'] = CTLust['Address'] + '_' + CTLust['City']
CTFinal['location_city'] = CTFinal['Tank Location'] + '_' + CTFinal['City']
CTLust['location_city'] = CTLust['location_city'].str.upper()
CTFinal['location_city'] = CTFinal['location_city'].str.upper()
CTLustUnique = CTLust.drop_duplicates(subset = 'location_city',keep='first')

CTFinalMerged = pd.merge(CTFinal,CTLustUnique, on='location_city',how='left')
CTFinal['lust'] = CTFinalMerged['Address'] + '_' + CTFinalMerged['City_y']
CTFinal['lust status'] = CTFinalMerged['Status']
del CTFinal['location_city']
CTFinal['Year Installed'] = pd.to_datetime(CTFinal['Year Installed'])

print('Merging Connecticut Final and Connecticut L-UST data')
CTFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Connecticut\Output\ConnecticutFinalMerged.xlsx', index=False)

print('Completed....')   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

