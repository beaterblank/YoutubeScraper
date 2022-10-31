from datetime import datetime
import dateutil.parser
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from traceback import print_stack
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from typing import Union
import logging
import time
import re

class Youtube:
    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_argument("--disable-features=PreloadMediaEngagementData, MediaEngagementBypassAutoplayPolicies")
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)

    def getByXpath(self,value: str,multiple:bool=False,
    timeout:float=5)-> Union[list[WebElement],WebElement]:

        start = time.time()
        diff = 0
        while(diff<timeout):
            try:
                if(multiple):
                    element = self.driver.find_elements(by='xpath',value=value)
                else:
                    element = self.driver.find_element(by='xpath',value=value)
                break;
            except NoSuchElementException:
                end = time.time()
                pass
            diff = end-start
        else:
            raise NoSuchElementException("timed out :( no Element Found")
        return element
    
    def processCounts(self,count:str)->int:
        temp = count
        cleaned = re.sub('[^A-Za-z0-9]+', '', count)
        cleaned = cleaned.replace(',','')
        cleaned = cleaned.replace('K','000')
        cleaned = cleaned.replace('lakhs','00000')
        cleaned = cleaned.replace('crore','0000000')
        cleaned = cleaned.replace('M','000000')
        cleaned = re.sub('[^0-9]+', '', cleaned)
        return int(cleaned)
    def processDates(self,datestring:str)->datetime:
        return dateutil.parser.parse(datestring).date()



class VideoPage(Youtube):
    def __init__(self,video: str) -> None:
        Youtube.__init__(self)
        self.video = video
        self.driver.get("https://www.youtube.com/watch?v="+video)
        self.getByXpath(value='//*[@id="description-inner"]')
        self.driver.find_element(value='html',by='tag name').send_keys(Keys.END)
        self.driver.execute_script('document.querySelector("#expand").click()')

    def getTitle(self)->str:
        return self.getByXpath('//*[@id="title"]/h1/yt-formatted-string').get_attribute("innerHTML")

    def getLikes(self)->int:
        return self.processCounts(self.getByXpath(value ='//*[@id="segmented-like-button"]/ytd-toggle-button-renderer/yt-button-shape/button/div[2]/span').get_attribute("innerHTML"))
    
    def getViewCount(self)->int:
        return self.processCounts(self.getByXpath(value = '//*[@id="info"]/span[1]').get_attribute('innerHTML'))

    def getUploadDate(self)->datetime:
        return self.processDates(self.getByXpath(value='//*[@id="info"]/span[3]').get_attribute('innerHTML'))
    
    def getCommentCount(self)->int:
        return self.processCounts(self.getByXpath(value='//*[@id="count"]/yt-formatted-string/span[1]').get_attribute('innerHTML'))
    
    def info(self) -> str:
        dct = {}
        dct['Title'] = self.getTitle()
        dct['Views'] = self.getViewCount()
        dct['Upload'] = self.getUploadDate()
        dct['Comments'] = self.getCommentCount()
        dct['Likes'] = self.getLikes()
        return str(dct)





    

