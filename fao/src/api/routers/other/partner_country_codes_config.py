# Template: templates/config.py.jinja2
# Generated as: fao/src/api/routers/partner_country_codes_config.py

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fao.src.db.pipelines.partner_country_codes.partner_country_codes_model import PartnerCountryCodes

from fao.src.core.validation import (
    is_valid_partner_country_code,
)
from fao.src.core.exceptions import (
    invalid_partner_country_code,
)

@dataclass
class PartnerCountryCodesConfig:
    """Configuration for partner_country_codes API"""
    
    # Basic info
    name: str = "partner_country_codes"
    model_name: str = "PartnerCountryCodes"
    table_name: str = "partner_country_codes"
    
    # Columns
    all_data_fields: List[str] = field(default_factory=lambda: [
        "partner_country_code",
        "partner_countries",
        "partner_country_code_m49",
        "source_dataset",
    ])

    all_parameter_fields: List[str] = field(default_factory=lambda: [
        "partner_country_code",
        "partner_countries",
        "partner_country_code_m49",
        "source_dataset",
    ])
    
    # Foreign keys
    foreign_keys: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])

    filter_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "partner_country_code",
            "filter_type": "multi",
            "filter_model": PartnerCountryCodes,  # <-- Actual model class
            "filter_column": "partner_country_code",
            "validation_func": is_valid_partner_country_code,
            "exception_func": invalid_partner_country_code,
        },
        {
            "name": "partner_countries",
            "filter_type": "like",
            "filter_model": PartnerCountryCodes,  # <-- Actual model class
            "filter_column": "partner_countries",
        },
        {
            "name": "partner_country_code_m49",
            "filter_type": "like",
            "filter_model": PartnerCountryCodes,  # <-- Actual model class
            "filter_column": "partner_country_code_m49",
        },
        {
            "name": "source_dataset",
            "filter_type": "like",
            "filter_model": PartnerCountryCodes,  # <-- Actual model class
            "filter_column": "source_dataset",
        },
    ])

    range_configs: List[Dict[str, Any]] = field(default_factory=lambda: [
    ])