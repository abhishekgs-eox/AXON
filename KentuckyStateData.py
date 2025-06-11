from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from zipfile import ZipFile
import time
import pandas as pd
import os

# # Chrome Driver path
# PATH = "C:\\Users\\Administrator\\Desktop\\axon_states\\Drivers\\New folder\\chromedriver_win32\\chromedriver.exe"
# #Kentucky Website URL
# URL = "https://eec.ky.gov/Environmental-Protection/Waste/underground-storage-tank/Pages/Resources.aspx"

# chromeOptions = Options()
# chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Kentucky\\Input"})
# driver =  webdriver.Chrome(PATH,options=chromeOptions)
# driver.maximize_window()
# driver.get(URL)
# driver.implicitly_wait(5)

# WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="ctl00_ctl00_m_g_f5b6befa_14e5_4713_85de_b3857d052c2a_ctl02_gvwData_ctl11_btnDownload"]')))
# driver.find_element(By.XPATH,'//*[@id="ctl00_ctl00_m_g_f5b6befa_14e5_4713_85de_b3857d052c2a_ctl02_gvwData_ctl11_btnDownload"]').click()
# # //*[@id="ctl00_ctl00_m_g_f5b6befa_14e5_4713_85de_b3857d052c2a_ctl02_gvwData_ctl11_btnDownload"]
# # //*[@id="ctl00_ctl00_m_g_f5b6befa_14e5_4713_85de_b3857d052c2a_ctl02_gvwData_ctl12_btnDownload

# while len(os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Kentucky\Input')) < 1:
#     time.sleep(0.2)
#     print('waiting to download...')

# print('-------Downloading the files -------')
# def Check_File_Status():
#     filesExtensions = []
#     filesList = []
#     for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Kentucky\Input'):
#         filesList.append(file)
#         filesExtensions = [x.split('.')[-1] for x in filesList]
#         print(filesExtensions)
#     if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
#         time.sleep(3)
#         Check_File_Status()
#     else:
#         pass

# Check_File_Status()

# print('-------Downloading the files is done-------')

# for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Kentucky\Input'):
#     DownloadedFile = file

# # print('Unzipping the file....')

# # zfile = r'C:\Users\Administrator\Desktop\axon_states\states\Kentucky\Input\\'+str(DownloadedFile)
# # with ZipFile(zfile) as zipObj:
# #     zipObj.printdir()
# #     zipObj.extractall(path="C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Kentucky\\Input")    

print('Reading Kentucky Mapping file....')
dfKmap = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Kentucky\\Required\\KentuckyMapping.xlsx")
#getting the headers
dfKmap = dfKmap[:0]

# Statewide UST Database Report
print('Reading Statewide UST Database Report file....')
dfsudr = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Kentucky\\Input\\Statewide UST Database Report.xls")
# delete last row
dfsudr.drop(index = dfsudr.index[-1], axis=0, inplace=True)

dfsudr['SITE_SEQ_ID'] = dfsudr['SITE_SEQ_ID'].fillna(1010101010)
dfsudr['SITE_SEQ_ID'] = dfsudr['SITE_SEQ_ID'].astype(int)
dfsudr['AI_ID'] = dfsudr['AI_ID'].astype(int)
dfsudr['SITE_SEQ_ID'] = dfsudr['SITE_SEQ_ID'].astype(str)
dfsudr['AI_ID'] = dfsudr['AI_ID'].astype(str)
dfsudr['facilityID'] = dfsudr['SITE_SEQ_ID'] + ' ' + dfsudr['AI_ID']
dfsudr['facilityID'] = dfsudr['facilityID'].str.replace('1010101010','')
dfsudr['facilityID'] = dfsudr['facilityID'].str.strip()
# columns replace
sudrMap = dfsudr[['AI_ID','SITE_SEQ_ID','ADDRESS_1','MAILING_ADDRESS_MUNICIPALITY','MAILING_ADDRESS_ZIP','TANK_INSTALL_DATE','CAPACITY_MSR','TANK_MATERIAL_CODE','PIPE_MATERIAL_CODE','TANK_SUBSTANCE_CODE','AI_NAME','COUNTY','TANK_STATUS_CODE']]
sudrMap.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','Year Installed','Tank Size','tank construction','piping construction_refined','content description','Facility Name','county','tank status']

print('Merging the Statewide UST Database Report file with Kentucky Mapping file and writing to excel')
#Concatinate the Dataframes
sudr = pd.concat([dfKmap,sudrMap])
sudr['State'] = 'Kentucky'
sudr['state_name'] = 'KY'
sudr['UST or AST'] = 'UST'
sudr['Secondary Containment (AST)'] = 'No'
sudr['Tank Tightness'] = 'No'
sudr.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Kentucky\Output\KentuckyFinal.xlsx', index = False)

