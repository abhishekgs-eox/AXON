from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
import pandas as pd
import os

PATH = "F:\Driver\chromedriver.exe"
URL="https://prodlamp.dep.state.fl.us/www_stcm/publicreports/FacilityLocTank"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "F:\\CountyFiles"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

# Dropdown = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cid"]'))))

# for i in Dropdown:
#     WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cid"]/option'+[i]))).click()
#     driver.implicitly_wait(5)
#     WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="download"]'))).click()
#     print('Downloading the files started....')
#     def Check_File_Status():
#         filesExtensions = []
#         filesList = []
#         for file in os.listdir(r'F:\CountyFiles'):
#             filesList.append(file)
#             filesExtensions = [x.split('.')[-1] for x in filesList]
#             print(filesExtensions)
#         if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
#             time.sleep(3)
#             Check_File_Status()
#         else:
#             pass

#     Check_File_Status()
#     driver.get(URL)

# select = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cid"]'))))
# options = select.options
# print(options)
# for index in range(0, len(options) - 1):
#     select.select_by_index(index)
    # do stuff

select = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cid"]'))))

for opt in select.options:
    print(opt.text)
    opt.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="facPreTrigger"]')))
    driver.find_element(By.XPATH,'//*[@id="facPreTrigger"]').click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="download"]'))).click()
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
            pass

    Check_File_Status()
    driver.get(URL)
    driver.implicitly_wait(10)
    
cc = pd.read_excel("F:\\CountyFiles\\BAKER.xls", engine="pyxlsb")    
    





    