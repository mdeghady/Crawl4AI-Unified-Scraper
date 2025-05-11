import logging
from logging.handlers import RotatingFileHandler
import os
import argparse
import json
from datetime import datetime
import asyncio

from crawl4ai import AsyncWebCrawler
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from importlib import import_module
from typing import Type

from scrapers.base_scraper import BaseScraper


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Web scraper for e-commerce websites')

    # Website selection arguments
    parser.add_argument('--website', type=str, help='Names of websites to scrape')
    parser.add_argument('--config', type=str, default='configs/websites.json', help='Path to the\
                        configuration file default: configs/websites.json')

    # Output control
    parser.add_argument('--output-dir', type=str, default='output', help='Directory to save output files')
    parser.add_argument('--log-dir', type=str, default='logs', help='Directory to save log files')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO', help='Set the logging level')

    # Behavior flags
    parser.add_argument('--list-websites', action='store_true', help='List available websites and exit')

    return parser.parse_args()

def setup_logging(args):
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, args.log_level))

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Create file handler with rotation (10 files of 1MB each)
    log_file = f"logs/scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024,
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

def get_scraper_class(scraper_name: str) -> Type[BaseScraper]:
    """Dynamically import and return the scraper class"""
    try:
        module = import_module('scrapers')
        scraper_class = getattr(module, scraper_name)
        if not issubclass(scraper_class, BaseScraper):
            raise ValueError(f"{scraper_name} is not a valid scraper class")
        return scraper_class
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Could not find scraper class {scraper_name}: {str(e)}")

async def main():
    # Parse command line arguments
    args = parse_arguments()

    # Setup logging
    logger = setup_logging(args)
    logger.info(f"Starting web scraping process for {args.website}")

    try:
        # Load configuration
        with open(args.config) as f:
            websites = json.load(f)
            logger.debug("Loaded website configurations")
        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)
        # Create a markdown generator
        # Step 1: Create a pruning filter
        prune_filter = PruningContentFilter(
            # Lower → more content retained, higher → more content pruned
            threshold=0.8,
            # "fixed" or "dynamic"
            threshold_type="dynamic",
            # Ignore nodes with <3 words
            min_word_threshold=0
        )

        # Step 2: Insert it into a Markdown Generator
        md_generator = DefaultMarkdownGenerator(content_filter=prune_filter,
                                                options={
                                                    "ignore_links": True,
                                                    "escape_html": False,
                                                    "body_width": 80,
                                                    "skip_internal_links": True,
                                                    "include_sup_sub": True
                                                })

        # Step 3: Initialize a scraper instance
        website_to_scrape = args.website
        website_config = websites[website_to_scrape]
        async with AsyncWebCrawler() as crawler:
            scraper_instance = get_scraper_class(website_config['scraper_class'])(website_config ,
                                                                                  crawler,
                                                                                  md_generator,
                                                                                  website_to_scrape,)
            # Run the scraper
            website_products = await scraper_instance.run()

            # Save the scraped data
            output_file = os.path.join(args.output_dir, f"{website_to_scrape}_products.json")
            try:
                scraper_instance._save_json(website_products, output_file)
            except Exception as e:
                logger.error(f"Failed to save scraped data for {website_to_scrape} to {output_file} due to {str(e)}")
                return

    except FileNotFoundError:
        logger.error(f"Configuration file not found: {args.config}")
        return
    except Exception as e:
        logger.critical(f"Fatal error in main scraping process: {str(e)}", exc_info=True)
        return



    logger.info("Scraping completed.")

if __name__ == "__main__":
    asyncio.run(main())