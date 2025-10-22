"""
Core scraper engine with Playwright and async support.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from utils.logger import get_logger

logger = get_logger(__name__)


class ProductScraper(ABC):
    """
    Abstract base class for product scrapers.

    Subclasses must implement the scrape_product method to define
    how to extract product data from a specific website.
    """

    @abstractmethod
    async def scrape_product(self, page: Page, url: str, product_id: int) -> Dict[str, Any]:
        """
        Scrape a single product from the given URL.

        Args:
            page: Playwright Page instance
            url: URL to scrape
            product_id: Unique identifier for the product

        Returns:
            Dictionary containing product data

        Raises:
            Exception: If scraping fails
        """
        pass

    @abstractmethod
    def get_product_urls(self) -> List[str]:
        """
        Get list of product URLs to scrape.

        Returns:
            List of URLs to scrape
        """
        pass


class ScraperEngine:
    """
    Main scraper engine managing concurrent scraping with Playwright.

    This class handles:
    - Browser initialization and cleanup
    - Concurrent task execution with semaphore control
    - Error handling and retry logic
    - Memory-efficient browser context management

    Attributes:
        max_concurrent: Maximum number of concurrent scraping tasks
        headless: Whether to run browser in headless mode
        timeout: Default timeout for page operations (ms)
    """

    def __init__(
        self,
        max_concurrent: int = 10,
        headless: bool = True,
        timeout: int = 30000
    ):
        """
        Initialize the scraper engine.

        Args:
            max_concurrent: Maximum concurrent tasks (default: 10)
            headless: Run browser in headless mode (default: True)
            timeout: Page operation timeout in ms (default: 30000)
        """
        self.max_concurrent = max_concurrent
        self.headless = headless
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.browser: Optional[Browser] = None
        logger.info(
            f"ScraperEngine initialized: max_concurrent={max_concurrent}, "
            f"headless={headless}, timeout={timeout}ms"
        )

    async def _init_browser(self, playwright) -> Browser:
        """
        Initialize Playwright browser.

        Args:
            playwright: Playwright instance

        Returns:
            Browser instance
        """
        logger.info("Launching browser...")
        browser = await playwright.chromium.launch(headless=self.headless)
        logger.info("Browser launched successfully")
        return browser

    async def _scrape_single_product(
        self,
        context: BrowserContext,
        scraper: ProductScraper,
        url: str,
        product_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape a single product with error handling.

        Args:
            context: Browser context
            scraper: ProductScraper instance
            url: Product URL
            product_id: Product ID

        Returns:
            Product data dict or None if failed
        """
        async with self.semaphore:
            page = None
            try:
                page = await context.new_page()
                page.set_default_timeout(self.timeout)

                logger.info(f"[ID:{product_id}] Scraping {url}")
                product_data = await scraper.scrape_product(page, url, product_id)

                logger.info(f"[ID:{product_id}] Successfully scraped: {product_data.get('name', 'Unknown')}")
                return product_data

            except Exception as e:
                logger.error(f"[ID:{product_id}] Failed to scrape {url}: {str(e)}")
                return None

            finally:
                if page:
                    await page.close()

    async def scrape_all(self, scraper: ProductScraper) -> List[Dict[str, Any]]:
        """
        Scrape all products using the provided scraper.

        Args:
            scraper: ProductScraper implementation

        Returns:
            List of scraped product dictionaries

        Example:
            >>> engine = ScraperEngine(max_concurrent=10)
            >>> scraper = MyCustomScraper()
            >>> products = await engine.scrape_all(scraper)
        """
        urls = scraper.get_product_urls()
        total_urls = len(urls)
        logger.info(f"Starting scrape of {total_urls} products")

        async with async_playwright() as playwright:
            browser = await self._init_browser(playwright)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )

            try:
                # Create tasks for concurrent scraping
                tasks = [
                    self._scrape_single_product(context, scraper, url, idx + 1)
                    for idx, url in enumerate(urls)
                ]

                # Execute all tasks concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Filter out None values and exceptions
                products = [
                    result for result in results
                    if result is not None and not isinstance(result, Exception)
                ]

                logger.info(f"Scraping completed: {len(products)}/{total_urls} successful")
                return products

            finally:
                await context.close()
                await browser.close()
                logger.info("Browser closed")

    async def scrape_batch(
        self,
        scraper: ProductScraper,
        urls: List[str],
        start_id: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Scrape a specific batch of URLs.

        Args:
            scraper: ProductScraper implementation
            urls: List of URLs to scrape
            start_id: Starting ID for products (default: 1)

        Returns:
            List of scraped product dictionaries
        """
        logger.info(f"Starting batch scrape of {len(urls)} products")

        async with async_playwright() as playwright:
            browser = await self._init_browser(playwright)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )

            try:
                tasks = [
                    self._scrape_single_product(context, scraper, url, start_id + idx)
                    for idx, url in enumerate(urls)
                ]

                results = await asyncio.gather(*tasks, return_exceptions=True)

                products = [
                    result for result in results
                    if result is not None and not isinstance(result, Exception)
                ]

                logger.info(f"Batch scraping completed: {len(products)}/{len(urls)} successful")
                return products

            finally:
                await context.close()
                await browser.close()
