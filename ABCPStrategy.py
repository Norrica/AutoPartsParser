#!/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio
import base64
import json
import os.path
import random
import time

from bs4 import BeautifulSoup
from pyppeteer.element_handle import ElementHandle
from pyppeteer.page import Page
from pyppeteer_stealth import stealth
from solvecaptcha import Solvecaptcha
from dotenv import load_dotenv

from browser_manager import BrowserManager

load_dotenv()

solver = Solvecaptcha(os.environ.get('CAPTCHA_API_TOKEN'))


async def type_random_delay(text_field: ElementHandle, text, min, max):
    '''
    Время задержки указывается в секундах, может быть float
    :param text_field: Поле куда вводится текст
    :param text: Текст
    :param min: Минимальное время задержки
    :param max: Максимальное время задержки
    :return: None
    '''
    for letter in text:
        await text_field.type(letter)
        await asyncio.sleep(random.uniform(min, max))


class ABCPStrategy:
    def __init__(self, manager, articles:list[str]):
        self._browser_manager: BrowserManager = manager
        self._domain: str = None
        self._current_page: Page = None
        self._items = articles

    def create_folder(self):
        self._folder = self._domain.split('//')[1]
        if not os.path.exists('./' + self._folder):
            os.mkdir('./' + self._folder)

    @property
    async def domain(self):
        return self._domain

    @domain.setter
    async def domain(self, page):
        self._domain = page

    async def parse_all(self):
        browser_parser = await self._browser_manager.start_parsing()
        self._current_page = await browser_parser.newPage()
        await stealth(self._current_page)
        for i in self._items:
            split = i.split()
            part_n, brand = split[0], ' '.join(split[1:])
            await self._current_page.goto(f'{self._domain}/search/{brand}/{part_n}',
                                          {'waitUntil': 'networkidle0'})
            if await self.check_for_captcha():
                print("captcha", end=' ')
                await self.solve_captcha(self._current_page)
            print('parsing ', self._domain + '/search' + '/' + brand + '/' + part_n, end=' ')
            await self.parse(self._current_page)
            print('done parsing')

    async def check_for_captcha(self):
        return 'captchaImg' in await self._current_page.content()

    async def solve_captcha(self, curr_page: Page):
        # Другой способ, через canvas
        # base64_image = await curr_page.Jeval(
        #     "img.captchaImg",
        #     """img => {
        #         const canvas = document.createElement('canvas');
        #         canvas.width = img.naturalWidth;
        #         canvas.height = img.naturalHeight;
        #         canvas.getContext('2d').drawImage(img, 0, 0);
        #         return canvas.toDataURL('image/png').split(',')[1];
        #     }"""
        # )
        while await self.check_for_captcha():
            element = await curr_page.querySelector("img.captchaImg")
            png_bytes = await element.screenshot()
            base64_image = base64.b64encode(png_bytes).decode("utf-8")
            t0 = time.perf_counter()
            result = solver.normal(
                base64_image,
                numeric=1,
                minLen=4,
                maxLen=4,
            )['code']
            t1 = time.perf_counter() - t0
            print(result, f'{t1} seconds')
            text_field = await curr_page.querySelector("#captchaSubmitInput")
            await type_random_delay(text_field, result, 0.3, 1)
            submit_btn = await curr_page.querySelector("#captchaSubmitBtn")
            await asyncio.sleep(random.uniform(0.6, 1.4))
            await submit_btn.click()
            await curr_page.waitForNavigation()

    async def parse(self, page: Page):
        soup = BeautifulSoup(await page.content(), "html.parser")
        items = []
        for row in soup.select("tr[data-current-brand-number]"):
            delivery_min = int(row.get("data-deadline", 0))
            delivery_max = int(row.get("data-deadline-max", 0))
            style = row.get("style", "").lower()
            in_stock = (delivery_min == 0 or "#09f46d" in style)
            item = {
                "brand": row.select_one(".resultBrand").get_text(strip=True),
                "description": row.select_one(".resultDescription").get_text(strip=True),
                "price": float(row.get("data-output-price", 0)),
                "delivery_min_hours": delivery_min,
                "delivery_max_hours": delivery_max,
                "in_stock": in_stock,
            }

            items.append(item)
            items = sorted(items, key=lambda e: e['price'])
        title = await self._current_page.title()
        fullpath = os.path.join(self._folder,f'{self._domain}.{title}.json')
        with open(fullpath, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False)
