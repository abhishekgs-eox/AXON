from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os


PATH = "F:\Driver\chromedriver.exe"
URL="https://anrweb.vt.gov/DEC/ERT/DataDump.aspx"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "F:\\Axon\\Vermont\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'F:\Axon\Vermont\Input'):
        filesList.append(file)
        filesExtensions = [x.split('.')[-1] for x in filesList]
        print(filesExtensions)
    if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
        time.sleep(3)
        Check_File_Status()
    else:
        pass


WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'ctl00_body_lbUSTFacility')))
driver.find_element(By.ID,'ctl00_body_lbUSTFacility').click()
while len(os.listdir(r'F:\Axon\Vermont\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')
Check_File_Status()
for file in os.listdir(r'F:\Axon\Vermont\Input'):
    print(file)
    if str(file) == 'ERT_Export.xlsx':
        os.renames(r'F:\Axon\Vermont\Input\ERT_Export.xlsx', r'F:\Axon\Vermont\Input\\UST_Facility.xlsx')
        
        
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'ctl00_body_lbUSTTank')))
driver.find_element(By.ID,'ctl00_body_lbUSTTank').click()
while len(os.listdir(r'F:\Axon\Vermont\Input')) < 2:
    time.sleep(0.2)
    print('waiting to download...')
Check_File_Status()
for file in os.listdir(r'F:\Axon\Vermont\Input'):
    print(file)
    if str(file) == 'ERT_Export.xlsx':
        os.renames(r'F:\Axon\Vermont\Input\ERT_Export.xlsx', r'F:\Axon\Vermont\Input\\UST_Tanks.xlsx')
        
        
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'ctl00_body_lbUSTCompartment')))
driver.find_element(By.ID,'ctl00_body_lbUSTCompartment').click()
while len(os.listdir(r'F:\Axon\Vermont\Input')) < 3:
    time.sleep(0.2)
    print('waiting to download...')
Check_File_Status()
for file in os.listdir(r'F:\Axon\Vermont\Input'):
    print(file)
    if str(file) == 'ERT_Export.xlsx':
        os.renames(r'F:\Axon\Vermont\Input\ERT_Export.xlsx', r'F:\Axon\Vermont\Input\\UST_Compartments.xlsx')
        
    
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'ctl00_body_lbUSTPipe')))
driver.find_element(By.ID,'ctl00_body_lbUSTPipe').click()
while len(os.listdir(r'F:\Axon\Vermont\Input')) < 4:
    time.sleep(0.2)
    print('waiting to download...')
Check_File_Status()
for file in os.listdir(r'F:\Axon\Vermont\Input'):
    print(file)
    if str(file) == 'ERT_Export.xlsx':
        os.renames(r'F:\Axon\Vermont\Input\ERT_Export.xlsx', r'F:\Axon\Vermont\Input\\UST_Pipes.xlsx')
        
print('.....All files Downloaded......') 

dfVTmap = pd.read_excel("F:\\Axon\\Vermont\\Required\\VermontMapping.xlsx")
print('Reading the Vermont Mapping file....')
dfVTmap = dfVTmap[:0]       

print('Reading facility file...')        
Facility = pd.read_excel("F:\\Axon\\Vermont\\Input\\UST_Facility.xlsx")
print('Reading Tanks file...')
Tanks = pd.read_excel("F:\\Axon\\Vermont\\Input\\UST_Tanks.xlsx")
print('Reading Compartments file...')
Compartments = pd.read_excel("F:\\Axon\\Vermont\\Input\\UST_Compartments.xlsx")
print('Reading Pipes file...')
Pipes = pd.read_excel("F:\\Axon\\Vermont\\Input\\UST_Pipes.xlsx")

dfFacility = Facility[['FacilityID','FacilityAddress','FacilityTown','FacilityZip','FacilityName','FacilityCounty']]
dfFacility.columns = ['Facility Id','Tank Location','City','Zipcode','Facility Name','county']

print('merging facility file with map file...')
Facilitymerge = pd.concat([dfVTmap,dfFacility])
Facilitymerge.to_excel(r'F:\Axon\Vermont\Output\Facility.xlsx', index=False)

dfTanks = Tanks[['FacilityID','TankID','Capacity','Protection','TankStatus']]
dfTanks.columns = ['Facility Id','Tank ID ','Tank Size ','tank construction','tank status']

print('merging Tanks file with map file...')
Tanksmerge = pd.concat([dfVTmap,dfTanks])
Tanksmerge.to_excel(r'F:\Axon\Vermont\Output\Tanks.xlsx', index=False)

dfCompartments = Compartments[['FacilityID','CompartmentID','Substance']]
dfCompartments.columns = ['Facility Id','Secondary Containment (AST)','content description']

print('merging Compartments file with map file...')
Compartmentsmerge = pd.concat([dfVTmap,dfCompartments])
Compartmentsmerge.to_excel(r'F:\Axon\Vermont\Output\Compartments.xlsx', index=False)

