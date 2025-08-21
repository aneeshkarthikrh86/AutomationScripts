# /utils/helpers.py
async def clear_browser_storage(context):
    await context.clear_cookies()
    await context.clear_permissions()
    for page in context.pages:
        await page.goto("about:blank")
        await page.evaluate("window.localStorage.clear(); window.sessionStorage.clear();")
