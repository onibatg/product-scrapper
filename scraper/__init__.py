"""
Web scraper module with Playwright integration.
"""

from .core import ScraperEngine, ProductScraper
from .examples import ExampleMercadoLibreScraper

__all__ = ["ScraperEngine", "ProductScraper", "ExampleMercadoLibreScraper"]
