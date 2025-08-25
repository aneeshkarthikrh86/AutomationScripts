import os
import time
import datetime
from tests.base_page import BaseClass
from playwright.sync_api import Page, BrowserContext

class RecoveryHelper(BaseClass):
    def __init__(self, page: Page, context: BrowserContext, baseUrl: str, username: str, password: str):
        self.page = page
        self.context = context
        self.baseUrl = baseUrl
        self.username = username
        self.password = password

    def get_screenshot_path(self, prefix, provider_name, page_num, game_name):
        dt = datetime.datetime.now().strftime("%d-%m-%y_%H-%M-%S")
        game_safe = game_name.replace(" ", "_").replace("/", "_")
        os.makedirs("screenshots", exist_ok=True)
        return f"screenshots/{prefix}_{provider_name}_page{page_num}_{game_safe}_{dt}.png"

    def reset_and_recover(self, provider_name, page_num, game_index, game_name):
        print(f"🔄 Resetting session and retrying {provider_name} → Page {page_num} → {game_name}")

        # Screenshot before reset
        screenshot_path = self.get_screenshot_path("reset", provider_name, page_num, game_name)
        try:
            self.page.screenshot(path=screenshot_path, full_page=True, timeout=60000)
            print(f"💾 Screenshot of reset saved: {screenshot_path}")
        except Exception as e:
            print(f"⚠ Screenshot failed: {e}")

        # Clear cookies/storage
        try:
            self.context.clear_cookies()
            self.page.evaluate("localStorage.clear()")
            self.page.evaluate("sessionStorage.clear()")
        except Exception:
            pass

        # Reload base URL
        self.page.goto(self.baseUrl, wait_until="domcontentloaded", timeout=20000)

        # Resilient login
        from pages.login_page import Login
        from pages.home_page import HomePage
        login_page = Login(self.baseUrl)
        login_page.page = self.page
        login_attempts = 0
        success_login = False
        while login_attempts < 3 and not success_login:
            try:
                login_page.login(self.username, self.password)
                login_page.Close_Popupbtnscal()
                success_login = True
            except Exception as e:
                login_attempts += 1
                print(f"⚠ Login attempt {login_attempts} failed: {e}")
                time.sleep(5)
        if not success_login:
            print(f"❌ Login failed after 3 attempts.")
            return None, None

        # Navigate back to Slots → Provider
        home_page = HomePage()
        home_page.page = self.page
        home_page.click_Slot()
        home_page.home_slot()

        # Click provider
        provider_buttons = self.page.query_selector_all(
            "//div[@class='mt-5 flex items-center slot_btn_container w-full overflow-auto light-scrollbar-h pb-[10px]']//button"
        )
        for btn in provider_buttons:
            if btn.text_content().strip() == provider_name:
                btn.scroll_into_view_if_needed()
                btn.click()
                break

        # Go to correct page if needed
        if page_num > 1:
            from pages.Slot_Providers import SlotProvider
            slot_provider = SlotProvider(self.page, self.context, self.baseUrl, self.username, self.password)
            slot_provider.click_page_number(page_num)

        # Retry game once
        game_buttons = self.page.query_selector_all("//div[@class='game_btn_content']//button[text()='Play Now']")
        if game_index < len(game_buttons):
            retry_btn = game_buttons[game_index]
            retry_btn.scroll_into_view_if_needed()
            retry_btn.hover()
            time.sleep(1.5)
            retry_btn.click()
            print(f"🔁 Retried {game_name} on {provider_name} page {page_num}")

            # Wait for close/back
            wait_for = [
                "//button/*[@class='w-5 h-5 game_header_close_btn']",
                "//button[text()='Back To Home']",
                "//button[text()='Cancel']"
            ]
            for _ in range(30):
                if any(self.page.is_visible(selector) for selector in wait_for):
                    break
                time.sleep(1)
            else:
                print(f"⚠ Game launched but no close/back button found: {game_name}")

            # Close game
            try:
                for selector in wait_for:
                    if self.page.is_visible(selector):
                        self.page.click(selector)
                        print(f"✅ Success after reset: {game_name}")
                        break
            except Exception as e:
                print(f"❌ Error closing {game_name} after reset: {e}")

        return self.page, self.context
