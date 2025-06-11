from selenium import webdriver
# from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os

PATH = "C:\\Users\\Administrator\\Desktop\\axon_states\\Drivers\\chromedriver.exe"
URL = "https://adem.alabama.gov/programs/land/ustcompliancemain.cnt"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Alabama\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="content"]/blockquote/a[2]')))
driver.find_element(By.XPATH,'//*[@id="content"]/blockquote/a[2]').click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="content"]/blockquote/a[3]')))
driver.find_element(By.XPATH,'//*[@id="content"]/blockquote/a[3]').click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="content"]/blockquote/a[4]')))
driver.find_element(By.XPATH,'//*[@id="content"]/blockquote/a[4]').click()

while len(os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Alabama\Input')) < 3:
    time.sleep(0.2)
    print('waiting to download...')

def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Alabama\Input'):
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

dfAmap = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Alabama\\Required\\AlabamaMapping.xlsx")
#getting the headers
dfAmap = dfAmap[:0]


#USTsites
dfust=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Alabama\\Input\\USTsites.xlsx")
print("Reading the USTsites file....")
#Renaming the columns
dfUSTmap =dfust[['SITE_ID_NUMBER','SITE_ADDRESS','SITE_CITY','SITE_ZIP','SITE_NAME','COUNTY_NAME']]
dfUSTmap.columns = ['Facility Id','Tank Location','City','Zipcode','Facility Name','county',]
#concate the data frames
print('Merging UST sites .... ')
usite = pd.concat([dfAmap,dfUSTmap])
usite.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Alabama\Output\UTSsites_Merged_data.xlsx', index = False)



#utanks
dfu=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Alabama\\Inputt\\UTanks.xlsx")
print("Reading the UTanks file....")
#Replacing the columns
dfUTanksmap = dfu[['SITE_ID_NUMBER','TANK_NUMBER','INSTALL_DATE_C1','NUMBER_OF_COMPARTMENTS_D1','CAPACITY_D','REMOVAL_DATE_3']]
dfUTanksmap.columns = ['Facility Id','Tank ID','Year Installed','Secondary Containment (AST)','Tank Size','tank status']
#Concate the data frames
print('Merging UTanks .... ')
UT = pd.concat([dfAmap,dfUTanksmap])
UT.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Alabama\Output\UTanks_Merged_data.xlsx', index = False)
UT['State'] = 'Alabama'
UT['state_name'] = 'AL'
UT['Tank Tightness'] = 'No'
UT['UST or AST'] = 'UST'

print('Merging UST sites and Utanks....')
usite = usite.drop_duplicates(subset = 'Facility Id',keep='first')
UT_Usites = pd.merge(UT,usite, on='Facility Id',how='left')

print('Writing all the merged data to excel file....')
#Replacing the columns
Alabama = UST_sites[['State_x', 'state_name_x', 'Facility Id', 'Tank ID_x', 'Tank Location_y', 'City_y', 'Zipcode_y', 'UST or AST_x', 'Year Installed_x', 'Tank Size_x', 'size range_x', 'tank construction_x', 'piping construction_refined_x', 'Secondary Containment (AST)_x', 'content description_x', 'Tank Tightness_x', 'Facility Name_y', 'lust_x', 'tank construction rating model_x', 'county_y', 'tank status_x', 'lust status_x']]
Alabama.columns = ['State', 'state_name', 'Facility Id', 'Tank ID', 'Tank Location', 'City', 'Zipcode', 'UST or AST', 'Year Installed', 'Tank Size', 'size range', 'tank construction', 'piping construction_refined', 'Secondary Containment (AST)', 'content description', 'Tank Tightness', 'Facility Name', 'lust', 'tank construction rating model', 'county', 'tank status', 'lust status']

Alabama.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Alabama\Output\AlabamaFinal.xlsx',index = False)

print('Reading Lower underground storage tank data....')
LustData=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\L-UST_Data\\LustDataAllStates.xlsx")
AL=LustData[LustData['State Name'] == 'Alabama']

print('writing albama Lower underground storage tank data....')
AL.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Alabama\Required\AlabamaLustData.xlsx',index = False)

print('Reading AlabamaFinal data....')
AlabFinal =pd.read_excel( r'C:\Users\Administrator\Desktop\axon_states\states\Alabama\Output\AlabamaFinal.xlsx')

print('Reading Alabama Lust Data....')
AlabLust=pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Alabama\Required\AlabamaLustData.xlsx')

AlabLust['location_city'] = AlabLust['Address'] + '_' + AlabLust['City']
AlabLust['location_city'] = AlabLust['location_city'].str.upper()
AlabFinal['location_city'] = AlabFinal['Tank Location'] +'_'+ AlabFinal['City']
AlabFinal['location_city'] = AlabFinal['location_city'].str.upper()
AlabLustUnique = AlabLust.drop_duplicates(subset = 'location_city',keep='first')

AlabFinalMerged = pd.merge(AlabFinal,AlabLustUnique, on='location_city',how='left')
AlabFinal['lust'] = AlabFinalMerged['Address'] + '_' + AlabFinalMerged['City_y']
AlabFinal['lust status'] = AlabFinalMerged['Status']
del AlabFinal['location_city']

print('Merging AlabamaFinal and Alabama L-UST data')
AlabFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Alabama\Output\AlabamaFinalMerged.xlsx', index=False)

print('Completed....')
















