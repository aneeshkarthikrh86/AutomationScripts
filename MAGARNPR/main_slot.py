import os
from dotenv import load_dotenv
from pages.login_page import Login
from pages.home_page import HomePage
from pages.Slot_Providers import SlotProvider

load_dotenv(override=True)

BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

if __name__ == "__main__":
    # Step 1: Start browser and login
    login_page = Login(BASE_URL)
    login_page.Start_Browser()
    login_page.launch_url()
    print(f"USERNAME from env: {USERNAME!r}")
    login_page.login(USERNAME, PASSWORD)
    login_page.Close_Popupbtnscal()

    # Step 2: Navigate to Slots
    home_page = HomePage()
    home_page.page = login_page.page  # reuse same page
    home_page.click_Slot()
    home_page.home_slot()

    # Step 3: Provider + Game testing
    slot_providers = SlotProvider(
        login_page.page,
        login_page.context,
        baseUrl=BASE_URL,
        username=USERNAME,
        password=PASSWORD,
    )

    # Run provider → games flow
    slot_providers.List_Provisers()

    # Step 4: Close browser
    login_page.close_Browser()
