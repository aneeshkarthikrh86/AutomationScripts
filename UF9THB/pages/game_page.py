import time
import os
import datetime
from tests.base_page import BaseClass
from playwright.sync_api import Error


class GameClick(BaseClass):
    """Handles game clicking, retries, and session recovery."""

    def get_screenshot_path(self, prefix, provider_name, page_num, game_name):
        """Generate screenshot path with datetime stamp."""
        dt = datetime.datetime.now().strftime("%d-%m-%y_%H-%M-%S")
        game_safe = game_name.replace(" ", "_").replace("/", "_")
        os.makedirs("screenshots", exist_ok=True)
        return f"screenshots/{prefix}_{provider_name}_page{page_num}_{game_safe}_{dt}.png"

    def clear_session(self):
        """Clear cookies, localStorage, sessionStorage."""
        self.context.clear_cookies()
        try:
            self.page.evaluate("localStorage.clear()")
            self.page.evaluate("sessionStorage.clear()")
        except Exception:
            pass

    def relogin(self):
        """Perform re-login after session reset."""
        from pages.login_page import Login
        from pages.home_page import HomePage

        USERNAME = os.getenv("USERNAME")
        PASSWORD = os.getenv("PASSWORD")

        login_page = Login(self.baseUrl)
        login_page.page = self.page
        login_page.login(USERNAME, PASSWORD)
        login_page.Close_Popupbtnscal()

        home_page = HomePage()
        home_page.page = self.page
        home_page.click_Slot()
        home_page.home_slot()

    def select_provider(self, provider_name, page_num):
        """Navigate to the given provider and page number."""
        from pages.Slot_Providers import SlotProvider

        slot_provider = SlotProvider()
        slot_provider.page = self.page
        Provider_btns = self.page.query_selector_all(
            "//div[@class='mt-5 flex items-center slot_btn_container w-full overflow-auto light-scrollbar-h pb-[10px]']//button"
        )
        for btn in Provider_btns:
            if btn.text_content().strip() == provider_name:
                btn.click()
                break

        if page_num > 1:
            self.click_page_number(page_num)

    def reset_and_recover(self, provider_name, page_num, retry_index, game_name):
        """Full reset: clear session, reload, login, retry game."""
        print(f"🔄 Resetting session and retrying {provider_name} -> Page {page_num} -> {game_name}")

        screenshot_path = self.get_screenshot_path("reset", provider_name, page_num, game_name)
        self.page.screenshot(path=screenshot_path)
        print(f"💾 Screenshot of reset saved: {screenshot_path}")

        self.clear_session()
        self.page.goto(self.baseUrl, wait_until="networkidle", timeout=25000)

        try:
            self.relogin()
            self.select_provider(provider_name, page_num)
        except Exception as e:
            print(f"❌ Reset failed during login/provider navigation: {e}")
            return

        Game_buttons = self.page.query_selector_all("//div[@class='game_btn_content']//button[text()='Play Now']")
        if retry_index < len(Game_buttons):
            retry_btn = Game_buttons[retry_index]
            retry_btn.scroll_into_view_if_needed()
            retry_btn.hover()
            time.sleep(1.5)
            retry_btn.click()
            print(f"🔁 Retried {game_name} on {provider_name} page {page_num}")
            self._close_if_open(game_name)

    def _close_if_open(self, game_name):
        """Attempt to close a running game gracefully."""
        try:
            if self.page.is_visible("//button/*[@class='w-5 h-5 game_header_close_btn']"):
                self.page.click("//button/*[@class='w-5 h-5 game_header_close_btn']")
                print(f"✅ Success after reset: {game_name}")
            elif self.page.is_visible("//button[text()='Back To Home']"):
                self.page.click("//button[text()='Back To Home']")
                print(f"✅ Success (back-to-home) after reset: {game_name}")
            elif self.page.is_visible("//button[text()='Cancel']"):
                self.page.click("//button[text()='Cancel']")
                print(f"✅ Success (cancel) after reset: {game_name}")
            else:
                print(f"⚠ Game launched but no close button found: {game_name}")
        except Exception as e:
            print(f"❌ Error closing {game_name} after reset: {e}")

    def GamesbtnClick(self, provider_name=None):
        """Click all 'Play Now' buttons, handle success/failure and retries with screenshots."""
        os.makedirs("screenshots", exist_ok=True)

        Total_Pages = self.page.query_selector_all(
            "//div[@class='p-holder admin-pagination']/button[not(contains(@class,'p-next')) and not(contains(@class,'p-prev'))]"
        )
        last_page_num = int(Total_Pages[-1].text_content()) if Total_Pages else 1
        print(f"Last page num is: {last_page_num}")

        failure_count = 0

        for current_page in range(1, last_page_num + 1):
            print(f"=== Now in Page {current_page} ===")
            time.sleep(2)

            Game_buttons = self.page.query_selector_all("//div[@class='game_btn_content']//button[text()='Play Now']")
            TotalGames = len(Game_buttons)
            print(f"Total Games: {TotalGames}")

            for indexg in range(TotalGames):
                game_name_locator = self.page.locator("(//div[@class='game_btn_content_text'])").nth(indexg)
                Gamename = game_name_locator.text_content().strip()

                try:
                    game_button = self.page.locator(
                        "(//div[@class='game_btn_content']//button[text()='Play Now'])"
                    ).nth(indexg)

                    game_button.scroll_into_view_if_needed()
                    time.sleep(1.5)
                    game_button.wait_for(state="visible", timeout=12000)
                    game_button.click()

                    close_btn = "//button/*[@class='w-5 h-5 game_header_close_btn']"
                    toast_msg = "//div[@class='toast-message text-sm' and text()='Something went wrong. Try again later.']"

                    self._wait_game_state(Gamename, provider_name, current_page, indexg, close_btn, toast_msg)

                    if failure_count >= 15:
                        print("❌ Too many failures. Skipping to next provider...")
                        return

                except Exception as e:
                    screenshot_path = self.get_screenshot_path("error", provider_name, current_page, Gamename)
                    self.page.screenshot(path=screenshot_path)
                    print(f"❌ Error on {Gamename}: {e} → Screenshot saved: {screenshot_path}")
                    time.sleep(5)
                    self.reset_and_recover(provider_name, current_page, indexg, Gamename)

            if current_page < last_page_num:
                self.click_page_number(current_page + 1)
                time.sleep(3)

    def _wait_game_state(self, game_name, provider_name, current_page, indexg, close_btn, toast_msg):
        """Wait for game success or failure message, handle accordingly."""
        max_wait, interval = 20, 1
        for _ in range(int(max_wait / interval)):
            if self.page.is_visible(close_btn) or self.page.is_visible(toast_msg):
                break
            time.sleep(interval)
        else:
            screenshot_path = self.get_screenshot_path("timeout", provider_name, current_page, game_name)
            self.page.screenshot(path=screenshot_path)
            print(f"⚠ Timeout waiting for {game_name} → Screenshot saved: {screenshot_path}")
            self.reset_and_recover(provider_name, current_page, indexg, game_name)
            return

        if self.page.is_visible(toast_msg):
            self._handle_failure(game_name, provider_name, current_page, indexg)
        else:
            self._handle_success(game_name, close_btn, provider_name, current_page, indexg)

    def _handle_failure(self, game_name, provider_name, current_page, indexg):
        """Handle failure case with screenshots and recovery."""
        try:
            self.page.wait_for_selector("//button[text()='Back To Home']", timeout=5000).click()
            print(f"❌ Failed: {game_name}")
        except Exception:
            screenshot_path = self.get_screenshot_path("fail", provider_name, current_page, game_name)
            self.page.screenshot(path=screenshot_path)
            print(f"❌ Failed (go_back timeout) {game_name} → Screenshot saved: {screenshot_path}")
            self.page.go_back()
            self.clear_session()
            self.reset_and_recover(provider_name, current_page, indexg, game_name)

    def _handle_success(self, game_name, close_btn, provider_name, current_page, indexg):
        """Handle success case with close or fallback reset."""
        time.sleep(5)
        try:
            self.page.wait_for_selector(close_btn, timeout=5000).click()
            print(f"✅ Success: {game_name}")
        except Exception:
            screenshot_path = self.get_screenshot_path("success", provider_name, current_page, game_name)
            self.page.screenshot(path=screenshot_path)
            print(f"✅ Success (no close button) {game_name} → Screenshot saved: {screenshot_path}")
            self.clear_session()
            self.reset_and_recover(provider_name, current_page, indexg, game_name)

    def click_page_number(self, target_page):
        """Click target page in shifting pagination UI."""
        while True:
            page_buttons = self.page.query_selector_all(
                "//div[@class='p-holder admin-pagination']/button[not(contains(@class,'p-next')) and not(contains(@class,'p-prev'))]"
            )
            visible_pages = [btn.text_content().strip() for btn in page_buttons]

            if str(target_page) in visible_pages:
                for btn in page_buttons:
                    if btn.text_content().strip() == str(target_page):
                        btn.scroll_into_view_if_needed()
                        btn.click()
                        time.sleep(3)
                        return True

            second_last_btn = page_buttons[-2]
            if second_last_btn.text_content().strip() != "…":
                second_last_btn.scroll_into_view_if_needed()
                second_last_btn.click()
                time.sleep(3)
            else:
                for btn in reversed(page_buttons):
                    if btn.text_content().strip().isdigit():
                        btn.scroll_into_view_if_needed()
                        btn.click()
                        time.sleep(3)
                        break
