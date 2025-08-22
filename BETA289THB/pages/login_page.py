import time
from tests.base_page import BaseClass

class Login(BaseClass):
    
    def enter_pin(self, pin="289289"):
        """Enter PIN into the PIN input field using JS evaluation"""
        self.page.evaluate(f'''
            () => {{
                const input = document.querySelector("#pinz");
                if (input) {{
                    input.focus();
                    input.value = "{pin}";
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    input.dispatchEvent(new KeyboardEvent('keyup', {{ bubbles: true, key: '0' }}));
                }}
            }}
        ''')
        print(f"🔑 PIN {pin} entered successfully.")

    def login(self, username, password, pin="289289"):
        """Performs the login flow with username, password, and optional PIN"""
        try:
            # Click Login button
            login_btn = self.page.locator("//div[@class='flex items-center gap-2 mr-2']//button[text()='Login']")
            login_btn.wait_for(state="visible", timeout=12000)
            login_btn.click()
            time.sleep(1)

            # Fill phone/username
            self.page.wait_for_selector("//input[@placeholder='09xxxxxxx']", timeout=12000).fill(username)
            time.sleep(1)

            # Next button
            self.page.wait_for_selector("//span[text()='Next']", timeout=12000).click()
            time.sleep(1)

            # Enter PIN
            self.enter_pin(pin)
            time.sleep(1)

            # Verify login success
            self.page.wait_for_selector("//button[text()='Logout']", timeout=8000)
            print("✅ Login successful.")
            return True

        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False

    def Close_Popupbtnscal(self):
        """Closes popup if it appears, otherwise silently continues"""
        try:
            popup_close = self.page.wait_for_selector(
                "//div[@style='max-width:600px;']/div/button[@class='mission_daily_close_btn']/img",
                timeout=3000
            )
            popup_close.click()
            time.sleep(1)
            print("🛑 Popup closed.")
        except:
            print("ℹ️ No popup to close.")
            pass