# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/currencies_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.currencies.currencies_model import Currencies

from fao.src.core.validation import (
    is_valid_iso_currency_code,
)
from fao.src.core.exceptions import (
    invalid_iso_currency_code,
)

@dataclass
class CurrenciesConfig:
    """Configuration for currencies API"""
    
    # Basic info
    name: str = "currencies"
    model_name: str = "Currencies"
    table_name: str = "currencies"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "iso_currency_code",
        "currency",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "iso_currency_code",
        "currency",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "iso_currency_code",
            "filter_type": "multi",
            "filter_model": Currencies,  # <-- Actual model class
            "filter_column": "iso_currency_code",
            "validation_func": is_valid_iso_currency_code,
            "exception_func": invalid_iso_currency_code,
        },
        {
            "name": "currency",
            "filter_type": "like",
            "filter_model": Currencies,  # <-- Actual model class
            "filter_column": "currency",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": Currencies,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])