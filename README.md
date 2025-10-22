# Product Scraper - Web Scraping POC with FastAPI

A modular and efficient web scraper built with Python, Playwright, and FastAPI. This proof of concept demonstrates concurrent web scraping of e-commerce sites (like Mercado Libre, OLX, Linio) with an HTTP API to query the collected data.

## Features

- **Async Web Scraping**: Built with Playwright and asyncio for efficient concurrent scraping
- **Configurable Concurrency**: Control up to 10 concurrent scraping tasks
- **RESTful API**: FastAPI-based API to query scraped product data
- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Error Handling**: Robust error handling with detailed logging
- **Batch Operations**: Support for batch retrieval of products via API
- **Memory Efficient**: Optimized to use less than 100MB for 10 concurrent scrapers

## Project Structure

```
product-scrapper/
├── api/
│   ├── __init__.py
│   └── routes.py              # FastAPI routes and endpoints
├── models/
│   ├── __init__.py
│   └── product.py             # Pydantic models for products
├── scraper/
│   ├── __init__.py
│   ├── core.py                # Core scraper engine with Playwright
│   └── examples.py            # Example scraper implementations
├── utils/
│   ├── __init__.py
│   ├── helpers.py             # Helper functions for file operations
│   └── logger.py              # Logging configuration
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
├── products.json              # Scraped product data (generated)
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd product-scrapper
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

## Usage

The application provides three main commands: `scrape`, `serve`, and `run`.

### 1. Run the Scraper

Scrape products and save them to `products.json`:

```bash
python main.py scrape
```

**Options**:
- `--max-products N`: Maximum number of products to scrape (default: 10)
- `--concurrent N`: Maximum concurrent tasks (default: 10)
- `--type TYPE`: Scraper type - `mercadolibre` or `olx` (default: mercadolibre)

**Examples**:
```bash
# Scrape 20 products with 10 concurrent tasks
python main.py scrape --max-products 20 --concurrent 10

# Use OLX-style scraper
python main.py scrape --type olx --max-products 15
```

### 2. Start the API Server

Serve the scraped products via REST API:

```bash
python main.py serve
```

**Options**:
- `--host HOST`: Host to bind (default: 0.0.0.0)
- `--port PORT`: Port to bind (default: 8000)
- `--reload`: Enable auto-reload on code changes

**Examples**:
```bash
# Start server on port 8080
python main.py serve --port 8080

# Start with auto-reload for development
python main.py serve --reload
```

### 3. Run Full Pipeline

Run scraper and optionally start the API server:

```bash
python main.py run --max-products 15
```

## API Endpoints

Once the server is running, the following endpoints are available:

### GET /

Root endpoint with API information.

**Example**:
```bash
curl http://localhost:8000/
```

### GET /health

Health check endpoint.

**Example**:
```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "product-scraper-api"
}
```

### GET /products

Get all products or filter by IDs.

**Query Parameters**:
- `ids` (optional): Comma-separated product IDs (e.g., "1,2,3")
- `limit` (optional): Maximum number of products to return
- `offset` (optional): Number of products to skip

**Examples**:

```bash
# Get all products
curl http://localhost:8000/products

# Get specific products by ID
curl http://localhost:8000/products?ids=1,2,3

# Pagination
curl http://localhost:8000/products?limit=10&offset=0

# Combine filters
curl http://localhost:8000/products?ids=1,5,10&limit=2
```

**Response**:
```json
{
  "total": 10,
  "products": [
    {
      "id": 1,
      "name": "Smartphone Samsung Galaxy A54",
      "image_url": "https://example.com/image.jpg",
      "description": "High-quality smartphone with excellent features...",
      "price": "$299.99",
      "rating": 4.5,
      "specifications": {
        "brand": "Samsung",
        "storage": "128GB",
        "ram": "6GB",
        "screen_size": "6.4 inches",
        "camera": "48MP main camera",
        "battery": "5000mAh"
      },
      "source_url": "https://example.com/product/123"
    }
  ]
}
```

### GET /products/{product_id}

Get a specific product by ID.

**Example**:
```bash
curl http://localhost:8000/products/1
```

**Response**:
```json
{
  "id": 1,
  "name": "Smartphone Samsung Galaxy A54",
  "image_url": "https://example.com/image.jpg",
  "description": "High-quality smartphone with excellent features...",
  "price": "$299.99",
  "rating": 4.5,
  "specifications": {
    "brand": "Samsung",
    "storage": "128GB",
    "ram": "6GB"
  },
  "source_url": "https://example.com/product/123"
}
```

### GET /docs

Interactive API documentation (Swagger UI).

**Access**: Open `http://localhost:8000/docs` in your browser

