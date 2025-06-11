from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
import time
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains
import xlwt
from xlwt import Workbook
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from csv import writer 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException


wb = Workbook()
sheet1 = wb.add_sheet('Sheet 1',cell_overwrite_ok=True)

chromedriver='C:\\Users\\Administrator\\Desktop\\axon_states\\Drivers\\chromedriver_win32 (4)\\chromedriver.exe'
driver = webdriver.Chrome(chromedriver)
df=pd.read_csv(r"C:\Users\Administrator\Desktop\facility_export1.csv")
# fac=pd.read_csv(r"C:\Users\VA_User\Desktop\Mass\facility_export (2).csv")
m=0
p=0

for i in df["URL"]:
    k=0
    
    # print(fac["UST Facility ID"][p])
    # sheet1.write(m, n, str(fac["UST Facility ID"][p]))
    
    p+=1
    time.sleep(3)
    j=1
    driver.get(i)
    buttons_length=driver.find_elements_by_css_selector(".fa.fa-th-list")
    buttons_length=len(buttons_length)
    print("butlength",buttons_length)
  
    

    while True:
        n=0

        try:
            
            #driver.implicitly_wait(10)
            time.sleep(5)
            
            
            
    
            button=driver.find_element_by_name("table:body:rows:"+str(j)+":cells:9:cell:form:buttons:0:button")
            facility_id=driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div[1]/div/div/div/div/div[1]/div[2]/span")
            print(facility_id.text)
            sheet1.write(m, n, facility_id.text)
            n+=1
            address=driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div/div[2]/div/div/div[1]/div[1]/div[2]/span/p")
            print(address.text)
            sheet1.write(m, n, address.text)
            n+=1
            facility_name=driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div[1]/div/div/div/div/div[1]/div[2]/h1")
            print(facility_name.text)
            sheet1.write(m, n, facility_name.text)
            n+=1
            ActionChains(driver).move_to_element(button).click(button).perform()
            driver.implicitly_wait(5)
            time.sleep(5)
            k+=1
            # print(k)
            j+=1 
            j+=buttons_length
            
            
            
            
           
            details=driver.find_element_by_xpath("/html/body/div[3]/div/div[2]/div/div[2]/div[1]/div/div[2]/div/div[1]/div/dl/dd[1]")
            print(details.text)
            sheet1.write(m, n, details.text)
            n+=1
            tank_id=driver.find_element_by_xpath("/html/body/div[3]/div/div[2]/div/div[2]/div[1]/div/div[1]/h3")
            print(tank_id.text)
            sheet1.write(m, n, tank_id.text)
            n+=1
            install_date=driver.find_element_by_xpath("/html/body/div[3]/div/div[2]/div/div[2]/div[1]/div/div[2]/div/div[2]/div/dl/dd[1]")
            print(install_date.text)
            sheet1.write(m, n, install_date.text)
            n+=1
            capacity=driver.find_element_by_xpath("/html/body/div[3]/div/div[2]/div/div[2]/div[1]/div/div[2]/div/div[2]/div/dl/dd[3]")
            print(capacity.text) 
            sheet1.write(m, n, capacity.text)
            n+=1
            contents=driver.find_element_by_xpath("/html/body/div[3]/div/div[2]/div/div[2]/div[2]/div/div[2]/div/div/form/div[2]/div/div[1]/table/tbody/tr/td[2]/div")
            print(contents.text)
            sheet1.write(m, n, contents.text)
            n+=1
            Piping_construction=driver.find_element_by_xpath("/html/body/div[3]/div/div[2]/div/div[2]/div[3]/div/div[2]/div[3]/div[2]/span")
            print(Piping_construction.text)
            sheet1.write(m, n, Piping_construction.text)
            n+=1
            Tank_construction=driver.find_element_by_xpath("/html/body/div[3]/div/div[2]/div/div[2]/div[1]/div/div[2]/div/div[2]/div/dl/dd[2]")
            print(Tank_construction.text)
            sheet1.write(m, n, Tank_construction.text)
            n+=1
            wb.save("C:\\Users\\Administrator\\Desktop\\Hey.xls")
        # details=driver.find_elements_by_css_selector(".col-xs-12.col-md-6")
            # tank=driver.find_elements_by_css_selector(".panel-title.clearfix")
            # contents=driver.find_element_by_css_selector(".table-condensed.table.table-hover")
            
            # n=1
            # m+=1
            # for detail in details:
                
            #     sheet1.write(m, n, detail.text)
            #     print(detail.text)
            #     n+=1
            #     if "Is the tank equipped with a submersible pump?" in detail.text:
            #         break
            #     time.sleep(2)
            # for tanks in tank:
            #     sheet1.write(m, n, tanks.text)
            #     n+=1
            #     if "Tank" in tanks.text:
            #         # print(tanks.text
            #         print(tanks.text)
                    
                    
            #         break
            # print(contents.text)
            # sheet1.write(m, n, contents.text)
            # n+=1
            
            # wb.save("Text0.xls")
            
            
            
            
            p_buttons=driver.find_elements_by_css_selector(".btn.btn-default")
            m+=1
            
            for p_button in p_buttons:
            
                if " Back to Facility" in p_button.text:
                    
                    
                    ActionChains(driver).move_to_element(p_button).double_click(p_button).perform()
                
               
        except:
            
            
            break
