"""
Example scraper implementations for different e-commerce sites.

These serve as templates and can be customized for real websites.
"""

from typing import List, Dict, Any
from playwright.async_api import Page
from scraper.core import ProductScraper
from utils.logger import get_logger

logger = get_logger(__name__)


class ExampleMercadoLibreScraper(ProductScraper):
    """
    Example scraper for Mercado Libre-style websites.

    This is a template implementation that demonstrates the scraping pattern.
    For actual implementation, adjust selectors to match the target website.

    Note: This example uses mock data for demonstration purposes.
    Replace with actual Playwright selectors for production use.
    """

    def __init__(self, search_query: str = "smartphone", max_products: int = 10):
        """
        Initialize the scraper.

        Args:
            search_query: Search term for products
            max_products: Maximum number of products to scrape
        """
        self.search_query = search_query
        self.max_products = max_products
        logger.info(f"ExampleMercadoLibreScraper initialized: query='{search_query}', max={max_products}")

    def get_product_urls(self) -> List[str]:
        """
        Get list of product URLs to scrape.

        In a real implementation, this would:
        1. Navigate to the search results page
        2. Extract product URLs from the listing
        3. Return the list of URLs

        For this example, we return mock URLs.

        Returns:
            List of product URLs
        """
        # Mock URLs for demonstration
        # In production, scrape actual search results
        base_urls = [
            "https://example.com/product/smartphone-samsung-a54",
            "https://example.com/product/iphone-13-128gb",
            "https://example.com/product/xiaomi-redmi-note-12",
            "https://example.com/product/motorola-edge-30",
            "https://example.com/product/samsung-galaxy-s23",
        ]

        urls = base_urls[:self.max_products]
        logger.info(f"Generated {len(urls)} product URLs")
        return urls

    async def scrape_product(self, page: Page, url: str, product_id: int) -> Dict[str, Any]:
        """
        Scrape product data from a single product page.

        For demonstration purposes, this returns mock data.
        In production, implement actual scraping logic:

        Example selectors (adjust for actual site):
        - name: await page.locator('h1.product-title').text_content()
        - price: await page.locator('span.price-tag').text_content()
        - description: await page.locator('div.description').text_content()
        - image: await page.locator('img.product-image').get_attribute('src')
        - rating: await page.locator('span.rating').text_content()

        Args:
            page: Playwright Page instance
            url: Product URL
            product_id: Product ID

        Returns:
            Product data dictionary
        """
        try:
            # Navigate to product page
            await page.goto(url, wait_until="domcontentloaded")

            # In production, extract real data using selectors
            # For now, return mock data based on URL

            # Extract product name from URL (mock approach)
            product_slug = url.split("/")[-1].replace("-", " ").title()

            # Mock data - replace with actual scraping logic
            product_data = {
                "id": product_id,
                "name": product_slug,
                "image_url": f"https://via.placeholder.com/400x400?text={product_slug.replace(' ', '+')}",
                "description": f"High-quality {product_slug.lower()} with excellent features and performance. "
                              f"Perfect for everyday use with advanced capabilities.",
                "price": self._mock_price(product_id),
                "rating": round(4.0 + (product_id % 10) / 10, 1),
                "specifications": self._mock_specifications(product_slug),
                "source_url": url
            }

            logger.debug(f"[ID:{product_id}] Extracted data: {product_data['name']}")
            return product_data

        except Exception as e:
            logger.error(f"[ID:{product_id}] Error scraping {url}: {e}")
            raise

    def _mock_price(self, product_id: int) -> str:
        """Generate mock price based on product ID."""
        base_prices = [299.99, 399.99, 499.99, 599.99, 699.99, 799.99, 899.99, 999.99]
        price = base_prices[product_id % len(base_prices)]
        return f"${price}"

    def _mock_specifications(self, product_name: str) -> Dict[str, Any]:
        """Generate mock specifications based on product name."""
        specs = {
            "brand": product_name.split()[0] if product_name else "Generic",
            "condition": "New",
            "warranty": "12 months",
            "shipping": "Free shipping"
        }

        # Add tech specs for smartphones
        if "smartphone" in product_name.lower() or any(
            brand in product_name.lower()
            for brand in ["samsung", "iphone", "xiaomi", "motorola"]
        ):
            specs.update({
                "storage": "128GB",
                "ram": "6GB",
                "screen_size": "6.4 inches",
                "camera": "48MP main camera",
                "battery": "5000mAh"
            })

        return specs


class ExampleOLXScraper(ProductScraper):
    """
    Example scraper for OLX-style classified sites.

    Template for scraping classified listing sites.
    """

    def __init__(self, category: str = "electronics", max_products: int = 10):
        """
        Initialize OLX-style scraper.

        Args:
            category: Product category
            max_products: Maximum products to scrape
        """
        self.category = category
        self.max_products = max_products
        logger.info(f"ExampleOLXScraper initialized: category='{category}', max={max_products}")

    def get_product_urls(self) -> List[str]:
        """Get list of product URLs from OLX-style site."""
        # Mock URLs for demonstration
        urls = [
            f"https://example-olx.com/item/electronics-{i}"
            for i in range(1, self.max_products + 1)
        ]
        logger.info(f"Generated {len(urls)} OLX-style URLs")
        return urls

    async def scrape_product(self, page: Page, url: str, product_id: int) -> Dict[str, Any]:
        """
        Scrape product from OLX-style listing.

        Args:
            page: Playwright Page
            url: Product URL
            product_id: Product ID

        Returns:
            Product data
        """
        try:
            await page.goto(url, wait_until="domcontentloaded")

            # Mock data for demonstration
            product_data = {
                "id": product_id,
                "name": f"Used Electronics Item #{product_id}",
                "image_url": f"https://via.placeholder.com/300x300?text=Item+{product_id}",
                "description": f"Pre-owned {self.category} item in good condition. "
                              f"Well maintained and fully functional.",
                "price": f"${100 + (product_id * 50)}",
                "rating": None,  # OLX typically doesn't have ratings
                "specifications": {
                    "condition": "Used - Good",
                    "category": self.category,
                    "location": "Local pickup available",
                    "seller_type": "Individual"
                },
                "source_url": url
            }

            return product_data

        except Exception as e:
            logger.error(f"[ID:{product_id}] Error scraping OLX-style page {url}: {e}")
            raise
