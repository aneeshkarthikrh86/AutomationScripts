from playwright.sync_api import sync_playwright
import time

# tests/base_page.py
class BaseClass:
    def __init__(self, baseUrl=None):
        self.baseUrl = baseUrl
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    def Start_Browser(self):
        # Get screen resolution
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless = False, args=["--start-maximized"])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()
        print("browser started (maximized)")
        
    def launch_url(self):
        self.page.goto(self.baseUrl, wait_until = "networkidle")
        print(f"Url excecuted {self.baseUrl}")
        
    def close_Browser(self):
        self.browser.close()
        self.playwright.stop()
        print("Browser closed")
        
def reset_and_recover(self, username, password, provider_name, page_number):
    print("🔄 Resetting session & re-logging in...")

    # Clear cookies/storage
    self.context.clear_cookies()
    try:
        self.page.evaluate("localStorage.clear()")
        self.page.evaluate("sessionStorage.clear()")
    except:
        pass

    # Relaunch login
    self.page.goto(self.baseUrl, wait_until="networkidle")
    from pages.login_page import Login
    login = Login(self.baseUrl)
    login.page = self.page
    login.login(username, password)
    login.Close_Popupbtnscal()

    # Back to Slots
    from pages.home_page import HomePage
    home = HomePage()
    home.page = self.page
    home.click_Slot()
    home.home_slot()

    # Back to correct provider
    from pages.Slot_Providers import SlotProvider
    sp = SlotProvider()
    sp.page = self.page
    provider_buttons = self.page.query_selector_all(
        "//div[@class='slot_btn_container']//button"
    )
    for btn in provider_buttons:
        if btn.text_content().strip() == provider_name:
            btn.scroll_into_view_if_needed()
            btn.click()
            break

    # Back to the same page
    from pages.game_page import Game_Click
    gc = Game_Click()
    gc.page = self.page
    if page_number > 1:
        gc.click_page_number(page_number)

    print(f"✅ Recovery complete → Provider: {provider_name}, Page: {page_number}")
        