### GET /redoc

Alternative API documentation (ReDoc).

**Access**: Open `http://localhost:8000/redoc` in your browser

## Product Data Schema

Each product contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Unique product identifier |
| `name` | string | Product name/title |
| `image_url` | string | URL to product image |
| `description` | string | Product description |
| `price` | string/float | Product price |
| `rating` | string/float | Product rating (optional) |
| `specifications` | object | Flexible key-value pairs for specs |
| `source_url` | string | Original product URL (optional) |

## Development

### Adding Custom Scrapers

To create a custom scraper:

1. Create a new class that inherits from `ProductScraper` in `scraper/examples.py`
2. Implement the required methods:
   - `get_product_urls()`: Return list of URLs to scrape
   - `scrape_product(page, url, product_id)`: Extract product data from a page

**Example**:

```python
from scraper.core import ProductScraper
from playwright.async_api import Page

class MyCustomScraper(ProductScraper):
    def get_product_urls(self) -> List[str]:
        # Return list of product URLs
        return ["https://example.com/product/1", ...]

    async def scrape_product(self, page: Page, url: str, product_id: int) -> Dict[str, Any]:
        await page.goto(url)

        # Extract data using Playwright selectors
        name = await page.locator('h1.product-title').text_content()
        price = await page.locator('span.price').text_content()

        return {
            "id": product_id,
            "name": name,
            "price": price,
            # ... other fields
        }
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Configuration

### Scraper Configuration

Modify scraper settings in `scraper/core.py`:

- `max_concurrent`: Maximum concurrent tasks (default: 10)
- `headless`: Run browser in headless mode (default: True)
- `timeout`: Page operation timeout in ms (default: 30000)

### API Configuration

Configure API settings when starting the server:

```bash
python main.py serve --host 0.0.0.0 --port 8000
```

## Performance

- **Memory Usage**: < 100MB for 10 concurrent scrapers
- **Concurrency**: Up to 10 concurrent scraping tasks
- **Timeout**: 30 seconds per page operation
- **Error Handling**: Graceful handling of network errors and HTML inconsistencies

## Logging

The application uses structured logging with the following format:

```
[2025-10-22 10:30:45] [INFO] [module_name] Message
```

Logs include:
- Scraping progress
- API requests
- Errors and exceptions
- Performance metrics

## Limitations

- **Example Implementation**: Current scrapers use mock data for demonstration
- **Rate Limiting**: No built-in rate limiting (add if needed for production)
- **Authentication**: No authentication on API endpoints
- **Database**: Uses JSON file storage (consider database for production)

## Production Considerations

For production deployment, consider:

1. **Database**: Replace JSON file with PostgreSQL/MongoDB
2. **Rate Limiting**: Add rate limiting to API endpoints
3. **Authentication**: Implement API key or OAuth authentication
4. **Caching**: Add Redis for caching frequently accessed data
5. **Monitoring**: Integrate with monitoring tools (Prometheus, Grafana)
6. **Error Tracking**: Add Sentry or similar error tracking
7. **Real Scrapers**: Implement actual scraping logic with proper selectors
8. **Respect robots.txt**: Always check and respect robots.txt
9. **User-Agent Rotation**: Implement user-agent rotation
10. **Proxy Support**: Add proxy support for large-scale scraping

## Troubleshooting

### Playwright Installation Issues

If Playwright browsers fail to install:

```bash
# Install system dependencies (Ubuntu/Debian)
playwright install-deps

# Reinstall browsers
playwright install chromium
```

### Port Already in Use

If port 8000 is already in use:

```bash
python main.py serve --port 8080
```

### Empty products.json

If the API returns "No products found":

```bash
# Run the scraper first
python main.py scrape
```

## License

MIT License - feel free to use this project as a template for your own scrapers.

## Author

**Jesús Legarda**

- Domain: Web Scraping / Data Engineering / FastAPI Integration
- Version: 1.0.0
- Last Updated: 2025-10-22

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/docs` endpoint

---

**Note**: This is a proof of concept for educational purposes. Always respect website terms of service and robots.txt when scraping.