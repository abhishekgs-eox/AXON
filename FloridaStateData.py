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


# print('Running FacilityLocTank link')
# def Check_File_Status_ALLtanks():
#     filesExtensions = []
#     filesList = []
#     for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\FacilityLocTank'):
#         filesList.append(file)
#         filesExtensions = [x.split('.')[-1] for x in filesList]
#         print(filesExtensions)
#     if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
#         time.sleep(3)
#         Check_File_Status_ALLtanks()
#     else:
#         time.sleep(1)
#         pass

# PATH = "C:\\Users\\Administrator\\Desktop\\axon_states\\Drivers\\chromedriver_win32\\chromedriver.exe"
# URL_ALLTANKS="https://prodlamp.dep.state.fl.us/www_stcm/publicreports/FacilityLocTank"

# chromeOptions = Options()
# chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Florida\\FacilityLocTank"})
# driver =  webdriver.Chrome(PATH,options=chromeOptions)
# driver.maximize_window()
# driver.get(URL_ALLTANKS)
# driver.implicitly_wait(5)

# print('Extracting all files from the website')
# time.sleep(35)
# optionsListString = driver.find_element(By.ID,'cid').text
# optionsList = optionsListString.split('\n')
# optionsList.remove(optionsList[-1])
# optionsList.remove(optionsList[-1])

# for i in optionsList:
#     time.sleep(35)
#     ele = Select(driver.find_element(By.ID,'cid'))
#     ele.select_by_visible_text(i.strip())
#     driver.find_element(By.ID,'facPreTrigger').click()
#     WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID,'download')))
#     driver.find_element(By.ID,'download').click()
#     time.sleep(6) #wait time to make file visible in folder
#     Check_File_Status_ALLtanks()
# for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\FacilityLocTank'):
#         if file == 'FacLocTank.xls':
#             os.renames(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\FacilityLocTank\FacLocTank.xls', r'C:\Users\Administrator\Desktop\axon_states\states\Florida\FacilityLocTank\\'+str(i.strip())+'.xls')
# # driver.get(URL_ALLTANKS)

# print('converting corrupted xls files to xlsx format')
# o = win32com.client.Dispatch("Excel.Application")
# o.Visible = False
# input_dir = r"C:\Users\Administrator\Desktop\axon_states\states\Florida\FacilityLocTank"
# output_dir = r"C:\Users\Administrator\Desktop\axon_states\states\Florida\FacilityLocTankXLSX"
# files = glob.glob(input_dir + "/*.xls")

# for filename in files:
#     file = os.path.basename(filename)
#     output = output_dir + '/' + file.replace('.xls','.xlsx')
#     wb = o.Workbooks.Open(filename)
#     wb.ActiveSheet.SaveAs(output,51)
#     wb.Close(True)  

# print('merging all the files into single file')
# CombinedCountyFile = pd.DataFrame()
# for Countyfile in os.listdir(output_dir):
#     fileDf= pd.read_excel(r"C:\Users\Administrator\Desktop\axon_states\states\Florida\FacilityLocTankXLSX\\"+Countyfile)
#     fileDf.columns = fileDf.iloc[12]
#     fileDf = fileDf[13:]
#     CombinedCountyFile = CombinedCountyFile.append(fileDf,ignore_index= False)
# CombinedCountyFile.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\Input\FacLocTank.xlsx', index=False)

# # print('Running RegTankConstruction link')
# # def Check_File_Status_Construction():
# #     filesExtensions = []
# #     filesList = []
# #     for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\TankConstruction'):
# #         filesList.append(file)
# #         filesExtensions = [x.split('.')[-1] for x in filesList]
# #         print(filesExtensions)
# #     if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
# #         time.sleep(35)
# #         Check_File_Status_Construction()
# #     else:
# #         time.sleep(35)
# #         pass


# # URL_Construction="https://prodlamp.dep.state.fl.us/www_stcm/publicreports/RegTankConstruction"

# # chromeOptions = Options()
# # chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Florida\\TankConstruction"})
# # driver =  webdriver.Chrome(PATH,options=chromeOptions)
# # driver.maximize_window()
# # driver.get(URL_Construction)
# # driver.implicitly_wait(5)

