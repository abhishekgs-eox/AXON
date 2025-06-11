import selenium
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from csv import writer 
import time
import pandas as pd
options = webdriver.ChromeOptions()
options.headless = False
#assert opts.headless  # Operating in headless mode
driver = Chrome(r'D:\prosper_2\chromedriver_win32\chromedriver.exe',options=options)
df=pd.read_excel(r"C:\Users\Administrator\Desktop\Minnesota_URL.xls")
for i in df["URL"]:
    driver.get(i)