print('Reading Lower underground storage tank data....')
LustData=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\L-UST_Data\\LustDataAllStates.xlsx")
KY=LustData[LustData['State Name'] == 'Kentucky']

print('writing Kentucky Lower underground storage tank data....')
KY.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Kentucky\Required\KentuckyLustData.xlsx',index = False)

print('Reading KentuckyFinal data....')
KYFinal =pd.read_excel( r'C:\Users\Administrator\Desktop\axon_states\states\Kentucky\Output\KentuckyFinal.xlsx')

print('Reading Kentucky Lust Data....')
KYLust=pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Kentucky\Required\KentuckyLustData.xlsx')

KYLust['location_city'] = KYLust['Address'] + '_' + KYLust['City']
KYLust['location_city'] = KYLust['location_city'].str.upper()
KYFinal['location_city'] = KYFinal['Tank Location'] + '_' + KYFinal['City']
KYFinal['location_city'] = KYFinal['location_city'].str.upper()
KYLustUnique = KYLust.drop_duplicates(subset = 'location_city', keep='first')

KYFinalMerged = pd.merge(KYFinal,KYLustUnique, on='location_city',how='left')
KYFinal['lust'] = KYFinalMerged['Address'] + '_' + KYFinalMerged['City_y']
KYFinal['lust status'] = KYFinalMerged['Status']
del KYFinal['location_city']

KYFinal['tank status1'] = ''
#triggering the conditions
KYFinal.loc[KYFinal['tank status'] == 'DUP', 'tank status1'] = 'Duplicate Tank To Another Site'
KYFinal.loc[KYFinal['tank status'] == 'T96', 'tank status1'] = 'Removed Tank 1996 Regs'
KYFinal.loc[KYFinal['tank status'] == 'TAB', 'tank status1'] = 'Tank Abandoned'
KYFinal.loc[KYFinal['tank status'] == 'TAC', 'tank status1'] = 'Active'
KYFinal.loc[KYFinal['tank status'] == 'TBL', 'tank status1'] = 'Removed Tank Backlog Regs'
KYFinal.loc[KYFinal['tank status'] == 'TCP', 'tank status1'] = 'Closed in Place'
KYFinal.loc[KYFinal['tank status'] == 'TCS', 'tank status1'] = 'Change in Service'
KYFinal.loc[KYFinal['tank status'] == 'TER', 'tank status1'] = 'Removed Tank Ereg'
KYFinal.loc[KYFinal['tank status'] == 'TEX', 'tank status1'] = 'Exempt'
KYFinal.loc[KYFinal['tank status'] == 'TNF', 'tank status1'] = 'Not Found'
KYFinal.loc[KYFinal['tank status'] == 'TR8', 'tank status1'] = 'Removed Prior to 1988'
KYFinal.loc[KYFinal['tank status'] == 'TRM', 'tank status1'] = 'Removed Tank Verified'
KYFinal.loc[KYFinal['tank status'] == 'TRR', 'tank status1'] = 'Tank Removed and Replaced'
KYFinal.loc[KYFinal['tank status'] == 'TTC', 'tank status1'] = 'Temporarily Closed'
KYFinal.loc[KYFinal['tank status'] == 'TUR', 'tank status1'] = 'Removed Tank Unverified'

KYFinal['tank construction1'] = ''
KYFinal.loc[KYFinal['tank construction'] == 'ALU', 'tank construction1'] = 'Aluminium'
KYFinal.loc[KYFinal['tank construction'] == 'CCR', 'tank construction1'] = 'Concrete'
KYFinal.loc[KYFinal['tank construction'] == 'DST', 'tank construction1'] = 'Doubled Wall Steel'
KYFinal.loc[KYFinal['tank construction'] == 'DWF', 'tank construction1'] = 'Double Wall Fiberglass'
KYFinal.loc[KYFinal['tank construction'] == 'DWM', 'tank construction1'] = 'Double Wall Mix'
KYFinal.loc[KYFinal['tank construction'] == 'FRP', 'tank construction1'] = 'Fiberglass Reinforced'
KYFinal.loc[KYFinal['tank construction'] == 'OTH', 'tank construction1'] = 'Other'
KYFinal.loc[KYFinal['tank construction'] == 'SST', 'tank construction1'] = 'Single Wall Steel'
KYFinal.loc[KYFinal['tank construction'] == 'SWM', 'tank construction1'] = 'Steel Mix'
KYFinal.loc[KYFinal['tank construction'] == 'UNK', 'tank construction1'] = 'Unknown'

