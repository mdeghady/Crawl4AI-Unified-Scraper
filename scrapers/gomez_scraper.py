import json

from crawl4ai import CrawlerRunConfig, CacheMode, JsonCssExtractionStrategy

from scrapers.base_scraper import NextPageButtonScraper
from my_utils import DataCleasnerUtils


class GomezScraper(NextPageButtonScraper , DataCleasnerUtils):
    async def parse_product(self, product_url: str, brand: str):
        """Parse product page and extract product details"""
        await super().parse_product(product_url, brand)

        # Extract product details
        product_schema = self.schema['product_page_schema']
        results = await self.crawler.arun(
            url=product_url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=JsonCssExtractionStrategy(schema=product_schema)
            )
        )

        # Extract Main Product
        product = json.loads(results.extracted_content)
        product[0]['ProductURL'] = product_url

        # Clan Price Data
        product[0]["PriceCurrency"] = self._convert_currency_symbos_to_code(product[0]["CurrentPrice"])
        product[0]['CurrentPrice'] = self.convert_price_to_float(product[0]['CurrentPrice'], ',')

        if not product[0]['OriginalPrice']:
            product[0]['OriginalPrice'] = product[0]['CurrentPrice']
        else:
            product[0]['OriginalPrice'] = self.convert_price_to_float(product[0]['OriginalPrice'], ',')

        # Clean Sizes
        if product[0]['AvailableSizes']:
            product[0]['AvailableSizes'] = self.flatten_list_of_dicts(product[0]['AvailableSizes'], 'Size')
        else:
            product[0]['AvailableSizes'] = []

        # self._save_product(product)
        self.dal.add_product(product[0])