# # print('Extracting all files from the website')
# # time.sleep(35)
# # optionsListString = driver.find_element(By.ID,'cid').text
# # optionsList = optionsListString.split('\n')
# # optionsList.remove(optionsList[-1])
# # optionsList.remove(optionsList[-1])

# # for i in optionsList:
# #     time.sleep(35)
# #     ele = Select(driver.find_element(By.ID,'cid'))
# #     ele.select_by_visible_text(i.strip())
# #     driver.find_element(By.ID,'facPreTrigger').click()
# #     WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID,'download')))
# #     driver.find_element(By.ID,'download').click()
# #     time.sleep(35) #wait time to make file visible in folder
# #     Check_File_Status_Construction()
# #     for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\TankConstruction'):
# #         if file == 'RegTankConstruction.xls':
# #             os.renames(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\TankConstruction\RegTankConstruction.xls', r'C:\Users\Administrator\Desktop\axon_states\states\Florida\TankConstruction\\'+str(i.strip())+'.xls')
# #     driver.get(URL_Construction)

# # print('converting corrupted xls files to xlsx format')
# # o = win32com.client.Dispatch("Excel.Application")
# # o.Visible = False
# # input_dir = r"C:\Users\Administrator\Desktop\axon_states\states\Florida\TankConstruction"
# # output_dir = r"C:\Users\Administrator\Desktop\axon_states\states\Florida\TankConstructionXLSX"
# # files = glob.glob(input_dir + "/*.xls")

# # for filename in files:
# #     file = os.path.basename(filename)
# #     output = output_dir + '/' + file.replace('.xls','.xlsx')
# #     wb = o.Workbooks.Open(filename)
# #     wb.ActiveSheet.SaveAs(output,51)
# #     wb.Close(True)
    
# # print('merging all the files into single file')
# # CombinedCountyFile = pd.DataFrame()
# # for Countyfile in os.listdir(output_dir):
# #     fileDf= pd.read_excel(r"C:\Users\Administrator\Desktop\axon_states\states\Florida\TankConstructionXLSX\\"+Countyfile)
# #     fileDf.columns = fileDf.iloc[13]
# #     fileDf = fileDf[14:]
# #     CombinedCountyFile = CombinedCountyFile.append(fileDf,ignore_index= False)
# # CombinedCountyFile.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\Input\RegTankConstruction.xlsx', index=False)

# # print('Running RegTankPiping link')
# # def Check_File_Status_Piping():
# #     filesExtensions = []
# #     filesList = []
# #     for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\TankPiping'):
# #         filesList.append(file)
# #         filesExtensions = [x.split('.')[-1] for x in filesList]
# #         print(filesExtensions)
# #     if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
# #         time.sleep(6)
# #         Check_File_Status_Piping()
# #     else:
# #         time.sleep(3)
# #         pass

# # URL_Piping="https://prodlamp.dep.state.fl.us/www_stcm/publicreports/RegTankPiping"

# # chromeOptions = Options()
# # chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Florida\\TankPiping"})
# # driver =  webdriver.Chrome(PATH,options=chromeOptions)
# # driver.maximize_window()
# # driver.get(URL_Piping)
# # driver.implicitly_wait(5)

# # print('Extracting all files from the website')
# # time.sleep(35)
# # optionsListString = driver.find_element(By.ID,'cid').text
# # optionsList = optionsListString.split('\n')
# # optionsList.remove(optionsList[-1])
# # optionsList.remove(optionsList[-1])

# # for i in optionsList:
# #     time.sleep(35)
# #     ele = Select(driver.find_element(By.ID,'cid'))
# #     ele.select_by_visible_text(i.strip())
# #     driver.find_element(By.ID,'facPreTrigger').click()
# #     WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID,'download')))
# #     driver.find_element(By.ID,'download').click()
# #     time.sleep(6) #wait time to make file visible in folder
# #     Check_File_Status_Piping()
# #     for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\TankPiping\\'):
# #         if file == 'RegTankPiping.xls':
# #             os.renames(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\TankPiping\RegTankPiping.xls', r'C:\Users\Administrator\Desktop\axon_states\states\Florida\TankPiping\\'+str(i.strip())+'.xls')
# #     driver.get(URL_Piping)

