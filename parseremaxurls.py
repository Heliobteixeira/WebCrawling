# -*- coding: latin-1 -*-
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def loadurls(jsonfile):
    emptyjson={}
    try:
        with open(jsonfile, 'r') as file:
            return json.load(file)
    except:
        return emptyjson
    
def saveurl(id, url, jsonfile):
    print 'Saving:' + id + url
    jsonvar=loadurls(jsonfile) #Load existing json
    jsonvar[str(id)]=url
    
    with open(jsonfile, 'w') as file:    
        json.dump(jsonvar, file)

def startwebdriver():
    driver = webdriver.Firefox()
    return driver

def openAdvancedSearch():
    global driver
    driver.get("http://www.remax.pt/AdvancedListingSearch.aspx")

def fillAdvancedSearch(propertytype, minprice):
    global driver
    driver.find_element_by_css_selector("input[type='radio'][name='ctl00$rdoComRes']").click() # Seleccionar Residencial
    driver.find_element_by_css_selector("input[type='radio'][name='ctl00$ddlTransactionType']").click() # Seleccionar For Sale
##    select = Select(driver.find_element_by_name('ctl00$ddlEnergyRatings'))
##    select.select_by_visible_text(CLASS)
    select = Select(driver.find_element_by_name('ctl00$ddlPropertyType'))
    select.select_by_visible_text(propertytype)
    select = Select(driver.find_element_by_name('ctl00$ddlMinPrice'))
    select.select_by_value(minprice)
    driver.find_element_by_css_selector("input[type='submit'][name='ctl00$btnSearch']").click()
    
def captureurls(jsonfile):
    global driver
    tds=driver.find_elements_by_class_name("proplist_id")
    for i in tds:
        id=i.find_element_by_tag_name('a')
        saveurl(id.text, id.get_attribute('href'), jsonfile)
        
def gotonextpage():
    global driver
    driver.find_element_by_link_text('Página Seguinte').click()

propertytype = 'Apartamento'

jsonfile='mined_urls_class'+propertytype

driver=startwebdriver()
openAdvancedSearch()
fillAdvancedSearch(propertytype, '20000')
try:    
    while True:        
        captureurls(jsonfile)
        gotonextpage()
        element=WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.ID, "divWaitImg")))
        element=WebDriverWait(driver, 120).until(EC.invisibility_of_element_located((By.ID, "divWaitImg")))
except:
    driver.close()
    raise
