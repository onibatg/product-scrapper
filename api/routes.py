"""
FastAPI routes for product API endpoints.
"""

from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from models.product import Product, ProductResponse
from utils.helpers import load_products
from utils.logger import get_logger

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Product Scraper API",
    description="API for querying scraped product data from e-commerce sites",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.

    Returns:
        API welcome message and available endpoints
    """
    return {
        "message": "Product Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "GET /products": "Get all products or filter by IDs",
            "GET /products/{product_id}": "Get a specific product by ID",
            "GET /health": "Health check endpoint",
            "GET /docs": "Interactive API documentation"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        API health status
    """
    return {"status": "healthy", "service": "product-scraper-api"}


@app.get("/products", response_model=ProductResponse, tags=["Products"])
async def get_products(
    ids: Optional[str] = Query(
        None,
        description="Comma-separated list of product IDs (e.g., '1,2,3')",
        example="1,2,3"
    ),
    limit: Optional[int] = Query(
        None,
        description="Maximum number of products to return",
        ge=1,
        le=1000
    ),
    offset: Optional[int] = Query(
        0,
        description="Number of products to skip",
        ge=0
    )
):
    """
    Get all products or filter by IDs.

    Query Parameters:
        - ids: Comma-separated product IDs for batch retrieval (optional)
        - limit: Maximum number of products to return (optional)
        - offset: Number of products to skip for pagination (optional)

    Returns:
        ProductResponse with total count and list of products

    Examples:
        - GET /products → Returns all products
        - GET /products?ids=1,2,3 → Returns products with IDs 1, 2, and 3
        - GET /products?limit=10&offset=0 → Returns first 10 products
        - GET /products?ids=1,5,10&limit=2 → Returns max 2 products from IDs 1,5,10

    Raises:
        HTTPException: 404 if no products found, 500 if data loading fails
    """
    try:
        # Load products from file
        products_data = load_products("products.json")

        if not products_data:
            raise HTTPException(
                status_code=404,
                detail="No products found. Run the scraper first to populate data."
            )

        # Filter by IDs if provided
        if ids:
            try:
                id_list = [int(id_str.strip()) for id_str in ids.split(",")]
                products_data = [p for p in products_data if p.get("id") in id_list]

                if not products_data:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No products found with IDs: {ids}"
                    )

                logger.info(f"Filtered products by IDs: {id_list}")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid ID format. Use comma-separated integers (e.g., '1,2,3')"
                )

        # Apply pagination
        total = len(products_data)

        if offset >= total:
            products_data = []
        else:
            end_index = offset + limit if limit else total
            products_data = products_data[offset:end_index]

        # Validate and convert to Product models
        try:
            products = [Product(**p) for p in products_data]
        except Exception as e:
            logger.error(f"Error validating product data: {e}")
            raise HTTPException(
                status_code=500,
                detail="Invalid product data format in storage"
            )

        logger.info(f"Returning {len(products)} products (total: {total})")

        return ProductResponse(
            total=total,
            products=products
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving products: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/products/{product_id}", response_model=Product, tags=["Products"])
async def get_product_by_id(product_id: int):
    """
    Get a specific product by ID.

    Path Parameters:
        product_id: The unique product identifier

    Returns:
        Product model with all product details

    Example:
        GET /products/1 → Returns product with ID 1

    Raises:
        HTTPException: 404 if product not found
    """
    try:
        products_data = load_products("products.json")

        if not products_data:
            raise HTTPException(
                status_code=404,
                detail="No products found. Run the scraper first to populate data."
            )

        # Find product by ID
        product_data = next(
            (p for p in products_data if p.get("id") == product_id),
            None
        )

        if not product_data:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {product_id} not found"
            )

        # Validate and return product
        try:
            product = Product(**product_data)
            logger.info(f"Retrieved product ID {product_id}: {product.name}")
            return product
        except Exception as e:
            logger.error(f"Error validating product {product_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Invalid product data format"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 error handler."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": str(exc.detail) if hasattr(exc, "detail") else "Resource not found",
            "path": str(request.url)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 error handler."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "path": str(request.url)
        }
    )
