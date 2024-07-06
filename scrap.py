import requests
from bs4 import BeautifulSoup
import os
import json
from typing import List
from models import ScrapingSettings
from retrying import retry


class Scraper:
    def __init__(self, settings: ScrapingSettings):
        self.base_url = "https://dentalstall.com/shop"
        self.settings = settings
        self.products = []

    @retry(wait_fixed=2000, stop_max_attempt_number=3)
    def fetch_page(self, url: str):
        proxies = (
            {"http": self.settings.proxy, "https": self.settings.proxy}
            if self.settings and self.settings.proxy
            else None
        )
        response = requests.get(url, proxies=proxies)
        response.raise_for_status()  # Will retry on HTTP errors
        return response.text

    def get_max_no_of_pages(self, html: str):
        # Locate the pagination section and find the maximum number of pages
        pagination = BeautifulSoup(html, "html.parser").find(
            "ul", class_="page-numbers"
        )
        if not pagination:
            print("Pagination not found")
            return 1  # Assuming there is at least one page if no pagination is found
        pages = pagination.find_all("a", class_="page-numbers")
        return int(pages[-2].text) if len(pages) > 2 else len(pages)

    def parse_products(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        products = soup.find_all("div", class_="product-inner")
        for product in products:
            try:
                name = product.find("h2", class_="woo-loop-product__title").text.strip()
            except AttributeError:
                name = ""
            try:
                price = (
                    float(
                        product.find("span", class_="woocommerce-Price-amount")
                        .text.strip()
                        .replace("₹", "")
                        .replace(",", "")
                    )
                    if product.find("span", class_="woocommerce-Price-amount")
                    else ""
                )
            except AttributeError:
                price = ""
            try:
                image = (
                    product.find("img", class_="attachment-woocommerce_thumbnail")[
                        "data-lazy-src"
                    ]
                    if product.find("img", class_="attachment-woocommerce_thumbnail")
                    else ""
                )
            except AttributeError:
                image = ""
            self.products.append(
                {
                    "product_title": name,
                    "product_price": price,
                    "path_to_image": self.download_image(image) if image else "",
                }
            )

    def download_image(self, url: str) -> str:
        response = requests.get(url)
        filename = os.path.basename(url)
        filepath = os.path.join("images", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(response.content)
        return filepath

    def scrape(self):
        max_pages = (
            self.settings.pages_limit
            if self.settings and self.settings.pages_limit
            else self.get_max_no_of_pages(self.fetch_page(self.base_url))
        )
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/page/{str(page)}/" if page > 1 else self.base_url
            print(f"starting scrapping url - {url}")
            html = self.fetch_page(url)
            self.parse_products(html)

    def save_to_json(self):
        with open("products.json", "w") as f:
            json.dump(self.products, f, indent=4)

    def notify(self):
        print(f"{len(self.products)} products were scraped and saved.")
