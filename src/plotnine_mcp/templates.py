"""
Plot templates - Preset configurations for common visualization patterns.
"""

from typing import Any, Optional

# Common plot templates
TEMPLATES = {
    "time_series": {
        "description": "Line plot optimized for time-based data with date formatting",
        "config": {
            "geoms": [{"type": "line", "params": {"size": 1}}],
            "scales": [{"aesthetic": "x", "type": "datetime", "params": {}}],
            "theme": {
                "base": "minimal",
                "customizations": {"figure_size": [12, 6]},
            },
        },
        "required_aesthetics": ["x", "y"],
        "suggested_aesthetics": ["color", "group"],
    },
    "scatter_with_trend": {
        "description": "Scatter plot with linear regression trend line and confidence interval",
        "config": {
            "geoms": [
                {"type": "point", "params": {"size": 2, "alpha": 0.6}},
                {"type": "smooth", "params": {"method": "lm", "se": True}},
            ],
            "theme": {"base": "minimal"},
        },
        "required_aesthetics": ["x", "y"],
        "suggested_aesthetics": ["color"],
    },
    "distribution_comparison": {
        "description": "Violin plot for comparing distributions across groups",
        "config": {
            "geoms": [
                {"type": "violin", "params": {"alpha": 0.7}},
                {"type": "jitter", "params": {"width": 0.1, "alpha": 0.3, "size": 1}},
            ],
            "theme": {"base": "bw"},
        },
        "required_aesthetics": ["x", "y"],
        "suggested_aesthetics": ["fill", "color"],
    },
    "category_breakdown": {
        "description": "Bar chart showing counts or values by category",
        "config": {
            "geoms": [{"type": "col", "params": {}}],
            "theme": {
                "base": "minimal",
                "customizations": {"legend_position": "bottom"},
            },
            "coords": {"type": "flip", "params": {}},
        },
        "required_aesthetics": ["x", "y"],
        "suggested_aesthetics": ["fill"],
    },
    "correlation_heatmap": {
        "description": "Heatmap for visualizing correlations or relationships",
        "config": {
            "geoms": [{"type": "tile", "params": {}}],
            "scales": [
                {
                    "aesthetic": "fill",
                    "type": "gradient",
                    "params": {"low": "blue", "high": "red"},
                }
            ],
            "theme": {
                "base": "minimal",
                "customizations": {"figure_size": [10, 8]},
            },
        },
        "required_aesthetics": ["x", "y", "fill"],
        "suggested_aesthetics": [],
    },
    "boxplot_comparison": {
        "description": "Boxplot with individual points for detailed distribution comparison",
        "config": {
            "geoms": [
                {"type": "boxplot", "params": {"alpha": 0.7}},
                {"type": "jitter", "params": {"width": 0.2, "alpha": 0.4, "size": 1}},
            ],
            "theme": {"base": "bw"},
        },
        "required_aesthetics": ["x", "y"],
        "suggested_aesthetics": ["fill", "color"],
    },
    "multi_line": {
        "description": "Multiple line plots for comparing trends across categories",
        "config": {
            "geoms": [{"type": "line", "params": {"size": 1.2}}],
            "theme": {
                "base": "minimal",
                "customizations": {
                    "figure_size": [12, 6],
                    "legend_position": "right",
                },
            },
        },
        "required_aesthetics": ["x", "y", "color"],
        "suggested_aesthetics": ["linetype"],
    },
    "histogram_with_density": {
        "description": "Histogram overlaid with kernel density curve",
        "config": {
            "geoms": [
                {"type": "histogram", "params": {"alpha": 0.7, "bins": 30}},
                {"type": "density", "params": {"alpha": 0}},
            ],
            "theme": {"base": "minimal"},
        },
        "required_aesthetics": ["x"],
        "suggested_aesthetics": ["fill", "color"],
    },
    "before_after": {
        "description": "Side-by-side comparison of before and after measurements",
        "config": {
            "geoms": [
                {"type": "point", "params": {"size": 3}},
                {"type": "line", "params": {"alpha": 0.5}},
            ],
            "theme": {"base": "bw"},
            "facets": {"type": "wrap", "params": {"ncol": 2}},
        },
        "required_aesthetics": ["x", "y"],
        "suggested_aesthetics": ["group", "color"],
    },
}


