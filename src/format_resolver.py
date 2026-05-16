"""
Format Resolver — Resolves target_country to target format using format_rules.

Loads format_rules.csv and provides lookup functions for
mapping countries to their required e-invoice formats.
"""

import csv
import os
from config import FORMAT_BY_NAME, COUNTRY_FORMAT_MAP, FORMAT_RULES


# ═══════════════════════════════════════════════════════════
# FORMAT RULES LOADER
# ═══════════════════════════════════════════════════════════

def load_format_rules_from_csv(filepath: str) -> dict:
    """
    Load format_rules.csv into a dict keyed by format_name.
    This allows the system to work with any format_rules.csv,
    not just the hardcoded config — critical for generalization.
    """
    rules = {}
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["format_name"]
            rules[name] = {
                "format_id": int(row["format_id"]),
                "format_name": name,
                "used_in_countries": row["used_in_countries"],
                "syntax": row["syntax"],
                "required_fields": row["required_fields"],
                "optional_fields": row.get("optional_fields", ""),
                "tax_id_field_name": row.get("tax_id_field_name", ""),
                "line_item_structure": row["line_item_structure"],
                "supports_credit_note": row["supports_credit_note"].lower() == "true",
                "max_line_items": int(row.get("max_line_items", 999)),
            }
    return rules


def build_country_format_map(format_rules: dict) -> dict:
    """
    Build a country → format_name mapping from format_rules.
    If multiple formats serve a country, the first one found is used.
    This allows dynamic mapping from any format_rules.csv.
    """
    country_map = {}
    for name, rule in format_rules.items():
        countries = [c.strip() for c in rule["used_in_countries"].split(",")]
        for country in countries:
            if country not in country_map:
                country_map[country] = name
    return country_map


# ═══════════════════════════════════════════════════════════
# RESOLVER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def resolve_target_format(target_country: str, country_map: dict = None) -> str:
    """
    Resolve which e-invoice format is required for a given target country.

    Args:
        target_country: 2-letter country code (e.g., 'DE', 'FR')
        country_map: Optional custom country→format mapping.
                     Falls back to config.COUNTRY_FORMAT_MAP if None.

    Returns:
        format_name string, or None if country is unsupported.
    """
    if country_map is None:
        country_map = COUNTRY_FORMAT_MAP
    return country_map.get(target_country)


def get_format_rules(format_name: str, rules_dict: dict = None) -> dict:
    """
    Get the full rules dict for a given format name.

    Args:
        format_name: e.g., 'peppol_bis_3', 'facturx'
        rules_dict: Optional custom rules dict.
                    Falls back to config.FORMAT_BY_NAME if None.

    Returns:
        Format rules dict, or None if format not found.
    """
    if rules_dict is None:
        rules_dict = FORMAT_BY_NAME
    return rules_dict.get(format_name)


def get_source_format_rules(source_format: str, rules_dict: dict = None) -> dict:
    """
    Get format rules for the source format of an invoice.
    source_format can be a format_name string.
    """
    return get_format_rules(source_format, rules_dict)


def get_syntax_pair(source_format: str, target_format: str, rules_dict: dict = None) -> tuple:
    """
    Get the (source_syntax, target_syntax) pair for a format transcoding.
    Returns ('UBL', 'CII'), ('CII', 'UBL'), etc.
    """
    src_rules = get_format_rules(source_format, rules_dict)
    tgt_rules = get_format_rules(target_format, rules_dict)

    src_syntax = src_rules["syntax"] if src_rules else "unknown"
    tgt_syntax = tgt_rules["syntax"] if tgt_rules else "unknown"

    return src_syntax, tgt_syntax
