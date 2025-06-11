from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os

PATH = "C:\\Users\\Administrator\\Desktop\\axon_states\\Drivers\\New folder\\chromedriver_win32\\chromedriver.exe"

URL1="https://data.delaware.gov/Energy-and-Environment/Underground-Storage-Tanks/jaq4-q4vs"

URL2="https://data.delaware.gov/Energy-and-Environment/Aboveground-Storage-Tanks/cgmv-7ssg"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Delaware\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()

driver.get(URL1)
driver.implicitly_wait(10)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div/div[2]/div/div/div[1]/div/div[2]/div/div[2]/button')))
driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div/div/div[1]/div/div[2]/div/div[2]/button').click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="export-flannel"]/section/ul/li[1]/a')))
driver.find_element(By.XPATH,'//*[@id="export-flannel"]/section/ul/li[1]/a').click()

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Delaware\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()

driver.get(URL2)
driver.implicitly_wait(10)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div/div[2]/div/div/div[1]/div/div[2]/div/div[2]/button')))
driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div/div/div[1]/div/div[2]/div/div[2]/button').click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="export-flannel"]/section/ul/li[1]/a')))
driver.find_element(By.XPATH,'//*[@id="export-flannel"]/section/ul/li[1]/a').click()

while len(os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Delaware\Input')) < 2:
    time.sleep(0.2)
    print('waiting to download...')

def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Delaware\Input'):
        filesList.append(file)
        filesExtensions = [x.split('.')[-1] for x in filesList]
        print(filesExtensions)
    if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
        time.sleep(3)
        Check_File_Status()
    else:
        pass

Check_File_Status()

print('file downloaded....')
# driver.quit()

dfcsv1 = pd.read_csv("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Delaware\\Input\\Underground_Storage_Tanks.csv")
dfcsv2 = pd.read_csv("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Delaware\\Input\\Aboveground_Storage_Tanks.csv")

dfcsv1.to_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Delaware\\Output\\Underground_Storage_Tanks.xlsx", index=False)
dfcsv2.to_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Delaware\\Output\\Aboveground_Storage_Tanks.xlsx", index=False)

dfDE1 = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Delaware\\Output\\Underground_Storage_Tanks.xlsx")
dfDE2 = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Delaware\\Output\\Aboveground_Storage_Tanks.xlsx")
print('reading ust and ast file....')

print('Reading Delaware mapping file....')
dfDEmap = pd.read_excel(r"C:\Users\Administrator\Desktop\axon_states\states\Delaware\Required\DelawareMapping.xlsx",)
print('Reading the Delaware Mapping file....')
dfDEmap = dfDEmap[:0]

DEmap1 = dfDE1[['ProgID','Unit_Name','Facility_Address1','Facility_City','Facility_Zip','Install_Date','Capacity','Tank_Material','Tank_Substance','Site_Name_UsedBy_Program','Tank_Status']]
DEmap1.columns = ['Facility Id','Tank ID ','Tank Location','City','Zipcode','Year Installed','Tank Size ','tank construction','content description','Facility Name','tank status']

DEmerge1 = pd.concat([dfDEmap,DEmap1])
DEmerge1['UST or AST'] = 'UST'

DEmap2 = dfDE2[['ProgID','Unit_Name','Facility_Address1','Facility_City','Facility_Zip','Install_Date','Capacity','Tank_Material','Tank_Substance','Site_Name_UsedBy_Program','Tank_Status']]
DEmap2.columns = ['Facility Id','Tank ID ','Tank Location','City','Zipcode','Year Installed','Tank Size ','tank construction','content description','Facility Name','tank status']

DEmerge2 = pd.concat([dfDEmap,DEmap2])
DEmerge2['UST or AST'] = 'AST'

print('Merging the UST and AST')

DEmerge = pd.concat([DEmerge1,DEmerge2])
DEmerge['State'] = 'Delaware'
DEmerge['state_name'] = 'DE'
print('C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Delaware\\Output\\DelawareFinal.xlsx')
DEmerge.to_excel('C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Delaware\\Output\\DelawareFinal.xlsx', index = False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\L-UST_Data\\LustDataAllStates.xlsx")
DE=LustData[LustData['State Name'] == 'Delaware']

print('writing Delaware Lower underground storage tank data....')
DE.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Delaware\Required\DelawareLustData.xlsx',index = False)

print('Reading Delaware Final data....')
DEFinal =pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Delaware\Output\DelawareFinal.xlsx')

print('Reading Delaware Lust Data....')
DELust=pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Delaware\Required\DelawareLustData.xlsx')

DELust['location_city'] = DELust['Address'] + '_' + DELust['City']
DEFinal['location_city'] = DEFinal['Tank Location'] + '_' + DEFinal['City']
DELust['location_city'] = DELust['location_city'].str.upper()
DEFinal['location_city'] = DEFinal['location_city'].str.upper()
DELustUnique = DELust.drop_duplicates(subset = 'location_city',keep='first')

DEFinalMerged = pd.merge(DEFinal,DELustUnique, on='location_city',how='left')
DEFinal['lust'] = DEFinalMerged['Address'] + '_' + DEFinalMerged['City_y']
DEFinal['lust_status'] = DEFinalMerged['Status']
del DEFinal['location_city']
DEFinal['Year Installed'] = pd.to_datetime(DEFinal['Year Installed'])

print('Merging Delaware Final and Delaware L-UST data')
DEFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Delaware\Output\DelawareFinalMerged.xlsx', index=False)

print('Completed....') 
