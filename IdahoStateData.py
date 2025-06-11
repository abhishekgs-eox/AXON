import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Chrome
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from csv import writer 
import time
import pandas as pd
import os

options = webdriver.ChromeOptions()
options.headless = False
#assert opts.headless  # Operating in headless mode
browser = Chrome(r'C:\Users\Administrator\Desktop\axon_states\Drivers\chromedriver_win32\chromedriver.exe',options=options)
browser.get('https://www2.deq.idaho.gov/waste/ustlust/pages/Search.aspx')
print("sript started")
count=0
browser.find_element_by_xpath("//*[@id='phContent_btnSearchFacility']").click()
time.sleep(10)
for k in range(1,1000000,1):
    browser.switch_to_window(browser.window_handles[0])
    if count==10:
        try:
            browser.find_element_by_xpath("//*[@id='phContent_gvFacility']/tbody/tr[14]/td/table/tbody/tr/td[12]").click()
            count=0
        
        except:
            browser.find_element_by_xpath("//*[@id='phContent_gvFacility']/tbody/tr[14]/td/table/tbody/tr/td[11]").click()
            count=0    
    else:
        browser.find_element_by_xpath("//*[text()="+str(k)+"]").click()
    count=count+1
    for i in range(1,13,1):
        browser.switch_to_window(browser.window_handles[0])
        fac_id = browser.find_element_by_xpath("//*[@id='phContent_gvFacility']/tbody/tr["+str(i+1)+"]/td[1]/a")
        ActionChains(browser) \
                .key_down(Keys.CONTROL) \
                .click(fac_id) \
                .key_up(Keys.CONTROL) \
                .perform()
        time.sleep(2)
        browser.switch_to_window(browser.window_handles[1])
        browser.find_element_by_xpath("//*[@id='phContent_chkInactivePipe']").click()
        time.sleep(5)
        nnotank= browser.find_elements_by_xpath("//*[@id='phContent_gvTank']/tbody/tr")
        print(len(nnotank))
        nnotank= len(nnotank)
        for j in range(2,nnotank+1,1):
            fac_id=browser.find_element_by_xpath("//*[@id='phContent_editFacility_txtFacilityID']")
            fac_id=fac_id.get_attribute("value")
            fac_name=browser.find_element_by_xpath("//*[@id='phContent_editFacility_txtFacilityName']")
            fac_name=fac_name.get_attribute("value")
            address1=browser.find_element_by_xpath("//*[@id='phContent_editFacility_txtAddress1']")
            address1=address1.get_attribute("value")
            address2=browser.find_element_by_xpath("//*[@id='phContent_editFacility_txtAddress2']")
            address2=address2.get_attribute("value")
            #city=browser.find_element_by_xpath("//*[@id='phContent_editFacility_ddlCity']").first_selected_option.ext
            fac_status=browser.find_element_by_xpath("//*[@id='phContent_editFacility_lblStatus']").text
            tank_id=browser.find_element_by_xpath("//*[@id='phContent_gvTank']/tbody/tr["+str(j)+"]/td[1]").text
            try:
                pipe_id=browser.find_element_by_xpath("//*[@id='phContent_gvPipe']/tbody/tr["+str(j)+"]/td[1]").text
                pipe_material=browser.find_element_by_xpath("//*[@id='phContent_gvPipe']/tbody/tr["+str(j)+"]/td[4]").text
            except:
                print("no pipe found")
                pipe_id=""
                pipe_material=""
            Capacity=browser.find_element_by_xpath("//*[@id='phContent_gvTank']/tbody/tr["+str(j)+"]/td[2]").text
            tank_status=browser.find_element_by_xpath("//*[@id='phContent_gvTank']/tbody/tr["+str(j)+"]/td[3]").text
            substance=browser.find_element_by_xpath("//*[@id='phContent_gvTank']/tbody/tr["+str(j)+"]/td[4]").text
            tank_material=browser.find_element_by_xpath("//*[@id='phContent_gvTank']/tbody/tr["+str(j)+"]/td[5]").text
            installed=browser.find_element_by_xpath("//*[@id='phContent_gvTank']/tbody/tr["+str(j)+"]/td[6]").text
            
            
            
            new_row=[]
            new_row.extend((fac_id,fac_name, address1,address2,fac_status,tank_id,pipe_id,Capacity,tank_status,substance,tank_material,pipe_material,installed))
            print(new_row)
            with open(r'C:\Users\Administrator\Desktop\axon_states\states\Idaho\Input\ID_state_tank.csv', 'a+', newline='') as f_object:
                writer_object = writer(f_object)
                writer_object.writerow(new_row) 
                f_object.close()
        browser.close()
        
URL="https://www2.deq.idaho.gov/waste/ustlust/pages/Search.aspx"

chromeOptions = Options()
chromeOptions.add_experimental_option("prefs",{"download.default_directory" : "C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Idaho\\Input"})
browser =  webdriver.Chrome(r'C:\Users\Administrator\Desktop\axon_states\Drivers\chromedriver_win32 (4)\chromedriver.exe',options=chromeOptions)
browser.maximize_window()
browser.get(URL)
browser.implicitly_wait(5)

WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH,'/html/body/div/div[3]/ul/li[6]/a')))
browser.find_element(By.XPATH,'/html/body/div/div[3]/ul/li[6]/a').click()

WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH,'/html/body/div/div[4]/div/form/table/tbody/tr[4]/td/a[3]')))
browser.find_element(By.XPATH,'/html/body/div/div[4]/div/form/table/tbody/tr[4]/td/a[3]').click()

while len(os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Idaho\Input')) < 2:
    time.sleep(0.2)
    print('waiting to download...')

print('Downloading the files started....')
def Check_File_Status():
    filesExtensions = []
    filesList = []
    for file in os.listdir(r'C:\Users\Administrator\Desktop\axon_states\states\Idaho\Input'):
        filesList.append(file)
        filesExtensions = [x.split('.')[-1] for x in filesList]
        print(filesExtensions)
    if 'crdownload' in filesExtensions or 'tmp' in filesExtensions:
        time.sleep(3)
        Check_File_Status()
    else:
        pass

Check_File_Status()

#browser.quit()

print('....Downloaded....')
        
dfIDmap = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Idaho\\Required\\IdahoMapping.xlsx")
print('Reading the Idaho Mapping file....')
dfIDmap = dfIDmap[:0]

IDcsv = pd.read_csv("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Idaho\Input\\ID_state_tank.csv", header = None, encoding='unicode_escape')        
IDcsv.columns = ["Facility ID","Facility Name","Address","Address1","Status","ID","Tank ID","Capacity","Tank Status","Substance","Tank Material","Pipe Material","Date Installed"]

IDcsv.to_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Idaho\\Output\\IdahoFile.xlsx", index=False)

print('Reading the Idaho State file....')
dfWI = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Idaho\\Output\\IdahoFile.xlsx")
\
IDmap = dfWI[['Facility ID','Tank ID','Address','Date Installed','Capacity','Tank Material','Pipe Material','Substance','Facility Name','Tank Status']]
IDmap.columns = ['Facility Id','Tank ID','Tank Location','Year Installed','Tank Size','tank construction','piping construction_refined','content description','Facility Name','tank status']

print('Merging the UST_List file with Idaho Mapping file and writing to excel')
IDmerge = pd.concat([dfIDmap,IDmap])
IDmerge.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Idaho\Output\IdahoMerged.xlsx', index = False)

IDfile = pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Idaho\Output\IdahoMerged.xlsx')

CityZip = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Idaho\\Input\\Waste_and_Remediation_UST_LUST_Reports_UST_List.xls")
# Assign row as column headers
CityZip.columns = CityZip.iloc[6]
# delete a multiple row by index value
CityZip = CityZip[7:]

CZmap = CityZip[['Facility ID','City','Zip']]
CZmap.columns = ['Facility Id','City','Zipcode']

CZfile = pd.concat([dfIDmap,CZmap])
CZfile.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Idaho\Output\IdahoCityZip.xlsx', index=False)

CZdata = pd.read_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Idaho\Output\IdahoCityZip.xlsx')

print('merging city and zip columns with final file based on facility id')
IDstate = CZdata.drop_duplicates(subset = 'Facility Id',keep='first')
IDstatefile = pd.merge(IDfile,IDstate, on='Facility Id',how='left')
IDstatefile['City_x'] = IDstatefile['City_y']
IDstatefile['Zipcode_x'] = IDstatefile['Zipcode_y']

IDmapfile = IDstatefile[['Facility Id','Tank ID_x','Tank Location_x','City_x','Zipcode_x','Year Installed_x','Tank Size_x','tank construction_x','piping construction_refined_x','content description_x','Facility Name_x','tank status_x']]
IDmapfile.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','Year Installed','Tank Size','tank construction','piping construction_refined','content description','Facility Name','tank status']

print('writing final idaho data...')
IDfull = pd.concat([dfIDmap,IDmapfile])
IDfull['State'] = 'Idaho'
IDfull['state_name'] = 'ID'
IDfull['UST or AST'] = 'UST'
IDfull.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Idaho\Output\IdahoFinal.xlsx', index=False)

print('Reading Lower underground storage tank data of All States....')
LustData=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\L-UST_Data\\LustDataAllStates.xlsx")
ID=LustData[LustData['State Name'] == 'Idaho']

print('writing Idaho Lower underground storage tank data....')
ID.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Idaho\Required\IdahoLustData.xlsx',index = False)

print('Reading IdahoFinal data....')
IDFinal =pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Idaho\\Output\\IdahoFinal.xlsx")

print('Reading Idaho Lust Data....')
IDLust=pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Idaho\\Required\\IdahoLustData.xlsx")

IDLust['location_city'] = IDLust['Address'] + '_' + IDLust['City']
IDLust['location_city'] = IDLust['location_city'].str.upper()
IDFinal['location_city'] = IDFinal['Tank Location'] + '_' + IDFinal['City']
IDFinal['location_city'] = IDFinal['location_city'].str.upper()
IDLustUnique = IDLust.drop_duplicates(subset = 'location_city', keep='first')

IDFinalMerged = pd.merge(IDFinal,IDLustUnique, on='location_city',how='left')
IDFinal['lust'] = IDFinalMerged['Address'] + '_' + IDFinalMerged['City_y']
IDFinal['lust status'] = IDFinalMerged['Status']
del IDFinal['location_city']

print('Merging Idaho Final and Idaho L-UST data')
IDFinal.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Idaho\Output\IdahoFinalMerged.xlsx', index=False)

print('Completed....')

