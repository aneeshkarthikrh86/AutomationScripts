import time
from playwright.sync_api import TimeoutError
from tests.base_page import BaseClass

class Login(BaseClass):
    def login(self, username, password, max_attempts=2):
        """
        Login with retry if initial login modal fails.
        Steps:
        1. Click 'Login' button to open modal.
        2. Enter username & password.
        3. Click 'Login' inside modal.
        4. If any step fails, close modal and retry once.
        """
        attempt = 1
        while attempt <= max_attempts:
            try:
                # Open login modal
                login_btn = self.page.locator("//div[@class='flex items-center gap-2 mr-2']//button[text()='Login']")
                login_btn.wait_for(state="visible", timeout=12000)
                login_btn.click()
                time.sleep(1)

                # Fill username & password
                self.page.wait_for_selector("//input[@placeholder='Username']", timeout=12000).fill(username)
                time.sleep(0.5)
                self.page.wait_for_selector("//input[@placeholder='Password']", timeout=12000).fill(password)

                # Click Login
                self.page.wait_for_selector("//div[@class='relative mt-8']/button[text()='Login']", timeout=12000).click()
                time.sleep(2)
                
                print(f"✅ Login successful on attempt {attempt}")
                return True

            except TimeoutError as e:
                print(f"⚠ Login attempt {attempt} failed: {e}")
                attempt += 1

                # Try to close login modal if open
                try:
                    close_modal_btn = self.page.locator("//div[@class='relative auth-skin']/button[@class='absolute top-[22px] right-[20px]']/img']")
                    if close_modal_btn.is_visible():
                        close_modal_btn.click()
                        time.sleep(1)
                        print("ℹ Login modal closed, retrying...")
                except Exception:
                    print("ℹ No login modal to close, retrying...")

        print("❌ Login failed after retries")
        return False

    def Close_Popupbtnscal(self):
        """Close any daily mission popups if present."""
        try:
            self.page.wait_for_selector(
                "//div[@style='max-width:600px;']/div/button[@class='mission_daily_close_btn']/img",
                timeout=3000
            ).click()
            time.sleep(1)
        except:
            pass