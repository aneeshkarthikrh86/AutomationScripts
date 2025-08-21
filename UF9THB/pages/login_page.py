import time
from tests.base_page import BaseClass

class Login(BaseClass):
    def login(self, username, password):
        login_btn = self.page.locator("//div[@class='flex items-center gap-2 mr-2']//button[text()='Login']")
        login_btn.wait_for(state="visible", timeout=12000)
        login_btn.click()
        time.sleep(1)

        self.page.wait_for_selector("//div[@class='relative mt-4']/input[@placeholder='Enter Your Username']", timeout=12000).fill(username)
        time.sleep(1)
        self.page.wait_for_selector("//input[@placeholder='Password']", timeout=12000).fill(password)
        self.page.wait_for_selector("//div[@class='relative flex justify-center']/button[text()='Login']", timeout=12000).click()
        time.sleep(3)

    def Close_Popupbtnscal(self):
        try:
            self.page.wait_for_selector("//div[@style='max-width:600px;']/div/button[@class='mission_daily_close_btn']/img", timeout=3000).click()
            time.sleep(1)
        except:
            pass
