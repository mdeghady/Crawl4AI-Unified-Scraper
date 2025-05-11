from scrapers.base_scraper import InfiniteScrollScraper


class BananabenzScraper(InfiniteScrollScraper):
    async def parse_product(self, product_url: str, brand: str):
        pass