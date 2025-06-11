import selenium
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from csv import writer 
import time
options = webdriver.ChromeOptions()
options.headless = False
#assert opts.headless  # Operating in headless mode
browser = Chrome(r'C:\Users\Administrator\Desktop\axon_states\Drivers\chromedriver_win32 (4)\chromedriver.exe',options=options)
browser.get('https://apps.dhec.sc.gov/Environment/USTRegistry')
print("sript started")
for k in range(2,50,1):
    browser.switch_to.window(browser.window_handles[0])
    browser.find_element_by_xpath("//*[@id='County']/option["+str(k)+"]").click()
    #browser.find_element_by_name('Submit').click()
    submit = browser.find_element_by_xpath("/html/body/div/section/form/p/input")
    ActionChains(browser) \
            .key_down(Keys.CONTROL) \
            .click(submit) \
            .key_up(Keys.CONTROL) \
            .perform()
    #browser.find_element_by_name('Submit').click()
    browser.switch_to.window(browser.window_handles[1])
    numberofrows = browser.find_elements_by_xpath("/html/body/div/section/table/tbody/tr")
    print(len(numberofrows))
    numberofrows = len(numberofrows)
    for j in range(1,numberofrows,1):
        time.sleep(5)
        browser.switch_to.window(browser.window_handles[1])
        fac_id = browser.find_element_by_xpath("/html/body/div/section/table/tbody/tr["+str(j+1)+"]/td[5]").text
        address = browser.find_element_by_xpath("/html/body/div/section/table/tbody/tr["+str(j+1)+"]/td[2]").text
        fac_name= browser.find_element_by_xpath("/html/body/div/section/table/tbody/tr["+str(j+1)+"]/td[1]").text
        city = browser.find_element_by_xpath("/html/body/div/section/table/tbody/tr["+str(j+1)+"]/td[3]").text 

        details = browser.find_element_by_xpath("/html/body/div/section/table/tbody/tr["+str(j+1)+"]/td[7]/a")
        ActionChains(browser) \
            .key_down(Keys.CONTROL) \
            .click(details) \
            .key_up(Keys.CONTROL) \
            .perform()
        browser.switch_to.window(browser.window_handles[2])
        browser.find_element_by_id("toggle-tanks").click()
        time.sleep(5)
        numberoftanks = browser.find_element_by_xpath("//*[@id='details']/div[32]").text
        numberoftanks = int(numberoftanks)
        print("number of tanks " +str(numberoftanks))
        for i in range(1,numberoftanks+1,1):
            if numberoftanks==0:
                break
                browser.close()
            else:
                tank_id = browser.find_element_by_xpath("//*[@id='tanks']/div["+str(i)+"]/div/div[2]").text
                installation_date = browser.find_element_by_xpath("//*[@id='tanks']/div["+str(i)+"]/div/div[5]").text
                tank_construction = browser.find_element_by_xpath("//*[@id='tanks']/div["+str(i)+"]/div/div[9]").text
                pipe_type = browser.find_element_by_xpath("//*[@id='tanks']/div["+str(i)+"]/div/div[11]").text
                tank_status = browser.find_element_by_xpath("//*[@id='tanks']/div["+str(i)+"]/div/div[15]").text
                substance = browser.find_element_by_xpath("//*[@id='tanks']/div["+str(i)+"]/div/div[36]").text
                capacity = browser.find_element_by_xpath("//*[@id='tanks']/div["+str(i)+"]/div/div[28]").text
                new_row=[]
                new_row.extend((fac_id,fac_name,address,city,tank_id,installation_date,tank_construction,pipe_type,tank_status,substance,capacity))
                print(new_row)
                with open(r'C:\Users\Administrator\Desktop\SC_NEW.csv', 'a+', newline='') as f_object:
                    writer_object = writer(f_object)
                    writer_object.writerow(new_row)  
                    f_object.close()
                
        browser.close()
    browser.close()
browser.quit()