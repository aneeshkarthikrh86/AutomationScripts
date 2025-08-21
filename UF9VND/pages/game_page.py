import time
from tests.base_page import BaseClass
from playwright.sync_api import Error

class Game_Click(BaseClass):
    
    def reset_and_recover(self, provider_name, page_num, retry_index, game_name):
        """
        Clears cache, logs in again, navigates back to the same provider and page,
        then retries the failed game once.
        """
        print(f"🔄 Resetting session and retrying {provider_name} -> Page {page_num} -> {game_name}")

        # Step 1: Clear cache/cookies
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
            print(f"🔁 Retried {game_name} on {provider_name} page {page_num}")
            time.sleep(5)
            if self.page.is_visible("//button/*[@class='w-5 h-5 game_header_close_btn']"):
                self.page.click("//button/*[@class='w-5 h-5 game_header_close_btn']")
    
    def GamesbtnClick(self, provider_name=None):
        """
        Clicks all 'Play Now' buttons for the current provider.
        Handles success/failure and recovers automatically on go_back timeouts.
        """
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

            # Refresh game buttons for current page
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
                    time.sleep(2.5)
                    game_button_locator.wait_for(state="visible", timeout=12000)
                    time.sleep(2.5)
                    game_button_locator.click()
                    close_btn = "//button/*[@class='w-5 h-5 game_header_close_btn']"
                    toast_msg = "//div[@class='toast-message text-sm' and text()='Something went wrong. Try again later.']"

                    # Wait for either close or toast
                    max_wait = 20
                    interval = 1
                    for _ in range(int(max_wait / interval)):
                        if self.page.is_visible(close_btn) or self.page.is_visible(toast_msg):
                            break
                        time.sleep(interval)
                    else:
                        print(f"⚠ Timeout waiting for close button or toast for {Gamename} → Resetting & retrying")

                        # Clear + re-login + go back to provider/page + retry this same game
                        self.reset_and_recover(provider_name, current_page, indexg, Gamename)

                        # After retry, continue with next game
                        continue

                    # Handle success/failure
                    if self.page.is_visible(toast_msg):
                        failure_count += 1
                        try:
                            self.page.wait_for_selector("//button[text()='Back To Home']", timeout=5000).click()
                            print(f"❌ Failed: {Gamename}")
                        except Exception:
                            print(f"❌ Failed (go_back timeout, clearing cache): {Gamename}")
                            self.page.go_back()
                            try:
                                self.page.evaluate("localStorage.clear()")
                                self.page.evaluate("sessionStorage.clear()")
                            except:
                                pass
                            if provider_name:
                                self.reset_and_recover(provider_name, current_page, indexg, Gamename)
                    else:
                        time.sleep(10)
                        try:
                            self.page.wait_for_selector(close_btn, timeout=5000).click()
                            print(f"✅ Success: {Gamename}")
                        except Exception:
                            print(f"✅ Success (go_back timeout, clearing cache): {Gamename}")
                            self.context.clear_cookies()
                            try:
                                self.page.evaluate("localStorage.clear()")
                                self.page.evaluate("sessionStorage.clear()")
                            except:
                                pass
                            if provider_name:
                                self.reset_and_recover(provider_name, current_page, indexg, Gamename)

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
                    print(f"Error on {Gamename}: {e}")
                    self.reset_and_recover(provider_name, current_page, indexg, Gamename)

            # Go to next page
            if current_page < last_page_num:
                self.click_page_number(current_page + 1)
                time.sleep(3)
    
    def click_page_number(self, target_page):
        """
        Clicks the given page number in a shifting pagination UI.
        Will click intermediate pages until the target becomes visible.
        """
        while True:
            page_buttons = self.page.query_selector_all(
                "//div[@class='p-holder admin-pagination']/button[not(contains(@class,'p-next')) and not(contains(@class,'p-prev'))]"
            )
            visible_pages = [btn.text_content().strip() for btn in page_buttons]

            # If the target page number is visible, click it and break
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
