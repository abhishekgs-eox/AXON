from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os
import selenium



PATH = "F:\Driver\chromedriver.exe"
URL="http://cedatareporting.pa.gov/Reportserver/Pages/ReportViewer.aspx?/Public/DEP/Tanks/SSRS/TANKS"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "F:\\Axon\\Pennsylvania\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="ReportViewerControl_ctl04_ctl00"]')))
driver.find_element(By.XPATH,'//*[@id="ReportViewerControl_ctl04_ctl00"]').click()

try:
  i = 0
  while(True):
    element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="ReportViewerControl_AsyncWait_Wait"]/table/tbody/tr/td[2]/span')))
    print("{} True".format(i))
    i += 1
except selenium.common.exceptions.TimeoutException:
  print("False")

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="ReportViewerControl_ctl05_ctl04_ctl00_ButtonLink"]')))
driver.find_element(By.XPATH,'//*[@id="ReportViewerControl_ctl05_ctl04_ctl00_ButtonLink"]').click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="ReportViewerControl_ctl05_ctl04_ctl00_Menu"]/div[7]/a')))
driver.find_element(By.XPATH,'//*[@id="ReportViewerControl_ctl05_ctl04_ctl00_Menu"]/div[7]/a').click()


while len(os.listdir(r'F:\Axon\Pennsylvania\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')

print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'F:\Axon\Pennsylvania\Input'):
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

for file in os.listdir(r'F:\Axon\Pennsylvania\Input'):
    DownloadedFile = file
    

dfcsv = pd.read_csv("F:\\Axon\\Pennsylvania\\Input\\"+str(DownloadedFile))

dfcsv.to_excel("F:\\Axon\\Pennsylvania\\Output\\TanksXLSX.xlsx", index=False)

print('Reading the Pennsylvania State file....')
dfPA = pd.read_excel("F:\\Axon\\Pennsylvania\\Output\\TanksXLSX.xlsx")

dfPAmap = pd.read_excel("F:\\Axon\\Pennsylvania\\Required\\PennsylvaniaMapping.xlsx",)
print('Reading the Pennsylvania Mapping file....')
dfPAmap = dfPAmap[:0]

PAmap = dfPA[['SITE_ID','SEQ_NUMBER','PF_ADDRESS1','PF_CITY','PF_ZIP','TANK_CODE','DATE_INSTALLED','CAPACITY','SUBSTANCE_CODE','PF_NAME','COUNTY','STATUS']]
PAmap.columns = ['Facility Id','Tank ID ','Tank Location','City','Zipcode','UST or AST','Year Installed','Tank Size ','content description','Facility Name','county','tank status']

print('Merging the UST_List file with Pennsylvania Mapping file and writing to excel')
PAmerge = pd.concat([dfPAmap,PAmap])
PAmerge['State'] = 'Pennsylvania'
PAmerge['state_name'] = 'PA'
PAmerge['Tank Tightness'] = 'No'
PAmerge['tank construction rating model'] = 'No'
PAmerge.to_excel(r'F:\Axon\Pennsylvania\Output\PennsylvaniaFinal.xlsx', index = False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("F:\\Axon\\Pennsylvania\\Required\\LustDataAllStates.xlsx")
PA=LustData[LustData['State Name'] == 'Pennsylvania']

print('writing Pennsylvania Lower underground storage tank data....')
PA.to_excel(r'F:\Axon\Pennsylvania\Required\PennsylvaniaLustData.xlsx',index = False)

print('Reading Pennsylvania Final data....')
PAFinal =pd.read_excel(r'F:\Axon\Pennsylvania\Output\PennsylvaniaFinal.xlsx')

print('Reading Pennsylvania Lust Data....')
PALust=pd.read_excel(r'F:\Axon\Pennsylvania\Required\PennsylvaniaLustData.xlsx')

PALust['location_city'] = PALust['Address'] + '_' + PALust['City']
PAFinal['location_city'] = PAFinal['Tank Location'] + '_' + PAFinal['City']
PALust['location_city'] = PALust['location_city'].str.upper()
PAFinal['location_city'] = PAFinal['location_city'].str.upper()
PALustUnique = PALust.drop_duplicates(subset = 'location_city',keep='first')

PAFinalMerged = pd.merge(PAFinal,PALustUnique, on='location_city',how='left')
PAFinal['lust'] = PAFinalMerged['Address'] + '_' + PAFinalMerged['City_y']
PAFinal['lust_status'] = PAFinalMerged['Status']
del PAFinal['location_city']
PAFinal['Year Installed'] = pd.to_datetime(PAFinal['Year Installed'])

PAFinal['tank status1'] = ''
PAFinal.loc[PAFinal['tank status'] == 'C', 'tank status1'] = 'Closed'
PAFinal.loc[PAFinal['tank status'] == 'T', 'tank status1'] = 'Temporarly out of services'
PAFinal['tank status'] = PAFinal['tank status1']
del PAFinal['tank status1']

print('Merging Pennsylvania Final and Pennsylvania L-UST data')
PAFinal.to_excel(r'F:\Axon\Pennsylvania\Output\PennsylvaniaFinalMerged.xlsx', index=False)

print('Completed....') 
