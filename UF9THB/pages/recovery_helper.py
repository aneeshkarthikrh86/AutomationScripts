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

    def reset_and_recover(self, provider_name, page_num, game_index, game_name, hard_reset=True):
        print(f"🔄 Resetting session ({'HARD' if hard_reset else 'LIGHT'}) → {provider_name} → Page {page_num} → {game_name}")

        screenshot_path = self.get_screenshot_path("reset", provider_name, page_num, game_name)
        try:
            self.page.screenshot(path=screenshot_path, full_page=True, timeout=60000)
            print(f"💾 Screenshot saved: {screenshot_path}")
        except Exception as e:
            print(f"⚠ Screenshot failed: {e}")

        if hard_reset:
            try:
                self.context.clear_cookies()
                self.page.evaluate("localStorage.clear()")
                self.page.evaluate("sessionStorage.clear()")
            except Exception:
                pass

            # ✅ Safe navigation with retries
            success_nav = False
            for attempt in range(3):
                try:
                    self.page.goto(self.baseUrl, wait_until="domcontentloaded", timeout=60000)
                    success_nav = True
                    break
                except Exception as e:
                    print(f"⚠ goto attempt {attempt+1} failed: {e}")
                    time.sleep(5)
            if not success_nav:
                print("❌ Could not reload base URL after 3 attempts")
                return None, None

            from pages.login_page import Login
            from pages.home_page import HomePage

            login_page = Login(self.baseUrl)
            login_page.page = self.page
            success_login = False
            for attempt in range(3):
                try:
                    login_page.login(self.username, self.password)
                    login_page.Close_Popupbtnscal()
                    success_login = True
                    break
                except Exception as e:
                    print(f"⚠ Login attempt {attempt+1} failed: {e}")
                    time.sleep(5)
            if not success_login:
                print(f"❌ Login failed after 3 attempts.")
                return None, None

            home_page = HomePage()
            home_page.page = self.page
            home_page.click_Slot()
            home_page.home_slot()

            # Select provider button
            provider_buttons = self.page.query_selector_all(
                "//div[@class='mt-5 flex items-center slot_btn_container w-full overflow-auto light-scrollbar-h pb-[10px]']//button"
            )
            for btn in provider_buttons:
                if btn.text_content().strip() == provider_name:
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    break

            # ✅ Pagination with Game_Click
            if page_num > 1:
                from pages.game_page import Game_Click
                game_click = Game_Click(self.page, self.context, self.baseUrl, self.username, self.password, recovery=self)
                game_click.click_page_number(page_num)

        # Retry game
        game_buttons = self.page.query_selector_all("//div[@class='game_btn_content']//button[text()='Play Now']")
        if game_index < len(game_buttons):
            retry_btn = game_buttons[game_index]
            retry_btn.scroll_into_view_if_needed()
            retry_btn.hover()
            time.sleep(1.5)
            retry_btn.click()
            print(f"🔁 Retried {game_name} on {provider_name} page {page_num}")

            # ✅ Use shared safe exit logic from Game_Click
            from pages.game_page import Game_Click
            temp_game_click = Game_Click(self.page, self.context, self.baseUrl, self.username, self.password, recovery=self)
            temp_game_click.handle_game_exit(game_name)

            time.sleep(3)

        return self.page, self.context
