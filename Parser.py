#!/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio
import os
from ftplib import FTP

import ftp_stuff
from AEXCStrategy import ABCPStrategy, AEXCStrategy
from STPartsStrategy import STPartsStrategy
from browser_manager import BrowserManager

USR_AGNT = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
}
CHROME_PATH = 'C:\Program Files\Google\Chrome\Application\chrome.exe'


class Parser:
    def __init__(self, strategy: ABCPStrategy):
        self._strategy = strategy
        self.results = []
        self._strategy.create_folder()

    async def parse(self):
        await self._strategy.parse_all()

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: ABCPStrategy):
        self._strategy = strategy


async def main():
    ftp = FTP()
    host = os.environ.get('FTP_IP')
    ftp.connect(host, int(os.environ.get('FTP_PORT')))
    ftp.login(os.environ.get("FTP_LOGIN"),
              os.environ.get("FTP_PWD"))

    articules = ftp_stuff.get_articules(ftp)
    print(articules)
    manager = BrowserManager()
    p = Parser(AEXCStrategy(manager, articules,ftp))
    await p.parse()
    p2 = Parser(STPartsStrategy(manager, articules,ftp))
    await p2.parse()
    print('all done')
    ftp.quit()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
