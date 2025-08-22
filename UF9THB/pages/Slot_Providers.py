import time
from pages.game_page import Game_Click

class SlotProvider:
    def __init__(self):
        self.page = None
        self.context = None
        self.baseUrl = None
        self.username = None
        self.password = None

    def select_provider(self, provider_name):
        """Click a specific provider by name"""
        provider_xpath = "//div[@class='mt-5 flex items-center slot_btn_container w-full overflow-auto light-scrollbar-h pb-[10px]']//button"
        buttons = self.page.query_selector_all(provider_xpath)
        for btn in buttons:
            if btn.text_content().strip() == provider_name:
                btn.scroll_into_view_if_needed()
                time.sleep(0.3)
                btn.click()
                return True
        print(f"⚠ Provider not found: {provider_name}")
        return False

    def List_Provisers(self):
        provider_xpath = "//div[@class='mt-5 flex items-center slot_btn_container w-full overflow-auto light-scrollbar-h pb-[10px]']//button"
        total_providers = len(self.page.query_selector_all(provider_xpath))

        for indexp in range(1, total_providers):
            Provider_btns = self.page.query_selector_all(provider_xpath)
            Provider_btn = Provider_btns[indexp]

            provider_name = Provider_btn.text_content().strip()
            print(f"Provider: {provider_name}")

            Provider_btn.scroll_into_view_if_needed()
            time.sleep(0.3)
            Provider_btn.click()

            game_page = Game_Click(self.page, self.context, self.baseUrl)
            game_page.username = self.username
            game_page.password = self.password
            game_page.GamesbtnClick(provider_name)
