from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page

CHROME_PATH = 'C:\Program Files\Google\Chrome\Application\chrome.exe'

usr_agent = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
}


class BrowserManager():
    def __init__(self):
        self.browser_parser:Browser = None
        self.captcha_browser = None
        self._cookies = None

    async def start_parsing(self) -> Browser:
        self.browser_parser = await launch(executablePath=CHROME_PATH, headless=True)
        return self.browser_parser

    async def start_captcha(self) -> Browser:
        self.captcha_browser = await launch(executablePath=CHROME_PATH, headless=False)
        return self.captcha_browser

    async def save_cookies(self,page:Page):
        self._cookies = await page.cookies()
        return self._cookies

    def restore_cookies(self):
        return self._cookies
