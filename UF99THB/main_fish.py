import os
from dotenv import load_dotenv
from pages.login_page import Login
from pages.home_page import HomePage
from pages.Slot_Providers import SlotProvider
from pages.Fishing_Provider import FishProvider
from pages.game_page import Game_Click

load_dotenv(override=True)

BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

if __name__ == "__main__":
    # Step 1: Login Page actions
    login_page = Login(BASE_URL)
    login_page.Start_Browser()
    login_page.launch_url()
    print(f"USERNAME from env: {USERNAME!r}")
    login_page.login(USERNAME, PASSWORD)
    login_page.Close_Popupbtnscal()
    
    # Step 2: Home Page actions
    home_page = HomePage()
    home_page.page = login_page.page  # reuse same page
    home_page.click_Fish()
    home_page.home_slot()
    
    # Step4:- Gameclick close testing
    Fishing_Provider = FishProvider()
    Fishing_Provider.page = login_page.page  # reuse same page
    Fishing_Provider.List_Provisers()
    
    # Step 3: Close browser
    login_page.close_Browser()