dfPipes = Pipes[['FacilityID','PipeProtectionType']]
dfPipes.columns = ['Facility Id','piping construction_refined']

print('merging Pipes file with map file...')
Pipesmerge = pd.concat([dfVTmap,dfPipes])
Pipesmerge.to_excel(r'F:\Axon\Vermont\Output\Pipes.xlsx', index=False)

Facilitymerge['Facility Id'] = Facilitymerge['Facility Id'].astype(str)
Tanksmerge['Facility Id'] = Tanksmerge['Facility Id'].astype(str)
FacilityUnique = Facilitymerge.drop_duplicates(subset = 'Facility Id', keep='first')

Tanks_Facility = pd.merge(Tanksmerge,FacilityUnique, on='Facility Id',how='left')


print('merging facility and tanks file on facility id')
Tanks_Facility.to_excel(r'F:\Axon\Vermont\Output\Tanks_Facility.xlsx', index=False)

Tanksmerge['Tank Location'] = Tanks_Facility['Tank Location_y']
Tanksmerge['City'] = Tanks_Facility['City_y']
Tanksmerge['Zipcode'] = Tanks_Facility['Zipcode_y']
Tanksmerge['Facility Name'] = Tanks_Facility['Facility Name_y']
Tanksmerge['county'] = Tanks_Facility['county_y']

Tanksmerge.to_excel(r'F:\Axon\Vermont\Output\Tanks_Facility_merged.xlsx', index=False)

print('merging modified Tanks file and Compartments file on facility id')

Tanksmerge['Facility Id'] = Tanksmerge['Facility Id'].astype(str)
Compartmentsmerge['Facility Id'] = Compartmentsmerge['Facility Id'].astype(str)
CompartmentUnique = Compartmentsmerge.drop_duplicates(subset = 'Facility Id', keep='first')

Facility_Tanks_Compartments = pd.merge(Tanksmerge,CompartmentUnique, on='Facility Id',how='left')
Tanksmerge['Secondary Containment (AST)'] = Facility_Tanks_Compartments['Secondary Containment (AST)_y']
Tanksmerge['content description'] = Facility_Tanks_Compartments['content description_y']      
        
Tanksmerge.to_excel(r'F:\Axon\Vermont\Output\Facility_Tanks_Compartments.xlsx', index=False)

print('merging modifies facility file and pipes file on facility id')
Tanksmerge['Facility Id'] = Tanksmerge['Facility Id'].astype(str)
Pipesmerge['Facility Id'] = Pipesmerge['Facility Id'].astype(str)
PipesUnique = Pipesmerge.drop_duplicates(subset = 'Facility Id', keep='first')

Facility_Tanks_Compartments_Pipes = pd.merge(Tanksmerge,PipesUnique, on='Facility Id',how='left')
Tanksmerge['piping construction_refined'] = Facility_Tanks_Compartments_Pipes['piping construction_refined_y']

Tanksmerge.to_excel(r'F:\Axon\Vermont\Output\Facility_Tanks_Compartments_Pipes.xlsx', index=False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("F:\\Axon\\Vermont\\Required\\LustDataAllStates.xlsx")
VT=LustData[LustData['State Name'] == 'Vermont']

print('writing Vermont Lower underground storage tank data....')
VT.to_excel(r'F:\Axon\Vermont\Required\VermontLustData.xlsx',index = False)

print('Reading Vermont Final data....')
VTFinal =pd.read_excel(r'F:\Axon\Vermont\Output\Facility_Tanks_Compartments_Pipes.xlsx')

print('Reading Vermont Lust Data....')
VTLust=pd.read_excel(r'F:\Axon\Vermont\Required\VermontLustData.xlsx')

VTLust['location_city'] = VTLust['Address'] + '_' + VTLust['City']
VTFinal['location_city'] = VTFinal['Tank Location'] + '_' + VTFinal['City']
VTLust['location_city'] = VTLust['location_city'].str.upper()
VTFinal['location_city'] = VTFinal['location_city'].str.upper()
VTLustUnique = VTLust.drop_duplicates(subset = 'location_city',keep='first')

VTFinalMerged = pd.merge(VTFinal,VTLustUnique, on='location_city',how='left')
VTFinal['lust'] = VTFinalMerged['Address'] + '_' + VTFinalMerged['City_y']
VTFinal['lust_status'] = VTFinalMerged['Status']
del VTFinal['location_city']

VTFinal['State'] = 'Vermont'
VTFinal['state_name'] = 'VT'
VTFinal['UST or AST'] = 'UST'
VTFinal['Tank Tightness'] = 'No'
VTFinal['tank construction rating model'] = 'No'

print('Merging Vermont Final and Vermont L-UST data')
VTFinal.to_excel(r'F:\Axon\Vermont\Output\VermontFinalMerged.xlsx', index=False)

print('Completed....')