# # print('converting corrupted xls files to xlsx format')
# # o = win32com.client.Dispatch("Excel.Application")
# # o.Visible = False
# # input_dir = r"C:\Users\Administrator\Desktop\axon_states\states\Florida\TankPiping"
# # output_dir = r"C:\Users\Administrator\Desktop\axon_states\states\Florida\TankPipingXLSX"
# # files = glob.glob(input_dir + "/*.xls")

# # for filename in files:
# #     file = os.path.basename(filename)
# #     output = output_dir + '/' + file.replace('.xls','.xlsx')
# #     wb = o.Workbooks.Open(filename)
# #     wb.ActiveSheet.SaveAs(output,51)
# #     wb.Close(True)

# print('merging all the files into single file')
# CombinedCountyFile = pd.DataFrame()
# for Countyfile in os.listdir(output_dir):
#     fileDf= pd.read_excel(r"C:\Users\Administrator\Desktop\axon_states\states\Florida\TankPipingXLSX\\"+Countyfile)
#     fileDf.columns = fileDf.iloc[12]
#     fileDf = fileDf[13:]
#     CombinedCountyFile = CombinedCountyFile.append(fileDf,ignore_index= False)
# CombinedCountyFile.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\Input\RegTankPiping.xlsx', index=False)

# print('Processing All the dowloaded files and merging process started')
# dfFLmap = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Florida\\Required\\FloridaMapping.xlsx")
# # print('Reading the Florida Mapping file....')
# dfFLmap = dfFLmap[:0]

# # print('Reading FacLocTank file....')
# AllTanks = pd.read_excel("C:\\Users\\Administrator\Desktop\\axon_states\\states\\Florida\\Output\\FacLocTank.xlsx")

# dfAllTanks = AllTanks[['FAC ID','TKID','FAC ADDR','FAC CITY','FAC ZIP','INSTALL','CAPACITY','CONTDESC','FAC NAME','COUNTY','TKSTAT']]
# dfAllTanks.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','Year Installed','Tank Size','content description','Facility Name','county','tank status']

# print('Merging the FacLocTank with Florida Mapping file and writing to excel')

# AllTanksmerge = pd.concat([dfFLmap,dfAllTanks])

# AllTanksmerge.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\Output\AllTanks_Merged.xlsx', index=False)

# print('Reading TankConstruction file....')
# Contruction = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Florida\\Output\\TankConstruction.xlsx")

# dfConstruction = Contruction[['FAC ID','TKID','CONSDESC']]
# dfConstruction.columns = ['Facility Id','Tank ID','tank construction']

# print('Merging the TankConstruction with Florida Mapping file and writing to excel')

# Constructionmerge = pd.concat([dfFLmap,dfConstruction])

# Constructionmerge.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\Output\Construction_Merged.xlsx', index=False)

# print('Reading TankPiping file....')
# Piping = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Florida\\Output\\TankPiping.xlsx")

# dfPiping = Piping[['FAC ID','TKID','PIPEDESC']]
# dfPiping.columns = ['Facility Id','Tank ID','piping construction_refined']

# print('Merging the TankPiping with Florida Mapping file and writing to excel')

# Pipingmerge = pd.concat([dfFLmap,dfPiping])

# Pipingmerge.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\Output\Piping_Merged.xlsx', index=False)

# print('Merging the FacLocTank and TankConstruction file and writing to excel')

# AllTanksmerge['Facility Id'] = AllTanksmerge['Facility Id'].astype(str)
# AllTanksmerge['Tank ID'] = AllTanksmerge['Tank ID'].astype(str)
# AllTanksmerge['FacilityID_TankID'] = AllTanksmerge['Facility Id'] + '_' + AllTanksmerge['Tank ID']
# AllTanksmerge['FacilityID_TankID'] = AllTanksmerge['FacilityID_TankID'].str.upper()

