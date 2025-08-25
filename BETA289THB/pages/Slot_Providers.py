import time
from tests.base_page import BaseClass
from pages.game_page import Game_Click
from pages.recovery_helper import RecoveryHelper   # ✅ import

class SlotProvider:
    def __init__(self, page, context, baseUrl=None, username=None, password=None):
        self.page = page
        self.context = context
        self.baseUrl = baseUrl
        self.username = username
        self.password = password
        self.recovery = RecoveryHelper(page, context, baseUrl, username, password)   # ✅ recovery helper

    def List_Provisers(self):
        """Loop through all providers and run their games."""
        provider_xpath = (
            "//div[@class='mt-5 flex items-center slot_btn_container "
            "w-full overflow-auto light-scrollbar-h pb-[10px]']//button"
        )
        total_providers = len(self.page.query_selector_all(provider_xpath))

        for indexp in range(1, total_providers):  # skipping 0 if that's 'All'
            # refresh provider buttons every loop (to avoid stale handles)
            Provider_btns = self.page.query_selector_all(provider_xpath)
            Provider_btn = Provider_btns[indexp]

            provider_name = Provider_btn.text_content().strip()
            print(f"🎰 Provider: {provider_name}")

            # make sure visible & in view before click
            Provider_btn.scroll_into_view_if_needed()
            self.page.wait_for_timeout(300)  # tiny wait
            Provider_btn.click()

            # Create game page handler with shared context + recovery
            game_page = Game_Click(self.page, self.context)   # ✅ constructor only takes page + context
            game_page.recovery = self.recovery                # ✅ attach recovery manually
            game_page.baseUrl = self.baseUrl
            game_page.username = self.username
            game_page.password = self.password

            # Run games for this provider
            game_page.GamesbtnClick(provider_name)
