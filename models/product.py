"""
Pydantic models for product data.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, HttpUrl


class Product(BaseModel):
    """
    Product model representing scraped product data.

    Attributes:
        id: Unique identifier for the product
        name: Product name/title
        image_url: URL to the product image
        description: Product description
        price: Product price (can be string with currency or float)
        rating: Product rating (float or string)
        specifications: Flexible dict with key-value pairs for product specs
        source_url: Original URL where the product was scraped from
    """

    id: int = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name", min_length=1)
    image_url: str = Field(..., description="URL to product image")
    description: str = Field(..., description="Product description")
    price: str | float = Field(..., description="Product price")
    rating: Optional[str | float] = Field(None, description="Product rating")
    specifications: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible specifications dict"
    )
    source_url: Optional[str] = Field(None, description="Original product URL")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Smartphone Samsung Galaxy A54",
                "image_url": "https://example.com/image.jpg",
                "description": "Smartphone with 128GB storage and 6GB RAM",
                "price": "$299.99",
                "rating": 4.5,
                "specifications": {
                    "brand": "Samsung",
                    "storage": "128GB",
                    "ram": "6GB",
                    "screen": "6.4 inches"
                },
                "source_url": "https://example.com/product/123"
            }
        }


class ProductResponse(BaseModel):
    """
    API response model for product queries.

    Attributes:
        total: Total number of products
        products: List of products
    """

    total: int = Field(..., description="Total number of products")
    products: List[Product] = Field(..., description="List of products")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 2,
                "products": [
                    {
                        "id": 1,
                        "name": "Product 1",
                        "image_url": "https://example.com/img1.jpg",
                        "description": "Description 1",
                        "price": "$99.99",
                        "rating": 4.5,
                        "specifications": {"brand": "BrandA"},
                        "source_url": "https://example.com/p1"
                    }
                ]
            }
        }
