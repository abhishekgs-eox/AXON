from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from zipfile import ZipFile
import time
import pandas as pd
import os

#Chrome Driver path
PATH = "F:\Driver\chromedriver.exe"
#Virginia Website URL
URL = "https://www.deq.virginia.gov/land-waste/petroleum-tanks/storage-tanks/aboveground-storage-tanks"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "F:\\Axon\\Virginia\\Input"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="link_1628864408988"]')))
driver.find_element(By.XPATH,'//*[@id="link_1628864408988"]').click()

while len(os.listdir(r'F:\Axon\Virginia\Input')) < 1:
    time.sleep(0.2)
    print('waiting to download...')

print('-------Downloading the files -------')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'F:\Axon\Virginia\Input'):
        filesList.append(file)
        filesExtensions = [x.split('.')[-1] for x in filesList]
        print(filesExtensions)
    if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
        time.sleep(3)
        Check_File_Status()
    else:
        pass

Check_File_Status()

print('-------Downloading the files is done-------')

for file in os.listdir(r'F:\Axon\Virginia\Input'):
    DownloadedFile = file

print('Unzipping the file....')

zfile = r'F:\Axon\Virginia\Input\\'+str(DownloadedFile)
with ZipFile(zfile) as zipObj:
    zipObj.printdir()
    zipObj.extractall(path="F:\Axon\Virginia\Input")    

print('Reading Virginia Mapping file....')
dfKmap = pd.read_excel("F:\\Axon\\Virginia\\Required\\VirginiaMapping.xlsx")
#getting the headers
dfKmap = dfKmap[:0]

dfTXT = pd.read_csv("F:\\Axon\\Virginia\\Input\\tanks.txt", error_bad_lines=False)