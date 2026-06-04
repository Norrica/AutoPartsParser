#!/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio
import base64
import io
import json
import os.path
import random
import time
from ftplib import FTP

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pyppeteer.element_handle import ElementHandle
from pyppeteer.page import Page
from pyppeteer_stealth import stealth
from solvecaptcha import Solvecaptcha

from browser_manager import BrowserManager
import requests_cache

load_dotenv()
requests_cache.install_cache('captcha_cache')

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
    def __init__(self, manager, articles: list[str], ftp: FTP):
        self._browser_manager: BrowserManager = manager
        self._domain: str = None
        self._current_page: Page = None
        self._articles = articles
        self._ftp = ftp
        self.results = []

    def create_folder(self):
        self._folder = self._domain.split('//')[1]

    @property
    async def domain(self):
        return self._domain

    @domain.setter
    async def domain(self, url):
        self._domain = url

    async def parse_all(self):
        browser_parser = await self._browser_manager.start_parsing()
        self._current_page = await browser_parser.newPage()
        await stealth(self._current_page)

        for article in self._articles:
            split = article.split(';')
            part_n, brand = split[0], ' '.join(split[1:])
            await self._current_page.goto(
                f'{self._domain}/search/{brand}/{part_n}',
                {'waitUntil': 'networkidle0'}
            )
            if await self.check_for_captcha(self._current_page):
                print("captcha", end=' ')
                await self.solve_captcha(self._current_page)
            print('parsing ', f'{self._domain}/search/{brand}/{part_n}', end=' ')
            offers = await self.parse(self._current_page)

            self.results.append({
                "article": part_n,
                "source": self._folder,
                "offers": offers
            })

            print('done')

        await self.create_json()
        print(f'json from {self._folder} created')

    async def parse(self, page: Page):
        offers = []
        soup = BeautifulSoup(await page.content(), "html.parser")
        for row in soup.select("tr[data-current-brand-number]"):
            delivery_min = int(row.get("data-deadline", 0))
            delivery_max = int(row.get("data-deadline-max", 0))
            style = row.get("style", "").lower()

            in_stock = (delivery_min == 0 or "#09f46d" in style)

            offers.append({
                "brand": row.select_one(".resultBrand").get_text(strip=True),
                "description": row.select_one(".resultDescription").get_text(strip=True),
                "price": float(row.get("data-output-price", 0)),
                "delivery_min_hours": delivery_min,
                "delivery_max_hours": delivery_max,
                "in_stock": in_stock,
            })

        return sorted(offers, key=lambda e: e["price"])

    async def create_json(self):
        data = json.dumps(
            self.results,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8")
        fb = io.BytesIO(data)
        self._ftp.storbinary(
            f'STOR {self._folder}.json',
            fb
        )

    async def check_for_captcha(self, page):
        return 'captchaImg' in await page.content()

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