# Constructionmerge['Facility Id'] = Constructionmerge['Facility Id'].astype(str)
# Constructionmerge['Tank ID'] = Constructionmerge['Tank ID'].astype(str)
# Constructionmerge['FacilityID_TankID'] = Constructionmerge['Facility Id'] + '_' + Constructionmerge['Tank ID']
# Constructionmerge['FacilityID_TankID'] = Constructionmerge['FacilityID_TankID'].str.upper()
# ConstructionUnique = Constructionmerge.drop_duplicates(subset = 'FacilityID_TankID', keep='first')

# AllTanks_Contruction = pd.merge(AllTanksmerge,ConstructionUnique, on='FacilityID_TankID',how='left')

# print('Merging the FacLocTank and TankPiping file and writing to excel')

# AllTanksmerge['Facility Id'] = AllTanksmerge['Facility Id'].astype(str)
# AllTanksmerge['Tank ID'] = AllTanksmerge['Tank ID'].astype(str)
# AllTanksmerge['FacilityID_TankID'] = AllTanksmerge['Facility Id'] + '_' + AllTanksmerge['Tank ID']
# AllTanksmerge['FacilityID_TankID'] = AllTanksmerge['FacilityID_TankID'].str.upper()

# Pipingmerge['Facility Id'] = Pipingmerge['Facility Id'].astype(str)
# Pipingmerge['Tank ID'] = Pipingmerge['Tank ID'].astype(str)
# Pipingmerge['FacilityID_TankID'] = Pipingmerge['Facility Id'] + '_' + Pipingmerge['Tank ID']
# Pipingmerge['FacilityID_TankID'] = Pipingmerge['FacilityID_TankID'].str.upper()
# PipingUnique = Pipingmerge.drop_duplicates(subset = 'FacilityID_TankID', keep='first')

# print('merging AllTanks and Contruction file....')
# AllTanks_Piping = pd.merge(AllTanksmerge,PipingUnique, on='FacilityID_TankID',how='left')

# AllTanksmerge['tank construction'] = AllTanks_Contruction['tank construction_y']
# AllTanksmerge['piping construction_refined'] = AllTanks_Piping['piping construction_refined_y']
# del AllTanksmerge['FacilityID_TankID']

# print('merging all thye files....')

# AllTanksmerge.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\Output\FloridaFinal.xlsx', index=False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\L-UST_Data\\LustDataAllStates.xlsx")
FL=LustData[LustData['State Name'] == 'Florida']

print('writing Florida Lower underground storage tank data....')
FL.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\Required\FloridaLustData.xlsx',index = False)

print('Reading FloridaFinal data....')
FLFinal =pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Florida\\Output\\FloridaFinal.xlsx")

print('Reading Florida Lust Data....')
FLLust=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Florida\\Required\\FloridaLustData.xlsx")

FLLust['location_city'] = FLLust['Address'] + '_' + FLLust['City']
FLLust['location_city'] = FLLust['location_city'].str.upper()
FLFinal['location_city'] = FLFinal['Tank Location'] + '_' + FLFinal['City']
FLFinal['location_city'] = FLFinal['location_city'].str.upper()
FLLustUnique = FLLust.drop_duplicates(subset = 'location_city', keep='first')

FLFinalMerged = pd.merge(FLFinal,FLLustUnique, on='location_city',how='left')
FLFinal['lust'] = FLFinalMerged['Address'] + '_' + FLFinalMerged['City_y']
FLFinal['lust status'] = FLFinalMerged['Status']
del FLFinal['location_city']
FLFinal['Year Installed'] = pd.to_datetime(FLFinal['Year Installed'])

FLFinal['State'] = 'Florida'
FLFinal['state_name'] = 'FL'
FLFinal['UST or AST'] = 'UST'
FLFinal['Tank Tightness'] = 'No'
FLFinal['Secondary Containment (AST)'] = 'No'

print('Merging Florida Final and Florida L-UST data')
FLFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\Output\FloridaFinalMerged.xlsx', index=False)

