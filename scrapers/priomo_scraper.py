from scrapers.base_scraper import NextPageButtonScraper


class PrimoScraper(NextPageButtonScraper):
    async def parse_product(self, product_url: str, brand: str):
        pass

