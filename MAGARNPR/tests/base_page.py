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
        
def reset_and_recover(self, provider_name, page_num, retry_index):
    """
    Clears cache, logs in again, navigates back to the same provider and page,
    then retries the failed game once.
    """
    print(f"🔄 Resetting session and retrying {provider_name} -> Page {page_num} -> Game {retry_index+1}")

    # Step 1: Clear cache
    self.context.clear_cookies()
    try:
        self.page.evaluate("localStorage.clear()")
        self.page.evaluate("sessionStorage.clear()")
    except:
        pass

    # Step 2: Re-login
    from pages.login_page import Login
    from pages.home_page import HomePage
    from pages.Slot_Providers import SlotProvider
    import os

    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")

    login_page = Login(self.baseUrl)
    login_page.page = self.page
    login_page.login(USERNAME, PASSWORD)
    login_page.Close_Popupbtnscal()

    # Step 3: Navigate → Slot → Provider
    home_page = HomePage()
    home_page.page = self.page
    home_page.click_Slot()
    home_page.home_slot()

    slot_provider = SlotProvider()
    slot_provider.page = self.page
    Provider_btns = self.page.query_selector_all(
        "//div[@class='mt-5 flex items-center slot_btn_container w-full overflow-auto light-scrollbar-h pb-[10px]']//button"
    )
    for btn in Provider_btns:
        if btn.text_content().strip() == provider_name:
            btn.click()
            break

    # Step 4: Navigate to the correct page
    if page_num > 1:
        self.click_page_number(page_num)

    # Step 5: Retry the same game index
    Game_buttons = self.page.query_selector_all("//div[@class='game_btn_content']//button[text()='Play Now']")
    if retry_index < len(Game_buttons):
        retry_btn = Game_buttons[retry_index]
        retry_btn.scroll_into_view_if_needed()
        retry_btn.click()
        print(f"🔁 Retried game {retry_index+1} on {provider_name} page {page_num}")
        time.sleep(5)
        # try to close immediately if success
        if self.page.is_visible("//button/*[@class='w-5 h-5 game_header_close_btn']"):
            self.page.click("//button/*[@class='w-5 h-5 game_header_close_btn']")

        
        
        