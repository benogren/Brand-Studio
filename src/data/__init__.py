"""Data module for brand names dataset."""

from src.data.brand_names_dataset import (
    BRAND_NAMES_DATASET,
    get_brands_by_industry,
    get_brands_by_personality,
    get_brands_by_strategy,
    get_dataset_stats
)

__all__ = [
    'BRAND_NAMES_DATASET',
    'get_brands_by_industry',
    'get_brands_by_personality',
    'get_brands_by_strategy',
    'get_dataset_stats'
]
