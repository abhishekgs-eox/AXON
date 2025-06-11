from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os


PATH = "F:\Driver\chromedriver.exe"
URL="https://apps.ecology.wa.gov/cleanupsearch/reports/ust"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "F:\\Axon\\Washington\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="table-helpers"]/div/div[1]/div/label[2]')))
driver.find_element(By.XPATH,'//*[@id="table-helpers"]/div/div[1]/div/label[2]').click()
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,'//*[@id="ExportOptions"]/div/div/div[2]/div[2]/div[2]/button[2]/span')))
driver.find_element(By.XPATH,'//*[@id="ExportOptions"]/div/div/div[2]/div[2]/div[2]/button[2]/span').click()

while len(os.listdir(r'F:\Axon\Washington\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')

print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'F:\Axon\Washington\Input'):
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

for file in os.listdir(r'F:\Axon\Washington\Input'):
    DownloadedFile = file


dfWAmap = pd.read_excel("F:\\Axon\\Washington\\Required\\WashingtonMapping.xlsx")
print('Reading the Washington Mapping file....')
dfWAmap = dfWAmap[:0]


#Reading UST Facilities Sheet = Site List
dfSiteList=pd.read_excel("F:\\Axon\\Washington\\Input\\"+str(DownloadedFile), sheet_name="Site List")
# Assign row as column headers
dfSiteList.columns = dfSiteList.iloc[0]
# delete a single row by index value
dfSiteList = dfSiteList.drop(labels=0, axis=0)
print('Reading the UstFacilities file sheet = Site List....')

SiteListmap = dfSiteList[['FacilitySiteID','USTID','Address','City','ZipCode','County']]
SiteListmap.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','county']

SiteListmerge = pd.concat([dfWAmap,SiteListmap])
print('Merging the Site List Sheet with Washington Mapping file and writing to excel')

SiteListmerge.to_excel(r'F:\Axon\Washington\Output\SiteList_Merged.xlsx', index=False)


#Reading UST Facilities Sheet = Tanks
dfTanks=pd.read_excel("F:\\Axon\\Washington\\Input\\"+str(DownloadedFile), sheet_name="Tanks")
print('Reading the UstFacilities file sheet = Tanks....')

Tanksmap = dfTanks[['USTID','InstallDate','ActualCapacity','TankConstruction','PipeConstruction','SiteName','TankStatus']]
Tanksmap.columns = ['Tank ID','Year Installed','Tank Size','tank construction','piping construction_refined','Facility Name','tank status']

Tanksmerge = pd.concat([dfWAmap,Tanksmap])
Tanksmerge['Tank ID'] = Tanksmerge['Tank ID'].astype(str)
print('Merging the Tanks Sheet with Washington Mapping file and writing to excel')
Tanksmerge.to_excel(r'F:\Axon\Washington\Output\Tanks_Merged.xlsx', index=False)


#joining Site List Sheet and Tanks Sheet and merging it to Washington Mapping file
print('Merging Site List and Tanks and write to excel....')
SiteListmerge = SiteListmerge.drop_duplicates(subset = 'Tank ID',keep='first')
SiteList_Tanks = pd.merge(Tanksmerge,SiteListmerge, on='Tank ID',how='left')

SiteList_Tanks.to_excel(r'F:\Axon\Washington\Output\SiteList_Tanks_Merged.xlsx', index=False)

print('Reading the SiteList_Tanks_Merged file....')
SiteList_Tanks_Merged=pd.read_excel("F:\\Axon\\Washington\\Output\\SiteList_Tanks_Merged.xlsx")

dfSiteList_Tanks = SiteList_Tanks_Merged[['Facility Id_y','Tank ID','Tank Location_y','City_y','Zipcode_y','Year Installed_x','Tank Size_x','tank construction_x','piping construction_refined_x','Facility Name_x','county_y','tank status_x']]
dfSiteList_Tanks.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','Year Installed','Tank Size','tank construction','piping construction_refined','Facility Name','county','tank status']


Cleaned_SiteList_Tanks = pd.concat([dfWAmap,dfSiteList_Tanks])
print('Merging Cleaned Data Site List and Tanks with Washington Mapping file and write to excel....')
Cleaned_SiteList_Tanks.to_excel(r'F:\Axon\Washington\Output\Cleaned_SiteList_Tanks_Merged.xlsx', index=False)

