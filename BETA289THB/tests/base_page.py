from playwright.sync_api import sync_playwright
import time

# tests/base_page.py
class BaseClass:
    def __init__(self, baseUrl=None):
        self.baseUrl = baseUrl
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def Start_Browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False, args=["--start-maximized"])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()
        print("🌐 Browser started (maximized)")

    def launch_url(self):
        self.page.goto(self.baseUrl, wait_until="networkidle")
        print(f"🚀 Launched URL: {self.baseUrl}")

    def close_Browser(self):
        self.browser.close()
        self.playwright.stop()
        print("🛑 Browser closed")
        