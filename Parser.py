#!/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio
import datetime
import os
from ftplib import FTP, error_perm

import ftp_stuff
from AEXCStrategy import ABCPStrategy, AEXCStrategy
from STPartsStrategy import STPartsStrategy
from browser_manager import BrowserManager


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


def get_ftp() -> FTP:
    ftp = FTP()
    host = os.environ.get('FTP_IP')
    ftp.connect(host, int(os.environ.get('FTP_PORT')))
    ftp.login(os.environ.get("FTP_LOGIN"),
              os.environ.get("FTP_PWD"))
    return ftp


async def main():
    ftp = get_ftp()
    while True:
        hour = datetime.datetime.now().hour
        if 10 < hour < 20:
            try:
                articules = ftp_stuff.get_articules(ftp)
                await asyncio.sleep(2)
            except error_perm:
                # print('got error 502')
                await asyncio.sleep(3)
                # await asyncio.sleep(60*15)
                continue
            except EOFError:
                print('got error EOFError')
                await asyncio.sleep(3)
                ftp = get_ftp()
                continue
            print(f'start parsing at {datetime.datetime.now()}')
            manager = BrowserManager()
            p2 = Parser(STPartsStrategy(manager, articules, ftp))
            await p2.parse()
            p = Parser(AEXCStrategy(manager, articules, ftp))
            await p.parse()
            print(f'done all sites at {datetime.datetime.now()}')
            # ftp.delete('From_1C.csv')
            break
    ftp.quit()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
