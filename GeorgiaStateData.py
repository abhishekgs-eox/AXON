from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os

PATH = "C:\\Users\\Administrator\\Desktop\\axon_states\\Drivers\\New folder\\chromedriver_win32\\chromedriver.exe"
URL = "https://epd.georgia.gov/ust-data-and-reporting"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Georgia\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="main-content"]/div/div[3]/div[1]/div/main/div[2]/p[4]/span/span/span/span[1]/a')))
driver.find_element(By.XPATH,'//*[@id="main-content"]/div/div[3]/div[1]/div/main/div[2]/p[4]/span/span/span/span[1]/a').click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="main-content"]/div/div[3]/div[1]/div/main/div[2]/p[6]/span/span/span/span[1]/a')))
driver.find_element(By.XPATH,'//*[@id="main-content"]/div/div[3]/div[1]/div/main/div[2]/p[6]/span/span/span/span[1]/a').click()

while len(os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Georgia\Input')) < 2:
    time.sleep(0.2)
    print('waiting to download...')

def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Georgia\Input'):
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

dfGRmap = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Georgia\\Required\\GeorgiaMapping.xlsx")
print('Reading the Georgia Mapping file....')
dfGRmap = dfGRmap[:0]

dfFultonCounties = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Georgia\\Input\\Appling to Fulton Counties Tank Data 122120.xlsx")
print('Reading Appling to Fulton Counties Tank Data 122120 file....')
#to delete the last row
dfFultonCounties = dfFultonCounties[:-1]

dfGilmer = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Georgia\\Input\\Gilmer to Worth Counties Tank Data_01_2022.xlsx")
print('Reading Gilmer to Worth Counties Tank Data_01_2022 file....')
dfGilmer = dfGilmer[:-1]

for i in range(len(dfFultonCounties.columns)):
    if dfFultonCounties.columns[i] != dfGilmer.columns[i]:
       dfGilmer.rename(columns = {dfGilmer.columns[i]:dfFultonCounties.columns[i]},inplace = True)

dfFulton_gilmer = pd.concat([dfFultonCounties,dfGilmer])
dfFulton_gilmer.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Georgia\Output\Fulton_Gilmer.xlsx', index = False)

#renaming the column
dfFulton_GilmerMap = dfFulton_gilmer[['Facility ID','UST Legacy Tank No.','Facility Street Address','Facility City','Tank Installation Date','Tank Capacity','Construction Description','Pipe Description','Content Description','Facility Name','County','Tank Status']]
dfFulton_GilmerMap.columns = ['Facility Id','Tank ID ','Tank Location','City','Year Installed','Tank Size ','tank construction','piping construction_refined','content description','Facility Name','county','tank status']

#concat the dataframes
print('Merging fulton counties and gilmer counties with  georgia mapping data....')
FultonGilmer=pd.concat([dfGRmap,dfFulton_GilmerMap])
FultonGilmer['State'] = 'Georgia'
FultonGilmer['state_name'] = 'GA'
FultonGilmer['UST or AST'] = 'UST'
FultonGilmer['Secondary Containment (AST)'] = 'No'
FultonGilmer['Tank Tightness'] = 'No'
FultonGilmer.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Georgia\Output\GeorgiaFinal.xlsx', index = False)

print("Reading the L-UST data for all states")
LustData = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\L-UST_Data\\LustDataAllStates.xlsx")
GA=LustData[LustData['State Name'] == 'Georgia']

print("writing the Georgia L-UST data....")
GA.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Georgia\Required\GeorgiaLustData.xlsx', index = False)

print('Reading GeorgiaFinal data....')
GAFinal=pd.read_excel( r'C:\Users\Administrator\Desktop\axon_states\states\Georgia\Output\GeorgiaFinal.xlsx')

print("Reading the Georgia L-UST data....")
GALust=pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Georgia\Required\GeorgiaLustData.xlsx')

GALust['location_city'] = GALust['Address'] + '_' + GALust['City']
GALust['location_city'] = GALust['location_city'].str.upper()
GAFinal['location_city'] = GAFinal['Tank Location'].str.strip() +'_'+ GAFinal['City']
GAFinal['location_city'] = GAFinal['location_city'].str.upper()
GeorgiaLustUnique = GALust.drop_duplicates(subset = 'location_city',keep='first')

GAFinalMerged = pd.merge(GAFinal,GeorgiaLustUnique, on='location_city',how='left')
# GAFinalMerged.to_excel('out222.xlsx', index=False)

GAFinal['lust'] = GAFinalMerged['Address'] + '_' + GAFinalMerged['City_y']
GAFinal['lust status'] = GAFinalMerged['Status']
del GAFinal['location_city']

print('Merging GeorgiaFinal and Georgia L-UST data')
GAFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Georgia\Output\GeorgiaFinalMerged.xlsx', index=False)

print('Completed....')










