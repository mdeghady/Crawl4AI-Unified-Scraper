from scrapers.base_scraper import NextPageButtonScraper
import json
from crawl4ai import CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from my_utils import FallbackJsonCssExtractionStrategy
import re

class WardowScraper(NextPageButtonScraper):
    async def parse_product(self, product_url: str, brand: str):
        """Parse product page and extract product details"""
        await super().parse_product(product_url, brand)
        # Extract product details
        product_schema = self.schema['product_page_schema']
        main_color = await self.crawler.arun(
            url=product_url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=FallbackJsonCssExtractionStrategy(schema=product_schema),
                markdown_generator=self.md_generator
            )
        )

        product = json.loads(main_color.extracted_content)
        product[0]['ProductURL'] = product_url
        product[0]['markdown'] = main_color.markdown.fit_markdown


        self.logger.debug(f"Successfully loaded main color for : {product_url}")


        # Extract other Colors urls
        other_colors_urls = [color.get("ColorURL")  for product_item in product for
                             color in product_item.get('OtherColorsURLs') if color.get("ColorURL")]


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
                color_product[0]['ProductURL'] = product_url
                color_product[0]['markdown'] = result.markdown.fit_markdown
                product.extend(color_product)

        # Clean Product Data
        for i in range(len(product)):
            product[i] = self.clean_product_data(product[i])

        # Save product data
        self.dal.save_product(product)

    def clean_product_data(self, product):
        """Clean product data"""
        # Remove unwanted keys
        product.pop('OtherColorsURLs', None)
        # Flatten the list of dictionaries
        product['DescriptionInside'] = [item.get('feature') for item in product['DescriptionInside'] if item]
        product['DescriptionGeneral'] = [item.get('feature') for item in product['DescriptionGeneral'] if item]
        product['ProductDetails'] = [item.get('feature') for item in product['ProductDetails'] if item]

        product['OriginalPrice'] = float(re.search(r'[\d,]+', product['OriginalPrice']).group().replace(',', ''))
        product['CurrentPrice'] = float(re.search(r'[\d,]+', product['CurrentPrice']).group().replace(',', ''))
        return product