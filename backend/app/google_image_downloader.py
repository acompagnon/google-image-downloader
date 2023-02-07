# -*- coding: utf-8 -*-
# !/usr/bin/python3

import base64
import argparse
import traceback
from time import sleep
from pathlib import Path
from typing import Dict, Any, Iterator, Tuple
from mimetypes import guess_extension, guess_type

import requests
import playwright
from bs4 import BeautifulSoup
from magic import from_buffer
from fake_headers import Headers
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

try:
    from logger import Logger
except ModuleNotFoundError:
    from app.logger import Logger


class GoogleImageDownloader:
    def __init__(
        self, output_path: str, proxy: Dict[str, Any] = None, headless: bool = True
    ):

        self._browser: playwright.sync_api._generated.Browser = None
        self._current_page: playwright.sync_api._generated.Page = None

        self.proxy = {"server": proxy} if proxy else None
        self.headless = headless

        self.session = requests.Session()
        self.session.headers = Headers().generate()
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}

        self.output_path = output_path

    def set_new_playwright(
        self,
        playwright: playwright.sync_api.Playwright,
    ) -> None:
        """Open a new playwright"""

        Logger.info(f"set_new_playwright(): Initialize")
        if self.proxy:
            Logger.info(f"set_new_playwright(): Used proxy {self.proxy}")

        self._browser = playwright.chromium.launch(
            headless=self.headless,
            args=["--no-sandbox"],
            proxy=self.proxy,
        )
        self._current_page = self._browser.new_page()

    def close_playwright(self) -> None:
        """Close current playwright"""

        if self._browser is not None:
            self._current_page.close()
            self._browser.close()

    def _detect_image_selector(self) -> str:
        Logger.info(f"_detect_image_selector(): Retrieving image preview div")

        layout = self._current_page.content()
        soup = BeautifulSoup(layout, "html.parser")

        images = soup.findAll("img", alt=True)
        images = [
            image
            for image in images
            if image.attrs.get("alt", "") and image.attrs.get("class", "")
        ]

        # Open image preview
        selector = f"img[alt=\"{images[1].attrs.get('alt')}\"]"
        self._current_page.click(selector)

        # Wait for preview
        sleep(1)

        layout = self._current_page.content()
        soup = BeautifulSoup(layout, "html.parser")
        preview_link = soup.find("a", {"target": "_blank", "role": "link"})
        preview_parent = preview_link.parent if preview_link else None
        if not preview_parent or not preview_parent.attrs.get("class", []):
            Logger.critical(
                f"_detect_image_selector(): Could not find selector, please open an issue"
            )
            return ""

        Logger.info(
            f'_detect_image_selector(): Done : {preview_parent.attrs["class"][0]}'
        )
        return preview_parent.attrs["class"][0]

    def _navigate(self, url: str) -> bool:
        try:
            if self._current_page is None:
                self._current_page = self._browser.new_page()

            Logger.info(f"_navigate(): Loading {url}")
            self._current_page.goto(url, timeout=60000)
            Logger.info(f"_navigate(): OK")
        except (PlaywrightTimeoutError, Exception) as e:
            Logger.warning(f"_navigate(): Could not load url {url} : {e}")
            Logger.warning(traceback.format_exc())
            return False

        return True

    def download(self, link: str, count: int) -> Tuple[str, bytes]:
        # TODO filenames
        if link.startswith("data"):
            index = link.find("base64,")
            b64_header = link[: index + 7]
            extension = guess_extension(guess_type(b64_header)[0])
            extension = ".jpg" if not extension else extension
            img_data = base64.b64decode(link[index + 7 :])
            img_filename = f"image_{count}{extension}"
            if self.output_path:
                with open(f"{self.output_path}/{img_filename}", "wb") as fp:
                    fp.write(img_data)
            return img_filename, img_data

        try:
            response = self.session.get(link)
        except (
            requests.exceptions.Timeout,
            requests.exceptions.SSLError,
            Exception,
        ) as e:
            Logger.warning(e)
            return None, None

        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if not content_type:
                return None, None
            extension = guess_extension(content_type)
            if not extension:
                mime = from_buffer(response.content, mime=True)
                extension = guess_extension(mime)
            extension = ".jpg" if not extension else extension
            img_filename = f"image_{count}{extension}"
            if self.output_path:
                with open(f"{self.output_path}/{img_filename}", "wb") as fp:
                    fp.write(response.content)
            return img_filename, response.content

        return None, None

    def crawl(self, selector_class: str, limit: int = 10) -> Iterator[str]:
        count = 0

        while True:
            try:
                layout = self._current_page.inner_html(
                    f'div[class="{selector_class}"]', timeout=1000
                )
            except Exception as e:
                Logger.warning(f"crawl(): {e}")
                break
            soup = BeautifulSoup(layout, "html.parser")
            image = soup.find("img")
            Logger.debug(f"image={image}")
            link = image.attrs.get("src", "") if soup else ""
            if not link:
                break
            yield link
            count += 1
            if limit != -1 and count >= limit:
                break
            selector_src = f"img[src=\"{image.attrs.get('src')}\"]"
            try:
                self._current_page.press(selector_src, "ArrowRight")
            except Exception as e:
                Logger.warning(e)
                selector_alt = f"img[alt=\"{image.attrs.get('alt')}\"]"
                self._current_page.press(selector_alt, "ArrowRight")
            sleep(0.1)

    def process(self, search: str = "", limit: int = -1) -> Iterator[bytes]:
        Logger.info(f"process() : search={search}")
        # Load query
        url = f'https://www.google.fr/imghp?hl=en&q={"+".join(search.split(" "))}'
        success = self._navigate(url=url)
        if success is False:
            return

        # Accept conditions
        with self._current_page.expect_navigation():
            self._current_page.click('button:has-text("Accept all")')

        # Launch search
        with self._current_page.expect_navigation():
            self._current_page.click('[aria-label="Google Search"]')

        # Detect div where images will be collected
        selector_class = self._detect_image_selector()
        if not selector_class:
            return

        imgs_src = self.crawl(selector_class=selector_class, limit=limit)
        if imgs_src:
            for i, img_src in enumerate(imgs_src):
                img_filename, img_bytes = self.download(link=img_src, count=i)
                Logger.info(
                    f"process(): {i + 1} images downloaded",
                )
                if img_filename and img_bytes:
                    yield {"filename": img_filename, "data": img_bytes}

        Logger.info(f"process(): Done")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("search_string", help="Google image query (ex: 'flag')")
    parser.add_argument(
        "--limit",
        "-l",
        default=-1,
        type=int,
        help="Images download limit, default None",
    )
    parser.add_argument(
        "--output", "-o", default="./images", type=str, help="Ouptut directory"
    )
    parser.add_argument(
        "--proxy-server",
        default=None,
        type=str,
        help="Proxy server (ex: 'http://myproxy:3128')",
    )
    parser.add_argument(
        "--no-headless",
        help="Display playwright window, this option does not work inside Docker",
        action="store_true",
    )
    parser.add_argument(
        "--verbose", "-v", help="Set Logger level to DEBUG", action="store_true"
    )
    args = parser.parse_args()

    Path(args.output).mkdir(parents=True, exist_ok=True)
    Logger.info(f"main(): Images will be saved in {args.output}")

    downloader = GoogleImageDownloader(
        output_path=args.output,
        proxy=args.proxy_server,
        headless=not args.no_headless,
    )

    try:
        with sync_playwright() as plwght:
            downloader.set_new_playwright(plwght)
            images = downloader.process(search=args.search_string, limit=args.limit)
            if images:
                for _ in images:
                    pass
            downloader.close_playwright()
    except Exception as e:
        Logger.error(f"main(): {e}")
        Logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()
