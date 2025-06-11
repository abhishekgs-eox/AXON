from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
import os


def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'F:\CountyFiles'):
        filesList.append(file)
        filesExtensions = [x.split('.')[-1] for x in filesList]
        print(filesExtensions)
    if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
        time.sleep(3)
        Check_File_Status()
    else:
        time.sleep(1)
        pass

PATH = "F:\Driver\chromedriver.exe"
URL="https://prodlamp.dep.state.fl.us/www_stcm/publicreports/FacilityLocTank"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "F:\\CountyFiles"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)




optionsListString = driver.find_element(By.ID,'cid').text
optionsList = optionsListString.split('\n')
optionsList.remove(optionsList[-1])
optionsList.remove(optionsList[-1])

for i in optionsList:
    ele = Select(driver.find_element(By.ID,'cid'))
    ele.select_by_visible_text(i.strip())
    driver.find_element(By.ID,'facPreTrigger').click()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID,'download')))
    driver.find_element(By.ID,'download').click()
    time.sleep(2) #wait time to make file visible in folder
    Check_File_Status()
    for file in os.listdir(r'F:\CountyFiles'):
        if file == 'FacLocTank.xls':
            os.renames(r'F:\CountyFiles\FacLocTank.xls', r'F:\CountyFiles\\'+str(i.strip())+'.xls')
    driver.get(URL)


    

