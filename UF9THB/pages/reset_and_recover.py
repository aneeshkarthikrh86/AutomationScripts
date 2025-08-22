import os, time, datetime
from pages.login_page import Login
from pages.home_page import HomePage
from pages.game_page import Game_Click

class ResetAndRecover:
    def __init__(self, page, context, baseUrl, username, password):
        self.page = page
        self.context = context
        self.baseUrl = baseUrl
        self.username = username
        self.password = password

    def clear_session(self):
        self.context.clear_cookies()
        try:
            self.page.evaluate("localStorage.clear()")
            self.page.evaluate("sessionStorage.clear()")
        except:
            pass

    def reset_and_recover(self, provider_name, page_num, retry_index, game_name):
        print(f"🔄 Resetting session and retrying {provider_name} -> Page {page_num} -> {game_name}")

        dt = datetime.datetime.now().strftime("%d-%m-%y_%H-%M-%S")
        os.makedirs("screenshots", exist_ok=True)
        path = f"screenshots/reset_{provider_name}_page{page_num}_{game_name}_{dt}.png"
        self.page.screenshot(path=path)

        self.clear_session()
        self.page.goto(self.baseUrl, wait_until="domcontentloaded", timeout=30000)

        login_page = Login(self.baseUrl)
        login_page.page = self.page
        login_page.relogin(self.username, self.password)

        home_page = HomePage()
        home_page.page = self.page
        home_page.click_Slot()
        home_page.home_slot()

        # Use Game_Click helper to select provider instead of importing SlotProvider
        game_helper = Game_Click(self.page, self.context, self.baseUrl)
        game_helper.select_provider(provider_name)

        if page_num > 1:
            game_helper.click_page_number(page_num)

        # Retry same game
        Game_buttons = self.page.query_selector_all("//div[@class='game_btn_content']//button[text()='Play Now']")
        if retry_index < len(Game_buttons):
            retry_btn = Game_buttons[retry_index]
            retry_btn.scroll_into_view_if_needed()
            retry_btn.hover()
            time.sleep(1.5)
            retry_btn.click()
            print(f"🔁 Retried {game_name} on {provider_name} page {page_num}")
