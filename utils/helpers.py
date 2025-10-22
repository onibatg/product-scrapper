"""
Helper functions for file operations and data management.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


def load_products(file_path: str = "products.json") -> List[Dict[str, Any]]:
    """
    Load products from JSON file.

    Args:
        file_path: Path to the JSON file (default: products.json)

    Returns:
        List of product dictionaries

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    path = Path(file_path)

    if not path.exists():
        logger.warning(f"File {file_path} not found, returning empty list")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data)} products from {file_path}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading products from {file_path}: {e}")
        return []


def save_products(products: List[Dict[str, Any]], file_path: str = "products.json") -> bool:
    """
    Save products to JSON file.

    Args:
        products: List of product dictionaries to save
        file_path: Path to the JSON file (default: products.json)

    Returns:
        True if successful, False otherwise

    Example:
        >>> products = [{"id": 1, "name": "Product 1", ...}]
        >>> save_products(products, "products.json")
        True
    """
    path = Path(file_path)

    try:
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(products)} products to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving products to {file_path}: {e}")
        return False


def merge_products(
    existing: List[Dict[str, Any]],
    new_products: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Merge new products with existing ones, avoiding duplicates by ID.

    Args:
        existing: List of existing product dictionaries
        new_products: List of new product dictionaries to merge

    Returns:
        Merged list of products

    Example:
        >>> existing = [{"id": 1, "name": "Old"}]
        >>> new = [{"id": 1, "name": "Updated"}, {"id": 2, "name": "New"}]
        >>> merged = merge_products(existing, new)
        >>> len(merged)
        2
    """
    # Create a dict indexed by ID for O(1) lookup
    products_dict = {p.get("id"): p for p in existing}

    # Update or add new products
    for product in new_products:
        product_id = product.get("id")
        if product_id is not None:
            products_dict[product_id] = product

    # Return as list
    merged = list(products_dict.values())
    logger.info(f"Merged products: {len(merged)} total")
    return merged
