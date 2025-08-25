# pages/recovery_helper.py
import os
import time
import datetime
from tests.base_page import BaseClass
from playwright.sync_api import Page, BrowserContext, TimeoutError

class RecoveryHelper(BaseClass):
    def __init__(self, page: Page, context: BrowserContext, baseUrl: str, username: str, password: str):
        self.page = page
        self.context = context
        self.baseUrl = baseUrl
        self.username = username
        self.password = password

    def get_screenshot_path(self, prefix, provider_name, page_num, game_name):
        """Generate screenshot path with datetime stamp."""
        dt = datetime.datetime.now().strftime("%d-%m-%y_%H-%M-%S")
        game_safe = game_name.replace(" ", "_").replace("/", "_")
        os.makedirs("screenshots", exist_ok=True)
        return f"screenshots/{prefix}_{provider_name}_page{page_num}_{game_safe}_{dt}.png"

    def reset_and_recover(self, provider_name, page_num, game_index, game_name):
        """
        Soft reset:
          - clear cookies/storage
          - reload base URL
          - resilient re-login
          - navigate back to provider/page
          - retry the failed game once
        """
        print(f"🔄 Resetting session and retrying {provider_name} → Page {page_num} → {game_name}")

        # Save screenshot before reset
        screenshot_path = self.get_screenshot_path("reset", provider_name, page_num, game_name)
        self.page.screenshot(path=screenshot_path)
        print(f"💾 Screenshot of reset saved: {screenshot_path}")

        # Step 1: Clear cookies and storage
        try:
            self.context.clear_cookies()
            self.page.evaluate("localStorage.clear()")
            self.page.evaluate("sessionStorage.clear()")
        except Exception:
            pass

        # Step 2: Reload base URL
        self.page.goto(self.baseUrl, wait_until="domcontentloaded", timeout=20000)

        # Step 3: Resilient Re-login
        from pages.login_page import Login
        from pages.home_page import HomePage
        login_page = Login(self.baseUrl)
        login_page.page = self.page

        success_login = False
        try:
            success_login = login_page.login(self.username, self.password, max_attempts=2)
            login_page.Close_Popupbtnscal()
        except Exception as e:
            print(f"⚠ Exception during login: {e}")

        if not success_login:
            print(f"❌ Login failed during reset, skipping game retry: {game_name}")
            return None, None

        # Step 4: Navigate back to Slots → Provider
        home_page = HomePage()
        home_page.page = self.page
        home_page.click_Slot()
        home_page.home_slot()

        # Click provider again
        provider_buttons = self.page.query_selector_all(
            "//div[@class='mt-5 flex items-center slot_btn_container w-full overflow-auto light-scrollbar-h pb-[10px]']//button"
        )
        for btn in provider_buttons:
            if btn.text_content().strip() == provider_name:
                btn.scroll_into_view_if_needed()
                btn.click()
                break

        # Step 5: Go to correct page number if needed
        if page_num > 1:
            from pages.Slot_Providers import SlotProvider
            slot_provider = SlotProvider(
                self.page,
                self.context,
                self.baseUrl,
                self.username,
                self.password
            )
            slot_provider.click_page_number(page_num)

        # Step 6: Retry the same game once
        game_buttons = self.page.query_selector_all("//div[@class='game_btn_content']//button[text()='Play Now']")
        if game_index < len(game_buttons):
            retry_btn = game_buttons[game_index]
            retry_btn.scroll_into_view_if_needed()
            retry_btn.hover()
            time.sleep(1.5)
            retry_btn.click()
            print(f"🔁 Retried {game_name} on {provider_name} page {page_num}")

            # Wait briefly & try closing
            try:
                if self.page.is_visible("//button/*[@class='w-5 h-5 game_header_close_btn']"):
                    time.sleep(15)
                    self.page.click("//button/*[@class='w-5 h-5 game_header_close_btn']")
                    print(f"✅ Success after reset: {game_name}")
                elif self.page.is_visible("//button[text()='Back To Home']"):
                    time.sleep(3)
                    self.page.click("//button[text()='Back To Home']")
                    print(f"✅ Success (back-to-home) after reset: {game_name}")
                elif self.page.is_visible("//button[text()='Cancel']"):
                    self.page.click("//button[text()='Cancel']")
                    print(f"✅ Success (cancel) after reset: {game_name}")
                else:
                    print(f"⚠ Game launched but no close button found: {game_name}")
            except Exception as e:
                print(f"❌ Error closing {game_name} after reset: {e}")

        return self.page, self.context
