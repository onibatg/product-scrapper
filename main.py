"""
Main entry point for the Product Scraper application.

This module provides CLI commands to:
1. Run the scraper to collect product data
2. Start the FastAPI server to serve the data
3. Run both scraper and server together

Usage:
    python main.py scrape [--max-products N] [--concurrent N]
    python main.py serve [--host HOST] [--port PORT]
    python main.py run [--max-products N]
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from scraper.core import ScraperEngine
from scraper.examples import ExampleMercadoLibreScraper, ExampleOLXScraper
from utils.helpers import save_products, load_products, merge_products
from utils.logger import get_logger

logger = get_logger(__name__)


async def run_scraper(
    max_products: int = 10,
    max_concurrent: int = 10,
    scraper_type: str = "mercadolibre"
) -> bool:
    """
    Run the scraper to collect product data.

    Args:
        max_products: Maximum number of products to scrape
        max_concurrent: Maximum concurrent scraping tasks
        scraper_type: Type of scraper to use ('mercadolibre' or 'olx')

    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 60)
    logger.info("Starting Product Scraper")
    logger.info("=" * 60)

    try:
        # Initialize scraper engine
        engine = ScraperEngine(
            max_concurrent=max_concurrent,
            headless=True,
            timeout=30000
        )

        # Select scraper implementation
        if scraper_type.lower() == "olx":
            scraper = ExampleOLXScraper(
                category="electronics",
                max_products=max_products
            )
        else:
            scraper = ExampleMercadoLibreScraper(
                search_query="smartphone",
                max_products=max_products
            )

        logger.info(f"Using scraper: {scraper.__class__.__name__}")

        # Run scraper
        products = await engine.scrape_all(scraper)

        if not products:
            logger.warning("No products were scraped")
            return False

        # Convert to dict format for saving
        products_data = [
            {
                "id": p["id"],
                "name": p["name"],
                "image_url": p["image_url"],
                "description": p["description"],
                "price": p["price"],
                "rating": p.get("rating"),
                "specifications": p.get("specifications", {}),
                "source_url": p.get("source_url")
            }
            for p in products
        ]

        # Load existing products and merge
        existing_products = load_products("products.json")
        merged_products = merge_products(existing_products, products_data)

        # Save to file
        success = save_products(merged_products, "products.json")

        if success:
            logger.info("=" * 60)
            logger.info(f"Successfully scraped and saved {len(products)} products")
            logger.info(f"Total products in database: {len(merged_products)}")
            logger.info("=" * 60)
            return True
        else:
            logger.error("Failed to save products")
            return False

    except Exception as e:
        logger.error(f"Error running scraper: {e}", exc_info=True)
        return False


def run_api_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Start the FastAPI server.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        reload: Enable auto-reload on code changes
    """
    import uvicorn

    logger.info("=" * 60)
    logger.info("Starting FastAPI Server")
    logger.info("=" * 60)
    logger.info(f"Server will be available at: http://{host}:{port}")
    logger.info(f"API Documentation: http://{host}:{port}/docs")
    logger.info("=" * 60)

    # Check if products.json exists
    if not Path("products.json").exists():
        logger.warning(
            "products.json not found! Run 'python main.py scrape' first "
            "to populate product data."
        )

    uvicorn.run(
        "api.routes:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


async def run_full_pipeline(max_products: int = 10):
    """
    Run scraper and then start API server.

    Args:
        max_products: Maximum number of products to scrape
    """
    # Run scraper first
    success = await run_scraper(max_products=max_products)

    if not success:
        logger.error("Scraping failed, aborting server start")
        return

    # Give user option to start server
    print("\nScraping completed successfully!")
    print("\nOptions:")
    print("1. Start API server now")
    print("2. Exit")

    try:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice == "1":
            run_api_server()
        else:
            logger.info("Exiting. Run 'python main.py serve' to start the API server later.")
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Product Scraper - Web scraping tool with FastAPI integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py scrape --max-products 20 --concurrent 10
  python main.py serve --port 8000
  python main.py run --max-products 15
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scrape command
    scrape_parser = subparsers.add_parser(
        "scrape",
        help="Run the scraper to collect product data"
    )
    scrape_parser.add_argument(
        "--max-products",
        type=int,
        default=10,
        help="Maximum number of products to scrape (default: 10)"
    )
    scrape_parser.add_argument(
        "--concurrent",
        type=int,
        default=10,
        help="Maximum concurrent scraping tasks (default: 10)"
    )
    scrape_parser.add_argument(
        "--type",
        choices=["mercadolibre", "olx"],
        default="mercadolibre",
        help="Type of scraper to use (default: mercadolibre)"
    )

    # Serve command
    serve_parser = subparsers.add_parser(
        "serve",
        help="Start the FastAPI server"
    )
    serve_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    serve_parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes"
    )

    # Run command (scrape + serve)
    run_parser = subparsers.add_parser(
        "run",
        help="Run scraper and optionally start server"
    )
    run_parser.add_argument(
        "--max-products",
        type=int,
        default=10,
        help="Maximum number of products to scrape (default: 10)"
    )

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    try:
        if args.command == "scrape":
            asyncio.run(run_scraper(
                max_products=args.max_products,
                max_concurrent=args.concurrent,
                scraper_type=args.type
            ))

        elif args.command == "serve":
            run_api_server(
                host=args.host,
                port=args.port,
                reload=args.reload
            )

        elif args.command == "run":
            asyncio.run(run_full_pipeline(max_products=args.max_products))

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