KYFinal['piping construction_refined1'] = ''
KYFinal.loc[KYFinal['piping construction_refined'] == 'ALU', 'piping construction_refined1'] = 'Aluminium'
KYFinal.loc[KYFinal['piping construction_refined'] == 'DFX', 'piping construction_refined1'] = 'Double Wall Flexible'
KYFinal.loc[KYFinal['piping construction_refined'] == 'DST', 'piping construction_refined1'] = 'Double Walled Steel'
KYFinal.loc[KYFinal['piping construction_refined'] == 'DWF', 'piping construction_refined1'] = 'Double Wall Fiberglass'
KYFinal.loc[KYFinal['piping construction_refined'] == 'FLX', 'piping construction_refined1'] = 'Flexible Wall'
KYFinal.loc[KYFinal['piping construction_refined'] == 'FRP', 'piping construction_refined1'] = 'Fiberglass Reinforced Plastic'
KYFinal.loc[KYFinal['piping construction_refined'] == 'GST', 'piping construction_refined1'] = 'Galvanized Steel'
KYFinal.loc[KYFinal['piping construction_refined'] == 'OTM', 'piping construction_refined1'] = 'Other Material'
KYFinal.loc[KYFinal['piping construction_refined'] == 'SIF', 'piping construction_refined1'] = 'Steel Interior/Fiberglass Lined'
KYFinal.loc[KYFinal['piping construction_refined'] == 'SST', 'piping construction_refined1'] = 'Single Wall Steel'
KYFinal.loc[KYFinal['piping construction_refined'] == 'UNK', 'piping construction_refined1'] = 'Unknown'

KYFinal['content description1'] = ''
KYFinal.loc[KYFinal['content description'] == 'AVG', 'content description1'] = 'Aviation fuel'
KYFinal.loc[KYFinal['content description'] == 'BIO', 'content description1'] = 'Bio-Diesel'
KYFinal.loc[KYFinal['content description'] == 'DEF', 'content description1'] = 'Diesel Exhaust Fluid'
KYFinal.loc[KYFinal['content description'] == 'DSL', 'content description1'] = 'Diesel'
KYFinal.loc[KYFinal['content description'] == 'EMP', 'content description1'] = 'Empty'
KYFinal.loc[KYFinal['content description'] == 'ETH', 'content description1'] = 'Ethanol'
KYFinal.loc[KYFinal['content description'] == 'FOL', 'content description1'] = 'Fuel Oil'
KYFinal.loc[KYFinal['content description'] == 'GAS', 'content description1'] = 'Gasoline'
KYFinal.loc[KYFinal['content description'] == 'HAZ', 'content description1'] = 'Cercla Hazardous Substance'
KYFinal.loc[KYFinal['content description'] == 'JET', 'content description1'] = 'Jet Fuel'
KYFinal.loc[KYFinal['content description'] == 'KER', 'content description1'] = 'Kerosene'
KYFinal.loc[KYFinal['content description'] == 'NOL', 'content description1'] = 'New Oil'
KYFinal.loc[KYFinal['content description'] == 'OIL', 'content description1'] = 'Oil'
KYFinal.loc[KYFinal['content description'] == 'ORD', 'content description1'] = 'DSL Off Road'
KYFinal.loc[KYFinal['content description'] == 'OTH', 'content description1'] = 'Other Substance'
KYFinal.loc[KYFinal['content description'] == 'PLS', 'content description1'] = 'GAS-Plus UnI Gas'
KYFinal.loc[KYFinal['content description'] == 'PRM', 'content description1'] = 'GAS-Prem UnI Gas'
KYFinal.loc[KYFinal['content description'] == 'REG', 'content description1'] = 'GAS-UNL-Reg UnI Gas'
KYFinal.loc[KYFinal['content description'] == 'UNK', 'content description1'] = 'Unknown Substance'
KYFinal.loc[KYFinal['content description'] == 'UOL', 'content description1'] = 'Used Oil'

KYFinal['tank status'] = KYFinal['tank status1']
del KYFinal['tank status1']

KYFinal['tank construction'] = KYFinal['tank construction1']
del KYFinal['tank construction1']

KYFinal['piping construction_refined'] = KYFinal['piping construction_refined1']
del KYFinal['piping construction_refined1']

KYFinal['content description'] = KYFinal['content description1']
del KYFinal['content description1']

print('Merging KentuckyFinal and Kentucky L-UST data')
KYFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Kentucky\Output\KentuckyFinalMerged.xlsx', index=False)

print('Completed....')






















   
   
   