print('Printing values based on the condition satisfied on county column')
FLFinal['county1'] = ''

FLFinal.loc[FLFinal['county'] == 1, 'county1'] = 'ALACHUA'
FLFinal.loc[FLFinal['county'] == 2, 'county'] = 'BAKER'
FLFinal.loc[FLFinal['county'] == 3, 'county1'] = 'BAY'
FLFinal.loc[FLFinal['county'] == 4, 'county1'] = 'BRADFORD'
FLFinal.loc[FLFinal['county'] == 5, 'county1'] = 'BREVARD'
FLFinal.loc[FLFinal['county'] == 6, 'county1'] = 'BROWARD'
FLFinal.loc[FLFinal['county'] == 7, 'county1'] = 'CALHOUN'
FLFinal.loc[FLFinal['county'] == 8, 'county1'] = 'CHARLOTTE'
FLFinal.loc[FLFinal['county'] == 9, 'county1'] = 'CITRUS'
FLFinal.loc[FLFinal['county'] == 10, 'county1'] = 'CLAY'
FLFinal.loc[FLFinal['county'] == 11, 'county1'] = 'COLLIER'
FLFinal.loc[FLFinal['county'] == 12, 'county1'] = 'COLUMBIA'
FLFinal.loc[FLFinal['county'] == 13, 'county1'] = 'MIAMI-DADE'
FLFinal.loc[FLFinal['county'] == 14, 'county1'] = 'DESOTO'
FLFinal.loc[FLFinal['county'] == 15, 'county1'] = 'DIXIE'
FLFinal.loc[FLFinal['county'] == 16, 'county1'] = 'DUVAL'
FLFinal.loc[FLFinal['county'] == 17, 'county1'] = 'ESCAMBIA'
FLFinal.loc[FLFinal['county'] == 18, 'county1'] = 'FLAGLER'
FLFinal.loc[FLFinal['county'] == 19, 'county1'] = 'FRANKLIN'
FLFinal.loc[FLFinal['county'] == 20, 'county1'] = 'GADSDEN'
FLFinal.loc[FLFinal['county'] == 21, 'county1'] = 'GILCHRIST'
FLFinal.loc[FLFinal['county'] == 22, 'county1'] = 'GLADES'
FLFinal.loc[FLFinal['county'] == 23, 'county1'] = 'GULF'
FLFinal.loc[FLFinal['county'] == 24, 'county1'] = 'HAMILTON'
FLFinal.loc[FLFinal['county'] == 25, 'county1'] = 'HARDEE'
FLFinal.loc[FLFinal['county'] == 26, 'county1'] = 'HENDRY'
FLFinal.loc[FLFinal['county'] == 27, 'county1'] = 'HERNANDO'
FLFinal.loc[FLFinal['county'] == 28, 'county1'] = 'HIGHLANDS'
FLFinal.loc[FLFinal['county'] == 29, 'county1'] = 'HILLSBOROUGH'
FLFinal.loc[FLFinal['county'] == 30, 'county1'] = 'HOLMES'
FLFinal.loc[FLFinal['county'] == 31, 'county1'] = 'INDIAN RIVER '
FLFinal.loc[FLFinal['county'] == 32, 'county1'] = 'JACKSON'
FLFinal.loc[FLFinal['county'] == 33, 'county1'] = 'JEFFERSON'
FLFinal.loc[FLFinal['county'] == 34, 'county1'] = 'LAFAYETTE'
FLFinal.loc[FLFinal['county'] == 35, 'county1'] = 'LAKE'
FLFinal.loc[FLFinal['county'] == 36, 'county1'] = 'LEE'
FLFinal.loc[FLFinal['county'] == 37, 'county1'] = 'LEON'
FLFinal.loc[FLFinal['county'] == 38, 'county1'] = 'LEVY'
FLFinal.loc[FLFinal['county'] == 39, 'county1'] = 'LIBERTY'
FLFinal.loc[FLFinal['county'] == 40, 'county1'] = 'MADISON'
FLFinal.loc[FLFinal['county'] == 41, 'county1'] = 'MANATEE'
FLFinal.loc[FLFinal['county'] == 42, 'county1'] = 'MARION'
FLFinal.loc[FLFinal['county'] == 43, 'county1'] = 'MARTIN'
FLFinal.loc[FLFinal['county'] == 44, 'county1'] = 'MONROE'
FLFinal.loc[FLFinal['county'] == 45, 'county1'] = 'NASSAU'
FLFinal.loc[FLFinal['county'] == 46, 'county1'] = 'OKALOOSA'
FLFinal.loc[FLFinal['county'] == 47, 'county1'] = 'OKEECHOBEE'
FLFinal.loc[FLFinal['county'] == 48, 'county1'] = 'ORANGE'
FLFinal.loc[FLFinal['county'] == 49, 'county1'] = 'OSCEOLA'
FLFinal.loc[FLFinal['county'] == 50, 'county1'] = 'PALM BEACH'
FLFinal.loc[FLFinal['county'] == 51, 'county1'] = 'PASCO'
FLFinal.loc[FLFinal['county'] == 52, 'county1'] = 'PINELLAS'
FLFinal.loc[FLFinal['county'] == 53, 'county1'] = 'POLK'
FLFinal.loc[FLFinal['county'] == 54, 'county1'] = 'PUTNAM'
FLFinal.loc[FLFinal['county'] == 55, 'county1'] = 'ST. JOHNS'
FLFinal.loc[FLFinal['county'] == 56, 'county1'] = 'ST. LUCIE'
FLFinal.loc[FLFinal['county'] == 57, 'county1'] = 'SANTA ROSA'
FLFinal.loc[FLFinal['county'] == 58, 'county1'] = 'SARASOTA'
FLFinal.loc[FLFinal['county'] == 59, 'county1'] = 'SEMINOLE'
FLFinal.loc[FLFinal['county'] == 60, 'county1'] = 'SUMTER'
FLFinal.loc[FLFinal['county'] == 61, 'county1'] = 'SUWANNEE'
FLFinal.loc[FLFinal['county'] == 62, 'county1'] = 'TAYLOR'
FLFinal.loc[FLFinal['county'] == 63, 'county1'] = 'UNION'
FLFinal.loc[FLFinal['county'] == 64, 'county1'] = 'VOLUSIA'
FLFinal.loc[FLFinal['county'] == 65, 'county1'] = 'WAKULLA'
FLFinal.loc[FLFinal['county'] == 66, 'county1'] = 'WALTON'
FLFinal.loc[FLFinal['county'] == 67, 'county1'] = 'WASHINGTON'

