import time
from tests.base_page import BaseClass
from pages.game_page import Game_Click

class FishProvider(BaseClass):
    def List_Provisers(self):
        time.sleep(1)
        Provider_btns = self.page.query_selector_all("//div[@class='mt-5 flex items-center slot_btn_container w-full overflow-auto light-scrollbar-h pb-[10px]']//button")
        total_providers = len(Provider_btns)
        for indexp in range(1, total_providers):
            Provider_btns = self.page.query_selector_all("//div[@class='mt-5 flex items-center slot_btn_container w-full overflow-auto light-scrollbar-h pb-[10px]']//button")
            Provider_btn = Provider_btns[indexp]
            provider_name = Provider_btn.text_content().strip()
            Provider_btn.scroll_into_view_if_needed()
            Provider_btn.click()
            print(f"Provider: {provider_name}")
            time.sleep(1)
            
            game_page = Game_Click()
            game_page.page = self.page
            game_page.GamesbtnClick()