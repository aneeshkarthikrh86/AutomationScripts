import time
from tests.base_page import BaseClass
from pages.game_page import Game_Click

class SlotProvider:
    def __init__(self):
        self.page = None
        self.context = None
        self.baseUrl = None
        self.username = None
        self.password = None

    def List_Provisers(self):
        # find provider buttons dynamically each loop
        provider_xpath = "//div[@class='mt-5 flex items-center slot_btn_container w-full overflow-auto light-scrollbar-h pb-[10px]']//button"
        total_providers = len(self.page.query_selector_all(provider_xpath))

        for indexp in range(1, total_providers):  # skipping 0 if that’s 'All'
            # refresh provider buttons every loop (to avoid stale element handles)
            Provider_btns = self.page.query_selector_all(provider_xpath)
            Provider_btn = Provider_btns[indexp]

            provider_name = Provider_btn.text_content().strip()
            print(f"Provider: {provider_name}")

            # make sure visible & in view before click
            Provider_btn.scroll_into_view_if_needed()
            self.page.wait_for_timeout(300)  # tiny wait
            Provider_btn.click()

            # Create game page handler with shared context
            game_page = Game_Click()
            game_page.page = self.page
            game_page.context = self.context
            game_page.baseUrl = self.baseUrl
            game_page.username = self.username
            game_page.password = self.password

            # Run games for this provider
            game_page.GamesbtnClick(provider_name)
