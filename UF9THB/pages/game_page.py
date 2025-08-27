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

    def handle_game_exit(self, game_name: str):
        """
        Shared safe method for closing games / handling toast popups.
        - Waits for iframe/game to actually load before closing.
        - Falls back to go_back() if stale element.
        """
        close_btn_selector = "//button/*[@class='w-5 h-5 game_header_close_btn']"
        toast_selector = "//div[@class='toast-message text-sm' and contains(text(),'Something went wrong')]"
        back_btn_selector = "//button[text()='Back To Home']"
        iframe_selector = "//iframe[contains(@class,'game_iframe')]"   # adjust if you have a stable locator
        common_image_xpath = "//img"  # or a known loading element inside iframe

        try:
            # ✅ Case 1: Close button visible
            if self.page.is_visible(close_btn_selector):
                print(f"⏳ Close button detected for {game_name}, waiting for game iframe...")
                try:
                    # Wait for iframe or game image (so we know it really loaded)
                    self.page.wait_for_selector(iframe_selector, timeout=15000)
                    self.page.wait_for_selector(common_image_xpath, timeout=15000)
                    print("Success: {game_name}")
                except Exception:
                    print(f"⚠ Game iframe not detected for {game_name}, continuing anyway.")

                print(f"⏳ Waiting 10s before closing {game_name}...")
                time.sleep(10)

                try:
                    self.page.click(close_btn_selector, timeout=5000)
                    print(f"✅ Closed {game_name}")
                    return True
                except Exception:
                    print(f"⚠ Close btn failed (stale) → using page.go_back()")
                    self.page.go_back(timeout=20000)
                    print(f"✅ Closed {game_name}")
                    return True

            # ✅ Case 2: Toast error visible
            elif self.page.is_visible(toast_selector):
                print(f"❌ Toast error for {game_name}, waiting 3s before back...")
                time.sleep(3)
                try:
                    if self.page.is_visible(back_btn_selector):
                        self.page.click(back_btn_selector, timeout=5000)
                        print(f"↩️ Back to lobby from {game_name}")
                        print("Failed: {game_name}")
                        return False
                    else:
                        print(f"⚠ Back button not visible, fallback go_back()")
                        self.page.go_back(timeout=20000)
                        print("Failed: {game_name}")
                        return False
                except Exception:
                    print(f"⚠ Back btn failed (stale) → using page.go_back()")
                    self.page.go_back(timeout=20000)
                    return False

            # ✅ Case 3: Neither close nor toast found
            else:
                print(f"⚠ No close/back/toast found → fallback page.go_back() for {game_name}")
                self.page.go_back(timeout=20000)
                return True

        except Exception as e:
            print(f"⚠ handle_game_exit error for {game_name}: {e}")
            try:
                self.page.go_back(timeout=20000)
                return True
            except:
                return False

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

                    game_key = f"{provider_name}_{current_page}_{indexg}"
                    if game_key in self.retried_games:
                        continue

                    # Try to click Play Now
                    for attempt in range(3):
                        try:
                            game_button_locator.wait_for(state="visible", timeout=15000)
                            game_button_locator.scroll_into_view_if_needed()
                            time.sleep(1)
                            game_button_locator.click()
                            break
                        except:
                            time.sleep(1)
                            if attempt == 2:
                                raise

                    # wait until either close_btn or toast_msg appears
                    close_btn = "//button/*[@class='w-5 h-5 game_header_close_btn']"
                    toast_msg = "//div[@class='toast-message text-sm' and text()='Something went wrong. Try again later.']"

                    for _ in range(30):
                        if self.page.is_visible(close_btn) or self.page.is_visible(toast_msg):
                            break
                        time.sleep(2)
                    else:
                        screenshot_path = self.get_screenshot_path("timeout", provider_name, current_page, Gamename)
                        self.page.screenshot(path=screenshot_path)
                        print(f"⚠ Timeout for {Gamename}")
                        self.retried_games.add(game_key)
                        self.recovery.reset_and_recover(provider_name, current_page, indexg, Gamename, hard_reset=False)
                        continue

                    # ✅ use the new safe exit handler
                    result = self.handle_game_exit(Gamename)
                    if result is False:
                        failure_count += 1
                        self.retried_games.add(game_key)
                        hard_reset = failure_count % 5 == 0
                        self.recovery.reset_and_recover(provider_name, current_page, indexg, Gamename, hard_reset)

                    time.sleep(2.5)
                    if current_page > 1:
                        self.click_page_number(current_page)

                    if failure_count >= 15:
                        print("❌ Too many failures → skipping provider")
                        return

                except Exception as e:
                    screenshot_path = self.get_screenshot_path("error", provider_name, current_page, Gamename)
                    self.page.screenshot(path=screenshot_path)
                    print(f"❌ Error on {Gamename}: {e}")
                    time.sleep(5)
                    self.retried_games.add(game_key)
                    self.recovery.reset_and_recover(provider_name, current_page, indexg, Gamename, hard_reset=False)

            if current_page < last_page_num:
                self.click_page_number(current_page + 1)
                time.sleep(3)

    def click_page_number(self, target_page: int):
        print(f"🔹 Attempting to go to page {target_page}")
        for attempt in range(3):
            try:
                pagination_container = self.page.locator("//div[@class='p-holder admin-pagination']")
                if pagination_container.is_visible():
                    pagination_container.scroll_into_view_if_needed()
                time.sleep(1)

                page_buttons = self.page.query_selector_all(
                    "//div[@class='p-holder admin-pagination']/button[not(contains(@class,'p-next')) and not(contains(@class,'p-prev'))]"
                )

                if not page_buttons:
                    print(f"⚠ Attempt {attempt+1}: no pagination buttons")
                    time.sleep(2)
                    continue

                max_visible = len(page_buttons)
                if target_page <= max_visible:
                    btn = page_buttons[target_page - 1]
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    time.sleep(1)
                    return True

                while True:
                    anchor_btn = page_buttons[-1]
                    anchor_btn.scroll_into_view_if_needed()
                    anchor_btn.click()
                    time.sleep(1.5)
                    page_buttons = self.page.query_selector_all(
                        "//div[@class='p-holder admin-pagination']/button[not(contains(@class,'p-next')) and not(contains(@class,'p-prev'))]"
                    )
                    if target_page <= len(page_buttons):
                        btn = page_buttons[target_page - 1]
                        btn.scroll_into_view_if_needed()
                        btn.click()
                        time.sleep(1)
                        print(f"✅ Clicked hidden page {target_page}")
                        return True

            except Exception as e:
                print(f"⚠ Attempt {attempt+1} failed: {e}")
                time.sleep(2)

        print(f"❌ Could not click page {target_page}")
        return False
