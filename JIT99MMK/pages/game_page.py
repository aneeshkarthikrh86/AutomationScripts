import time
import os
import datetime
from tests.base_page import BaseClass
from playwright.sync_api import Page, BrowserContext
from pages.recovery_helper import RecoveryHelper


class Game_Click(BaseClass):
    def __init__(self, page: Page, context: BrowserContext,
                 baseUrl=None, username=None, password=None,
                 recovery: RecoveryHelper = None):
        self.page = page
        self.context = context
        self.baseUrl = baseUrl
        self.username = username
        self.password = password

        # Recovery helper (delegate reset here)
        self.recovery = recovery if recovery else RecoveryHelper(
            page, context, baseUrl, username, password
        )

        # Selectors
        self.play_button = "//button[contains(text(),'Play Now')]"
        self.close_button = "//button[contains(@class,'close-btn')]"
        self.back_button = "//button[contains(text(),'Back') or contains(@class,'back-btn')]"
        self.error_popup = "//div[contains(text(),'Failed to load game') or contains(text(),'Game Disabled')]"

    def get_screenshot_path(self, prefix, provider_name, page_num, game_name):
        """Generate screenshot path with datetime stamp."""
        dt = datetime.datetime.now().strftime("%d-%m-%y_%H-%M-%S")
        game_safe = game_name.replace(" ", "_").replace("/", "_")
        os.makedirs("screenshots", exist_ok=True)
        return f"screenshots/{prefix}_{provider_name}_page{page_num}_{game_safe}_{dt}.png"

    def GamesbtnClick(self, provider_name=None):
        """Click all 'Play Now' buttons, handle success/failure and retries with screenshots."""
        os.makedirs("screenshots", exist_ok=True)

        # Get total pages
        Total_Pages = self.page.query_selector_all(
            "//div[@class='p-holder admin-pagination']/button[not(contains(@class,'p-next')) and not(contains(@class,'p-prev'))]"
        )
        last_page_num = int(Total_Pages[-1].text_content()) if Total_Pages else 1
        print(f"Last page num is: {last_page_num}")

        failure_count = 0

        for current_page in range(1, last_page_num + 1):
            print(f"=== Now in Page {current_page} ===")
            time.sleep(2)

            Game_buttons = self.page.query_selector_all(
                "//div[@class='game_btn_content']//button[text()='Play Now']"
            )
            TotalGames = len(Game_buttons)
            print(f"Total Game: {TotalGames}")

            for indexg in range(TotalGames):
                try:
                    game_button_locator = self.page.locator(
                        "(//div[@class='game_btn_content']//button[text()='Play Now'])"
                    ).nth(indexg)
                    game_name_locator = self.page.locator(
                        "(//div[@class='game_btn_content_text'])"
                    ).nth(indexg)

                    Gamename = game_name_locator.text_content().strip()

                    # Scroll & click
                    game_button_locator.scroll_into_view_if_needed()
                    time.sleep(1.5)
                    game_button_locator.wait_for(state="visible", timeout=12000)
                    game_button_locator.click()
                    close_btn = "//button/*[@class='w-5 h-5 game_header_close_btn']"
                    toast_msg = ("//div[@class='toast-message text-sm' and "
                                 "text()='Something went wrong. Try again later.']")

                    # Wait for either close or toast
                    max_wait = 20
                    interval = 1
                    for _ in range(int(max_wait / interval)):
                        if self.page.is_visible(close_btn) or self.page.is_visible(toast_msg):
                            break
                        time.sleep(interval)
                    else:
                        # Timeout: take screenshot and recover
                        screenshot_path = self.get_screenshot_path("timeout", provider_name, current_page, Gamename)
                        self.page.screenshot(path=screenshot_path)
                        print(f"⚠ Timeout waiting for close or toast for {Gamename} → Screenshot saved: {screenshot_path}")
                        time.sleep(5)
                        self.recovery.reset_and_recover(provider_name, current_page, indexg, Gamename)
                        continue

                    # Handle success/failure
                    if self.page.is_visible(toast_msg):
                        failure_count += 1
                        time.sleep(5)
                        try:
                            self.page.wait_for_selector("//button[text()='Back To Home']", timeout=50000).click()
                            print(f"❌ Failed: {Gamename}")
                        except Exception:
                            screenshot_path = self.get_screenshot_path("fail", provider_name, current_page, Gamename)
                            self.page.screenshot(path=screenshot_path)
                            print(f"❌ Failed (go_back timeout) {Gamename} → Screenshot saved: {screenshot_path}")
                            self.page.go_back()
                            try:
                                self.page.evaluate("localStorage.clear()")
                                self.page.evaluate("sessionStorage.clear()")
                            except:
                                pass
                            if provider_name:
                                self.recovery.reset_and_recover(provider_name, current_page, indexg, Gamename)
                    else:
                        # Success
                        time.sleep(10)
                        try:
                            self.page.wait_for_selector(close_btn, timeout=25000).click()
                            print(f"✅ Success: {Gamename}")
                        except Exception:
                            screenshot_path = self.get_screenshot_path("success", provider_name, current_page, Gamename)
                            self.page.screenshot(path=screenshot_path)
                            print(f"✅ Success (go_back timeout) {Gamename} → Screenshot saved: {screenshot_path}")
                            self.context.clear_cookies()
                            try:
                                self.page.evaluate("localStorage.clear()")
                                self.page.evaluate("sessionStorage.clear()")
                            except:
                                pass
                            if provider_name:
                                self.recovery.reset_and_recover(provider_name, current_page, indexg, Gamename)

                    # Ensure we're on correct page
                    self.page.wait_for_selector("//button[text()='Logout']", timeout=12000)
                    time.sleep(2)
                    if current_page > 1:
                        self.click_page_number(current_page)

                    # Stop if too many failures
                    if failure_count >= 15:
                        print("❌ Too many failures. Skipping to next provider...")
                        return

                except Exception as e:
                    screenshot_path = self.get_screenshot_path("error", provider_name, current_page, Gamename)
                    self.page.screenshot(path=screenshot_path)
                    print(f"❌ Error on {Gamename}: {e} → Screenshot saved: {screenshot_path}")
                    time.sleep(5)
                    self.recovery.reset_and_recover(provider_name, current_page, indexg, Gamename)

            # Pagination screenshot
            if current_page < last_page_num:
                self.click_page_number(current_page + 1)
                time.sleep(3)

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

            # Otherwise, click the second-to-last visible number to shift forward
            second_last_btn = page_buttons[-2]
            if second_last_btn.text_content().strip() != "…":
                second_last_btn.scroll_into_view_if_needed()
                second_last_btn.click()
                time.sleep(3)
            else:
                # Fallback: click the last numeric before "…" if needed
                for btn in reversed(page_buttons):
                    if btn.text_content().strip().isdigit():
                        btn.scroll_into_view_if_needed()
                        btn.click()
                        time.sleep(3)
                        break