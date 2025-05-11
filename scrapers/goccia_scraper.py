import json

from crawl4ai import CrawlerRunConfig, CacheMode

from scrapers.base_scraper import NextPageButtonScraper
from my_utils import FallbackJsonCssExtractionStrategy


class GocciaScraper(NextPageButtonScraper):
    async def parse_product(self, product_url: str, brand: str):
        """Parse product page and extract product details"""

        await super().parse_product(product_url, brand)

        # Extract product details
        product_schema = self.schema['product_page_schema']
        results = await self.crawler.arun(
            url=product_url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=FallbackJsonCssExtractionStrategy(schema=product_schema),
                markdown_generator=self.md_generator
            )
        )

        # Extract Main Product
        product = json.loads(results.extracted_content)
        product[0]['ProductURL'] = product_url
        product[0]['markdown'] = results.markdown.fit_markdown

        self._save_product(product)