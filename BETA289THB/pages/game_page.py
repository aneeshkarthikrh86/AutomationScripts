import os
import time
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
        self.recovery = recovery if recovery else RecoveryHelper(page, context, baseUrl, username, password)
        self.retried_games = set()

    def get_screenshot_path(self, prefix, provider_name, page_num, game_name):
        dt = datetime.datetime.now().strftime("%d-%m-%y_%H-%M-%S")
        game_safe = game_name.replace(" ", "_").replace("/", "_")
        os.makedirs("screenshots", exist_ok=True)
        return f"screenshots/{prefix}_{provider_name}_page{page_num}_{game_safe}_{dt}.png"

    def GamesbtnClick(self, provider_name=None):
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
            print(f"Total Game: {TotalGames}")

            for indexg in range(TotalGames):
                try:
                    game_button_locator = self.page.locator("(//div[@class='game_btn_content']//button[text()='Play Now'])").nth(indexg)
                    game_name_locator = self.page.locator("(//div[@class='game_btn_content_text'])").nth(indexg)
                    Gamename = game_name_locator.text_content().strip()

                    # Skip if already retried
                    game_key = f"{provider_name}_{current_page}_{indexg}"
                    if game_key in self.retried_games:
                        continue

                    # Click game
                    game_button_locator.scroll_into_view_if_needed()
                    time.sleep(1.5)
                    game_button_locator.wait_for(state="visible", timeout=12000)
                    game_button_locator.click()

                    close_btn = "//button/*[@class='w-5 h-5 game_header_close_btn']"
                    toast_msg = "//div[@class='toast-message text-sm' and text()='Something went wrong. Try again later.']"

                    # Wait for close/toast
                    for _ in range(20):
                        if self.page.is_visible(close_btn) or self.page.is_visible(toast_msg):
                            break
                        time.sleep(1)
                    else:
                        screenshot_path = self.get_screenshot_path("timeout", provider_name, current_page, Gamename)
                        self.page.screenshot(path=screenshot_path)
                        print(f"⚠ Timeout for {Gamename} → Screenshot saved: {screenshot_path}")
                        self.retried_games.add(game_key)
                        self.recovery.reset_and_recover(provider_name, current_page, indexg, Gamename)
                        continue

                    # Handle result
                    if self.page.is_visible(toast_msg):
                        failure_count += 1
                        try:
                            self.page.wait_for_selector("//button[text()='Back To Home']", timeout=5000).click()
                        except:
                            screenshot_path = self.get_screenshot_path("fail", provider_name, current_page, Gamename)
                            self.page.screenshot(path=screenshot_path)
                        print(f"❌ Failed: {Gamename}")
                        self.retried_games.add(game_key)
                        self.recovery.reset_and_recover(provider_name, current_page, indexg, Gamename)
                    else:
                        try:
                            self.page.wait_for_selector(close_btn, timeout=5000).click()
                            print(f"✅ Success: {Gamename}")
                        except:
                            screenshot_path = self.get_screenshot_path("success", provider_name, current_page, Gamename)
                            self.page.screenshot(path=screenshot_path)
                            print(f"✅ Success (timeout) {Gamename} → Screenshot saved: {screenshot_path}")

                    # Ensure on correct page
                    if current_page > 1:
                        self.click_page_number(current_page)

                    if failure_count >= 15:
                        print("❌ Too many failures. Skipping to next provider...")
                        return

                except Exception as e:
                    screenshot_path = self.get_screenshot_path("error", provider_name, current_page, Gamename)
                    self.page.screenshot(path=screenshot_path)
                    print(f"❌ Error on {Gamename}: {e} → Screenshot saved: {screenshot_path}")
                    time.sleep(5)
                    self.retried_games.add(game_key)
                    self.recovery.reset_and_recover(provider_name, current_page, indexg, Gamename)

            if current_page < last_page_num:
                self.click_page_number(current_page + 1)
                time.sleep(3)

    def click_page_number(self, target_page):
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
                        self.page.wait_for_selector("//div[@class='game_btn_content']//button[text()='Play Now']", timeout=20000)
                        time.sleep(2)
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
