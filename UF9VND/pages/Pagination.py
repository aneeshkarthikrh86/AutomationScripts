from tests.base_page import BaseClass
import time

class pagination_loop():
    def click_page_number(page, target_page):
        """Clicks a page number button by its visible text."""
        Total_Pages = page.query_selector_all("//div[@class='p-holder admin-pagination']/button[not(contains(@class,'p-next')) and not(contains(@class,'p-prev'))]")
        for page_btn in Total_Pages:
            if page_btn.text_content().strip() == str(target_page):
                page_btn.scroll_into_view_if_needed()
                page_btn.click()
                return True
        return False 
     
    def pagination_click(self, page):
        Total_Pages = page.query_selector_all("//div[@class='p-holder admin-pagination']/button[not(contains(@class,'p-next')) and not(contains(@class,'p-prev'))]")
        time.sleep(5)
        last_page_num = int(Total_Pages[-1].text_content())
        print(f"Last page num is: {last_page_num}")
        time.sleep(5)
        current_page_num = 1
        while current_page_num <= last_page_num:
            print(f"Now i am in :{current_page_num}")
            
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(3)
            next_page = current_page_num + 1
            
            if self.click_page_number (page, next_page):
                time.sleep(3)
                current_page_num = next_page
                
            else:
                Total_Pages = page.query_selector_all("//div[@class='p-holder admin-pagination']/button[not(contains(@class,'p-next')) and not(contains(@class,'p-prev'))]")
                anchor_page = int(Total_Pages[2].text_content())
                self.click_page_number(page, anchor_page)
                time.sleep(3)

# from playwright.sync_api import sync_playwright
# import time

# def click_page_number(page, target_page):
#     """Clicks a page number button by its visible text."""
#     Total_Pages = page.query_selector_all("//div[@class='p-holder admin-pagination']/button[not(contains(@class,'p-next')) and not(contains(@class,'p-prev'))]")
#     for page_btn in Total_Pages:
#         if page_btn.text_content().strip() == str(target_page):
#             page_btn.scroll_into_view_if_needed()
#             page_btn.click()
#             return True
#     return False    
    

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)  # visible browser
#     context = browser.new_context()
#     page = context.new_page()
    
#     page.goto("https://www.uf-9.com/en-th")
#     time.sleep(5)
#     Total_Pages = page.query_selector_all("//div[@class='p-holder admin-pagination']/button[not(contains(@class,'p-next')) and not(contains(@class,'p-prev'))]")
#     time.sleep(5)
#     last_page_num = int(Total_Pages[-1].text_content())
#     print(f"Last page num is: {last_page_num}")
#     time.sleep(5)
#     current_page_num = 1
#     while current_page_num <= last_page_num:
#         print(f"Now i am in :{current_page_num}")
        
#         page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
#         time.sleep(3)
#         next_page = current_page_num + 1
        
#         if click_page_number (page, next_page):
#             time.sleep(3)
#             current_page_num = next_page
            
#         else:
#           Total_Pages = page.query_selector_all("//div[@class='p-holder admin-pagination']/button[not(contains(@class,'p-next')) and not(contains(@class,'p-prev'))]")
#           anchor_page = int(Total_Pages[2].text_content())
#           click_page_number(page, anchor_page)
#           time.sleep(3)
    

