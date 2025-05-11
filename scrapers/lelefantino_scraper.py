from urllib.parse import urljoin

from scrapers.base_scraper import LoadMoreScraper
import json
from crawl4ai import CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

class LelefantinoScraper(LoadMoreScraper):
    async def parse_product(self, product_url: str, brand: str):
        """Parse product page and extract product details"""
        await super().parse_product(product_url, brand)
        # Extract product details
        product_schema = self.schema['product_page_schema']
        result = await self.crawler.arun(
            url=product_url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=JsonCssExtractionStrategy(schema=product_schema),
                markdown_generator=self.md_generator
            ),
        )
        # Extract Main Product
        product = json.loads(result.extracted_content)
        product[0]['markdown'] = result.markdown.fit_markdown
        product[0]['ProductURL'] = product_url


        # Extract other Colors urls
        other_colors_urls = [urljoin(self.config['base_url'], color["ColorURL"]) for product_item in product for
                             color in product_item['OtherColorsURLs']]

        if other_colors_urls:
            # Extract other colors
            color_response = await self.crawler.arun_many(
                urls=other_colors_urls,
                config=CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    extraction_strategy=JsonCssExtractionStrategy(schema=product_schema),
                    markdown_generator=self.md_generator
                ),
            )
            for result, product_url in zip(color_response, other_colors_urls):
                color_product = json.loads(result.extracted_content)
                color_product[0]['markdown'] = result.markdown.fit_markdown
                product.extend(color_product)
        self._save_product(product)


