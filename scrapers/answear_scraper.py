import json
import re
from crawl4ai import CrawlerRunConfig, CacheMode
from scrapers.base_scraper import NextPageButtonScraper
from my_utils import FallbackJsonCssExtractionStrategy

class AnswearScraper(NextPageButtonScraper):
    async def parse_product(self, product_url: str, brand: str):
        """Parse product page and extract product details"""

        await super().parse_product(product_url, brand)

        # JS commands to open the size dropdown
        js_commands = [
        "document.querySelector('div[data-test=\"size_dropdown\"]')?.click()"
        ]

        # Schema for product details extraction
        product_schema = self.schema['product_page_schema']

        # Extract product details
        result = await self.crawler.arun(
            url=product_url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=FallbackJsonCssExtractionStrategy(product_schema),
                js_code=js_commands
            )
        )

        if not result:
            self.logger.warning(f"Failed to extract product details from {product_url}")
            return None
        
        # The JSON output is stored in 'extracted_content'
        data = json.loads(result.extracted_content)
        product = data[0]

        info_data = json.loads(product.pop('info'))
        product['AvailableSizes'] = info_data['size']
        product['category'] = info_data['category']

        if not product['OriginalPrice']:
            product['OriginalPrice'] = product['CurrentPrice']
        
        product['PriceCurrency'] = product['CurrentPrice'].split(" ")[-1]

        product['OriginalPrice'] = float(re.search(r'[\d.]+', product['OriginalPrice']).group())
        product['CurrentPrice'] = float(re.search(r'[\d.]+', product['CurrentPrice']).group())
        product['ProductURL'] = product_url

        self.dal.add_product(product)