#Reading UST Facilities Sheet = Compartments
dfCompartments=pd.read_excel("F:\\Axon\\Washington\\Input\\"+str(DownloadedFile), sheet_name="Compartments")
print('Reading the UstFacilities file sheet = Compartments....')

Compartmentsmap = dfCompartments[['SiteId','CompartmentNumber','StoredSubstance']]
Compartmentsmap.columns = ['Tank ID','Secondary Containment (AST)','content description']

print('Writing the Compartments merged file....')
CompartmentsMerge = pd.concat([dfWAmap,Compartmentsmap])
CompartmentsMerge.to_excel(r'F:\Axon\Washington\Output\Compartments_Merged.xlsx', index=False)

print('Reading the Compartments Merged file....')
Compartments = pd.read_excel("F:\\Axon\\Washington\\Output\\Compartments_Merged.xlsx")
dfCOMUnique = Compartments.drop_duplicates(subset = 'Tank ID',keep='first')

print('Reading Cleaned_SiteList_Tanks file....')
Cleaned_SL_T = pd.read_excel("F:\\Axon\\Washington\\Output\\Cleaned_SiteList_Tanks_Merged.xlsx")

SL_TK_COM = pd.merge(Cleaned_SL_T, dfCOMUnique, on='Tank ID',how='left',suffixes=["_SLTK","_CMPT"])
SL_TK_COM.to_excel(r'F:\Axon\Washington\Output\SL_TK_COM_Merged.xlsx', index=False)

print('Reading the SL_TK_COM_Merged file....')
SL_TK_COM_Merged = pd.read_excel("F:\\Axon\\Washington\\Output\\SL_TK_COM_Merged.xlsx")


Cleaned_SL_TK_COM = SL_TK_COM_Merged[['Facility Id_SLTK','Tank ID','Tank Location_SLTK','City_SLTK','Zipcode_SLTK','Year Installed_SLTK','Tank Size_SLTK','tank construction_SLTK','piping construction_refined_SLTK','Facility Name_SLTK','county_SLTK','tank status_SLTK','Secondary Containment (AST)_CMPT','content description_CMPT']]
Cleaned_SL_TK_COM.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','Year Installed','Tank Size','tank construction','piping construction_refined','Facility Name','county','tank status','Secondary Containment (AST)','content description']

print('Writing the cleaned SL_TK_COM file to excel....')
SL_TK_COM_Merge = pd.concat([dfWAmap,Cleaned_SL_TK_COM])
SL_TK_COM_Merge['State'] = 'Washington'
SL_TK_COM_Merge['state_name'] = 'WA'
SL_TK_COM_Merge['UST or AST'] = 'UST'
SL_TK_COM_Merge['Tank Tightness'] = 'No'
SL_TK_COM_Merge.to_excel(r'F:\Axon\Washington\Output\WashingtonFinal.xlsx', index=False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("F:\\Axon\\Washington\\Required\\LustDataAllStates.xlsx")
WA=LustData[LustData['State Name'] == 'Washington']

print('writing Washington Lower underground storage tank data....')
WA.to_excel(r'F:\Axon\Washington\Required\WashingtonLustData.xlsx',index = False)

print('Reading WashingtonFinal data....')
WAFinal =pd.read_excel("F:\\Axon\\Washington\\Output\\WashingtonFinal.xlsx")

print('Reading Washington Lust Data....')
WALust=pd.read_excel("F:\\Axon\\Washington\\Required\\WashingtonLustData.xlsx")

WALust['location_city'] = WALust['Address'] + '_' + WALust['City']
WALust['location_city'] = WALust['location_city'].str.upper()
WAFinal['location_city'] = WAFinal['Tank Location'] + '_' + WAFinal['City']
WAFinal['location_city'] = WAFinal['location_city'].str.upper()
WALustUnique = WALust.drop_duplicates(subset = 'location_city', keep='first')

WAFinalMerged = pd.merge(WAFinal,WALustUnique, on='location_city',how='left')
WAFinal['lust'] = WAFinalMerged['Address'] + '_' + WAFinalMerged['City_y']
WAFinal['lust status'] = WAFinalMerged['Status']
del WAFinal['location_city']
WAFinal['Year Installed'] = pd.to_datetime(WAFinal['Year Installed'])

print('Merging Washington Final and Washington L-UST data')
WAFinal.to_excel(r'F:\Axon\Washington\Output\WashingtonFinalMerged.xlsx', index=False)

print('Completed....')




















