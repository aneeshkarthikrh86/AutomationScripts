from playwright.sync_api import sync_playwright, TimeoutError
import time

class RecoveryHelper:
    def __init__(self, login_func):
        """
        login_func: function that performs login when browser restarts.
        Example: login_func(context, page) -> returns logged in page
        """
        self.login_func = login_func

    def reset_and_recover(self, page, context, provider_name, page_num):
        """
        Soft recovery: close current game tab, refresh provider/page.
        """
        try:
            print(f"🔄 Soft reset: Provider={provider_name}, Page={page_num}")
            # close any child pages (game tabs)
            for p in context.pages[1:]:
                try:
                    p.close()
                except Exception:
                    pass

            # reload current provider/page
            page.reload()
            page.wait_for_selector("//div[@class='slot_game_container']", timeout=15000)
            print("✅ Soft reset successful.")
            return page, context
        except Exception as e:
            print(f"⚠️ Soft reset failed: {e}")
            return None, None

    def hard_restart(self, provider_index, page_num):
        """
        Hard recovery: restart browser & re-login.
        """
        try:
            print(f"🛠 Hard restart: Restarting browser at Provider {provider_index}, Page {page_num}")
            pw = sync_playwright().start()
            browser = pw.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            # perform login (user supplies login_func)
            page = self.login_func(context, page)

            # navigate back to provider/page
            self.navigate_to_provider_page(page, provider_index, page_num)

            print("✅ Hard restart successful.")
            return page, context, pw
        except Exception as e:
            print(f"🚨 Hard restart failed: {e}")
            return None, None, None

    def navigate_to_provider_page(self, page, provider_index, page_num):
        """
        Logic to click provider button + go to correct pagination page.
        You’ll need to adapt selectors to your site.
        """
        # Example: click provider
        providers = page.query_selector_all("//div[contains(@class,'slot_btn_container')]//button")
        providers[provider_index].click()
        page.wait_for_timeout(2000)

        # Example: click pagination
        page_buttons = page.query_selector_all(
            "//div[@class='p-holder admin-pagination']/button[not(contains(@class,'p-next')) and not(contains(@class,'p-prev'))]"
        )
        for btn in page_buttons:
            if btn.text_content().strip() == str(page_num):
                btn.click()
                page.wait_for_timeout(1500)
                break
