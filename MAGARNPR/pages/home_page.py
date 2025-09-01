import time
from tests.base_page import BaseClass

# pages/home_page.py
class HomePage(BaseClass):
    def click_Slot(self):
        self.page.wait_for_selector("//a[text()=' Slot']",timeout=12000).click()
        time.sleep(1)
    def home_slot(self):
        self.page.wait_for_selector("//a[text()=' Home']",timeout=12000).hover()
        time.sleep(1)
    def click_Fish(self):
        self.page.wait_for_selector("//a[text()=' Fishing']",timeout=12000).click()
        time.sleep(1)
    def click_Card(self):
        self.page.wait_for_selector("//a[text()=' Card Game']",timeout=12000).click()
        time.sleep(1)
    def click_Instawin(self): 
        self.page.wait_for_selector("//a[text()=' Instant Win']",timeout=12000).click()
        time.sleep(1)