def get_template(template_name: str) -> dict[str, Any]:
    """
    Get a plot template by name.

    Args:
        template_name: Name of the template

    Returns:
        Template configuration dictionary

    Raises:
        KeyError: If template name not found
    """
    if template_name not in TEMPLATES:
        available = ", ".join(sorted(TEMPLATES.keys()))
        raise KeyError(
            f"Template '{template_name}' not found. Available templates: {available}"
        )

    return TEMPLATES[template_name]


def list_templates() -> dict[str, str]:
    """
    List all available templates with descriptions.

    Returns:
        Dictionary mapping template names to descriptions
    """
    return {name: info["description"] for name, info in TEMPLATES.items()}


def apply_template(
    template_name: str,
    data_source: dict[str, Any],
    aes: dict[str, str],
    overrides: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Apply a template to create a complete plot configuration.

    Args:
        template_name: Name of the template to use
        data_source: Data source configuration
        aes: Aesthetic mappings (must include required aesthetics)
        overrides: Optional overrides for template config

    Returns:
        Complete plot configuration ready for create_plot

    Raises:
        ValueError: If required aesthetics are missing
        KeyError: If template not found
    """
    template = get_template(template_name)

    # Validate required aesthetics
    required = template["required_aesthetics"]
    provided = set(aes.keys())
    missing = set(required) - provided

    if missing:
        raise ValueError(
            f"Template '{template_name}' requires aesthetics: {required}. "
            f"Missing: {list(missing)}"
        )

    # Start with template config
    config = {
        "data_source": data_source,
        "aes": aes,
        **template["config"],
    }

    # Apply overrides if provided
    if overrides:
        config.update(overrides)

    return config


def suggest_template(
    num_numeric: int, num_categorical: int, has_time: bool, goal: Optional[str] = None
) -> list[str]:
    """
    Suggest appropriate templates based on data characteristics.

    Args:
        num_numeric: Number of numeric columns
        num_categorical: Number of categorical columns
        has_time: Whether data has time/date columns
        goal: Optional user-specified goal (e.g., "compare", "trend", "distribution")

    Returns:
        List of suggested template names
    """
    suggestions = []

    # Time-based suggestions
    if has_time and num_numeric >= 1:
        suggestions.append("time_series")
        if num_categorical >= 1:
            suggestions.append("multi_line")

    # Distribution comparisons
    if num_categorical >= 1 and num_numeric >= 1:
        suggestions.append("distribution_comparison")
        suggestions.append("boxplot_comparison")

    # Correlation/relationship
    if num_numeric >= 2:
        suggestions.append("scatter_with_trend")
        if num_numeric >= 3:
            suggestions.append("correlation_heatmap")

    # Single variable distribution
    if num_numeric >= 1 and num_categorical == 0:
        suggestions.append("histogram_with_density")

    # Category breakdown
    if num_categorical >= 1:
        suggestions.append("category_breakdown")

    # Goal-based refinement
    if goal:
        goal_lower = goal.lower()
        if "trend" in goal_lower or "time" in goal_lower:
            suggestions = [s for s in suggestions if "time" in s or "line" in s]
        elif "compare" in goal_lower or "comparison" in goal_lower:
            suggestions = [
                s for s in suggestions if "comparison" in s or "boxplot" in s
            ]
        elif "distribution" in goal_lower:
            suggestions = [
                s for s in suggestions if "distribution" in s or "histogram" in s
            ]
        elif "correlation" in goal_lower or "relationship" in goal_lower:
            suggestions = [s for s in suggestions if "correlation" in s or "scatter" in s]

    # Remove duplicates while preserving order
    seen = set()
    unique_suggestions = []
    for item in suggestions:
        if item not in seen:
            seen.add(item)
            unique_suggestions.append(item)

    return unique_suggestions[:5]  # Return top 5
