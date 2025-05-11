import json

from crawl4ai import CrawlerRunConfig, CacheMode,JsonCssExtractionStrategy
import re
from scrapers.base_scraper import NextPageButtonScraper


class CoolcultureScraper(NextPageButtonScraper):
    async def parse_product(self, product_url: str, brand: str):
        """Parse product page and extract product details"""

        await super().parse_product(product_url, brand)

        # Extract product details
        product_schema = self.schema['product_page_schema']
        results = await self.crawler.arun(
            url=product_url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=JsonCssExtractionStrategy(schema=product_schema),
                markdown_generator=self.md_generator
            )
        )

        # Extract Main Product
        product = json.loads(results.extracted_content)
        product[0]['ProductURL'] = product_url
        product[0]['markdown'] = results.markdown.fit_markdown

        # Clean Product Data
        product[0] = self.clean_product_data(product[0])

        self._save_product(product)

    def clean_product_data(self, product):
        """Clean product data"""
        # Implement cleaning logic here
        # Example: Remove unwanted keys or format values
        product['ProductColor'] = product['ProductColor'].replace('Color:', '').replace(":","").strip()
        product['CurrentPrice'] = float(re.search(r'[\d,]+', product['CurrentPrice']).group().replace(',', ''))
        product['OldPrice'] = float(re.search(r'[\d,]+', product['OldPrice']).group().replace(',', ''))
        product['AvailableSizes'] = [d.get('Size') for d in product['AvailableSizes'] if d]
        product['Collection'] = product['Collection'].split(":")[-1].strip() if product['Collection'] else None
        return product