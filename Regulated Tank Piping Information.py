from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import pandas as pd
import win32com.client
import glob
import time
import os


def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'F:\TankPiping'):
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
URL="https://prodlamp.dep.state.fl.us/www_stcm/publicreports/RegTankPiping"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "F:\\TankPiping"})
driver =  webdriver.Chrome(PATH,options=chromeOptions)
driver.maximize_window()
driver.get(URL)
driver.implicitly_wait(5)

print('Extracting all files from the website')
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
    for file in os.listdir(r'F:\TankPiping'):
        if file == 'RegTankPiping.xls':
            os.renames(r'F:\TankPiping\RegTankPiping.xls', r'F:\TankPiping\\'+str(i.strip())+'.xls')
    driver.get(URL)

print('converting corrupted xls files to xlsx format')
o = win32com.client.Dispatch("Excel.Application")
o.Visible = False
input_dir = r"F:\TankPiping"
output_dir = r"F:\TankPipingXLSX"
files = glob.glob(input_dir + "/*.xls")

for filename in files:
    file = os.path.basename(filename)
    output = output_dir + '/' + file.replace('.xls','.xlsx')
    wb = o.Workbooks.Open(filename)
    wb.ActiveSheet.SaveAs(output,51)
    wb.Close(True)   

print('merging all the files into single file')
CombinedCountyFile = pd.DataFrame()
for Countyfile in os.listdir(output_dir):
    fileDf= pd.read_excel(r"F:\TankPipingXLSX\\"+Countyfile)
    fileDf.columns = fileDf.iloc[12]
    fileDf = fileDf[13:]
    CombinedCountyFile = CombinedCountyFile.append(fileDf,ignore_index= False)
CombinedCountyFile.to_excel(r'F:\RegTankPiping.xlsx', index=False)