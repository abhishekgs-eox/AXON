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
browser.get('https://www.dec.ny.gov/cfmx/extapps/derexternal/index.cfm?pageid=4')
print("sript started")
def fetch_tank():    
    tank_id=browser.find_element_by_xpath("//*[@id='				tank_1']/input[11]")
    tank_id.click()
    for tank in range(1,notanks,1):
        print(tank)
        site_id=site_name=""
        site_id = browser.find_element_by_xpath('//*[@id="content"]/div[1]').text
        site_id = site_id.split("Site No:",1)[1]
        print(site_id)
    
        site_name = browser.find_element_by_xpath("//*[@id='content']/div[2]").text
        site_name = site_name.split("Site Name:",1)[1]
        print(site_name)

        tank_id = browser.find_element_by_xpath("//*[@id='content']/div[3]").text
        tank_id = tank_id.split("Tank No:",1)[1]
        
        tank_loc = browser.find_element_by_xpath("//strong[contains(text(),'Tank Location')]/parent::div").text
        tank_loc = browser.find_element_by_xpath("//*[@id='content']/div[4]").text
        # tank_loc = tank_loc.split("Tank Location:",1)[1]

        tank_status = browser.find_element_by_xpath("//strong[contains(text(),'Tank Status')]/parent::div").text
        tank_status = browser.find_element_by_xpath("//*[@id='content']/div[7]").text
        # tank_status = tank_status.split("Tank Status:",1)[1]

        instal_date = browser.find_element_by_xpath("//strong[contains(text(),'Tank Install Date')]/parent::div").text
        instal_date = browser.find_element_by_xpath("//*[@id='content']/div[8]").text
        # instal_date = instal_date.split("Tank Install Date:",1)[1]

        capacity = browser.find_element_by_xpath("//strong[contains(text(),'Tank Capacity')]/parent::div").text
        capacity = browser.find_element_by_xpath("//*[@id='content']/div[11]").text
        # capacity = capacity.split("Tank Capacity:",1)[1]

        T_type = browser.find_element_by_xpath("//strong[contains(text(),'Tank Type')]/parent::div").text
        T_type = browser.find_element_by_xpath("//*[@id='content']/div[14]").text
        # T_type = T_type.split("Tank Type:",1)[1]

        T_secondry = browser.find_element_by_xpath("//strong[contains(text(),'Tank Secondary Containment')]/parent::div").text
        T_secondry = browser.find_element_by_xpath("//*[@id='content']/div[17]").text
        # T_secondry = T_secondry.split("Tank Secondary Containment:",1)[1]
        
        P_type = browser.find_element_by_xpath("//strong[contains(text(),'Pipe Type')]/parent::div").text
        print(P_type)
        P_type = P_type.split("Pipe Type:",1)[1]
        try:
            substance = browser.find_element_by_xpath("//strong[contains(text(),'Product Stored')]/parent::div").text
            print(P_type)
            substance = substance.split("Product Stored:",1)[1]
        except:
            substance=""
        new_row=[]
        new_row.extend((site_id,site_name,tank_id,tank_loc,tank_status,instal_date,capacity,T_type,T_secondry,P_type,substance))
        print(new_row)
        with open(r'C:\Users\Administrator\Desktop\NW_tank_11032022PBS.csv', 'a+', newline='') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(new_row)  
            f_object.close()
        nexttank = browser.find_element_by_xpath("//*[@value='Next Tank' and @name='submit']")
        nexttank.click()
    browser.close()

# browser.find_element_by_xpath("//*[@id='ExpirationDate']").send_keys("12/06/2021")
print("Hi")
time.sleep(5)
browser.find_element_by_xpath("/html/body/div/div[3]/div/form[2]/div[3]/strong/select/option[4]").click()
browser.find_element_by_name('Submit').click()
# print('Submit button clicked')
# fac_id= browser.find_element_by_name('submit')
# nextpage = browser.find_element_by_xpath("//*[@value='Last 50' and @name='Navigate' and @type='submit']")
# nextpage.click()
while True:
    if (browser.find_element_by_xpath("//*[@value='Next 50' and @name='Navigate' and @type='submit']").is_enabled()==False):
        break
    for i in range(1,50,1):
        browser.switch_to_window(browser.window_handles[0])
        fac_ids = browser.find_element_by_xpath("//*[@id='content']/table/tbody/tr["+str(i+1)+"]/td[1]/form/input[8]")
        ActionChains(browser) \
            .key_down(Keys.CONTROL) \
            .click(fac_ids) \
            .key_up(Keys.CONTROL) \
            .perform()
        browser.switch_to.window(browser.window_handles[1])
        notanks = browser.find_elements_by_name("submit2")
        notanks= len(notanks)
        if (notanks>0):
            fetch_tank()
        else:
            browser.close()
    browser.switch_to_window(browser.window_handles[0])
    nextpage = browser.find_element_by_xpath("//*[@value='Next 50' and @name='Navigate' and @type='submit']").is_enabled()
    nextpage = browser.find_element_by_xpath("//*[@value='Next 50' and @name='Navigate' and @type='submit']")
    nextpage.click()    
browser.close()
browser.quit()