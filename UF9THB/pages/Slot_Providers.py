import time
from pages.game_page import Game_Click

class SlotProvider:
    def __init__(self, page=None, context=None, baseUrl=None, username=None, password=None):
        self.page = page
        self.context = context
        self.baseUrl = baseUrl
        self.username = username
        self.password = password

    def list_providers(self):
        """Iterate through all slot providers and run games for each."""
        provider_xpath = "//div[@class='mt-5 flex items-center slot_btn_container w-full overflow-auto light-scrollbar-h pb-[10px]']//button"
        total_providers = len(self.page.query_selector_all(provider_xpath))

        for index in range(1, total_providers):  # skip 0 if 'All'
            # Refresh buttons to avoid stale element
            provider_buttons = self.page.query_selector_all(provider_xpath)
            provider_btn = provider_buttons[index]
            provider_name = provider_btn.text_content().strip()
            print(f"Provider: {provider_name}")

            # Scroll into view and click
            provider_btn.scroll_into_view_if_needed()
            self.page.wait_for_timeout(300)
            provider_btn.click()

            # Initialize game page handler
            game_page = Game_Click()
            game_page.page = self.page
            game_page.context = self.context
            game_page.baseUrl = self.baseUrl
            game_page.username = self.username
            game_page.password = self.password

            # Run games for this provider
            game_page.GamesbtnClick(provider_name)