print('Printing values based on the condition satisfied on tank status column')
FLFinal['tank status1'] = ''

FLFinal.loc[FLFinal['tank status'] == 'A', 'tank status1'] = 'Closed'
FLFinal.loc[FLFinal['tank status'] == 'B', 'tank status1'] = 'Closed'
FLFinal.loc[FLFinal['tank status'] == 'F', 'tank status1'] = 'Open'
FLFinal.loc[FLFinal['tank status'] == 'T', 'tank status1'] = 'Open'
FLFinal.loc[FLFinal['tank status'] == 'U', 'tank status1'] = 'Open'
FLFinal.loc[FLFinal['tank status'] == 'E', 'tank status1'] = 'Open'
FLFinal.loc[FLFinal['tank status'] == 'D', 'tank status1'] = 'Closed'
FLFinal.loc[FLFinal['tank status'] == 'Z', 'tank status1'] = 'Open'
FLFinal.loc[FLFinal['tank status'] == 'V', 'tank status1'] = 'Open'
FLFinal.loc[FLFinal['tank status'] == 'M', 'tank status1'] = 'Closed'
FLFinal.loc[FLFinal['tank status'] == 'X', 'tank status1'] = 'Open'

print('replacing the original columns with the modified columns')
FLFinal['county'] = FLFinal['county1']
FLFinal['tank status'] = FLFinal['tank status1']
del FLFinal['county1']
del FLFinal['tank status1']
FLFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\Output\Florida_FL_FinalMerged.xlsx', index=False)

print('Completed....')