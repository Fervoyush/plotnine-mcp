"""
Error handling utilities with smart suggestions.
"""

import difflib
from typing import Optional


def suggest_column_name(column: str, available_columns: list[str], threshold: float = 0.6) -> Optional[str]:
    """
    Suggest a column name using fuzzy matching.

    Args:
        column: The column name that was not found
        available_columns: List of available column names
        threshold: Similarity threshold (0-1)

    Returns:
        Best matching column name or None
    """
    if not available_columns:
        return None

    matches = difflib.get_close_matches(column, available_columns, n=1, cutoff=threshold)
    return matches[0] if matches else None


def format_column_error(column: str, available_columns: list[str]) -> str:
    """
    Format a helpful error message for missing column.

    Args:
        column: The column name that was not found
        available_columns: List of available column names

    Returns:
        Formatted error message with suggestion
    """
    suggestion = suggest_column_name(column, available_columns)

    message = f"Column '{column}' not found in data."

    if suggestion:
        message += f"\n\nDid you mean: '{suggestion}'?"

    message += f"\n\nAvailable columns: {', '.join(available_columns)}"

    return message


def suggest_geom_type(geom_type: str, available_geoms: list[str]) -> Optional[str]:
    """
    Suggest a geometry type using fuzzy matching.

    Args:
        geom_type: The geometry type that was not found
        available_geoms: List of available geometry types

    Returns:
        Best matching geom type or None
    """
    if not available_geoms:
        return None

    matches = difflib.get_close_matches(geom_type, available_geoms, n=1, cutoff=0.5)
    return matches[0] if matches else None


def format_geom_error(geom_type: str, available_geoms: list[str]) -> str:
    """
    Format a helpful error message for unknown geom type.

    Args:
        geom_type: The geometry type that was not found
        available_geoms: List of available geometry types

    Returns:
        Formatted error message with suggestion
    """
    suggestion = suggest_geom_type(geom_type, available_geoms)

    message = f"Unknown geometry type: '{geom_type}'"

    if suggestion:
        message += f"\n\nDid you mean: '{suggestion}'?"

    message += f"\n\nAvailable geometry types: {', '.join(sorted(available_geoms))}"

    return message


def suggest_theme_name(theme: str, available_themes: list[str]) -> Optional[str]:
    """
    Suggest a theme name using fuzzy matching.

    Args:
        theme: The theme name that was not found
        available_themes: List of available themes

    Returns:
        Best matching theme or None
    """
    if not available_themes:
        return None

    matches = difflib.get_close_matches(theme, available_themes, n=1, cutoff=0.5)
    return matches[0] if matches else None


def format_theme_error(theme: str, available_themes: list[str]) -> str:
    """
    Format a helpful error message for unknown theme.

    Args:
        theme: The theme name that was not found
        available_themes: List of available themes

    Returns:
        Formatted error message with suggestion
    """
    suggestion = suggest_theme_name(theme, available_themes)

    message = f"Unknown theme: '{theme}'"

    if suggestion:
        message += f"\n\nDid you mean: '{suggestion}'?"

    message += f"\n\nAvailable themes: {', '.join(sorted(available_themes))}"

    return message
