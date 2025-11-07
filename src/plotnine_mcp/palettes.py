"""
Color palettes library for plotnine visualizations.
"""

# Color-blind safe palettes
COLORBLIND_SAFE = {
    "okabe_ito": [
        "#E69F00",  # Orange
        "#56B4E9",  # Sky Blue
        "#009E73",  # Bluish Green
        "#F0E442",  # Yellow
        "#0072B2",  # Blue
        "#D55E00",  # Vermillion
        "#CC79A7",  # Reddish Purple
    ],
    "tol_bright": [
        "#4477AA",  # Blue
        "#EE6677",  # Red
        "#228833",  # Green
        "#CCBB44",  # Yellow
        "#66CCEE",  # Cyan
        "#AA3377",  # Purple
        "#BBBBBB",  # Grey
    ],
    "tol_muted": [
        "#332288",  # Indigo
        "#88CCEE",  # Cyan
        "#44AA99",  # Teal
        "#117733",  # Green
        "#999933",  # Olive
        "#DDCC77",  # Sand
        "#CC6677",  # Rose
        "#882255",  # Wine
        "#AA4499",  # Purple
    ],
}

# Scientific color palettes
SCIENTIFIC = {
    "viridis": [
        "#440154",
        "#482777",
        "#3E4989",
        "#31688E",
        "#26828E",
        "#1F9E89",
        "#35B779",
        "#6DCD59",
        "#B4DE2C",
        "#FDE724",
    ],
    "plasma": [
        "#0D0887",
        "#4C02A1",
        "#7E03A8",
        "#A92395",
        "#CC4678",
        "#E56B5D",
        "#F89441",
        "#FEC328",
        "#F0F921",
    ],
    "inferno": [
        "#000004",
        "#1B0C41",
        "#4A0C6B",
        "#781C6D",
        "#A52C60",
        "#CF4446",
        "#ED6925",
        "#FB9A06",
        "#F7D13D",
        "#FCFFA4",
    ],
    "magma": [
        "#000004",
        "#180F3E",
        "#451077",
        "#721F81",
        "#9F2F7F",
        "#CD4071",
        "#F1605D",
        "#FD9668",
        "#FEC287",
        "#FCFDBF",
    ],
}

# Categorical color palettes
CATEGORICAL = {
    "set1": [
        "#E41A1C",
        "#377EB8",
        "#4DAF4A",
        "#984EA3",
        "#FF7F00",
        "#FFFF33",
        "#A65628",
        "#F781BF",
        "#999999",
    ],
    "set2": [
        "#66C2A5",
        "#FC8D62",
        "#8DA0CB",
        "#E78AC3",
        "#A6D854",
        "#FFD92F",
        "#E5C494",
        "#B3B3B3",
    ],
    "set3": [
        "#8DD3C7",
        "#FFFFB3",
        "#BEBADA",
        "#FB8072",
        "#80B1D3",
        "#FDB462",
        "#B3DE69",
        "#FCCDE5",
        "#D9D9D9",
        "#BC80BD",
        "#CCEBC5",
        "#FFED6F",
    ],
    "tableau10": [
        "#4E79A7",
        "#F28E2B",
        "#E15759",
        "#76B7B2",
        "#59A14F",
        "#EDC948",
        "#B07AA1",
        "#FF9DA7",
        "#9C755F",
        "#BAB0AC",
    ],
}

# Brand/Corporate color palettes
CORPORATE = {
    "corporate_blue": [
        "#003f5c",
        "#2f4b7c",
        "#665191",
        "#a05195",
        "#d45087",
        "#f95d6a",
        "#ff7c43",
        "#ffa600",
    ],
    "professional": [
        "#1f77b4",  # Blue
        "#ff7f0e",  # Orange
        "#2ca02c",  # Green
        "#d62728",  # Red
        "#9467bd",  # Purple
        "#8c564b",  # Brown
        "#e377c2",  # Pink
        "#7f7f7f",  # Gray
    ],
    "modern": [
        "#264653",  # Dark Blue
        "#2A9D8F",  # Teal
        "#E9C46A",  # Yellow
        "#F4A261",  # Orange
        "#E76F51",  # Red
    ],
}

# Sequential palettes
SEQUENTIAL = {
    "blues": ["#F7FBFF", "#DEEBF7", "#C6DBEF", "#9ECAE1", "#6BAED6", "#4292C6", "#2171B5", "#08519C", "#08306B"],
    "greens": ["#F7FCF5", "#E5F5E0", "#C7E9C0", "#A1D99B", "#74C476", "#41AB5D", "#238B45", "#006D2C", "#00441B"],
    "reds": ["#FFF5F0", "#FEE0D2", "#FCBBA1", "#FC9272", "#FB6A4A", "#EF3B2C", "#CB181D", "#A50F15", "#67000D"],
    "oranges": ["#FFF5EB", "#FEE6CE", "#FDD0A2", "#FDAE6B", "#FD8D3C", "#F16913", "#D94801", "#A63603", "#7F2704"],
}

# Diverging palettes
DIVERGING = {
    "red_blue": ["#B2182B", "#D6604D", "#F4A582", "#FDDBC7", "#F7F7F7", "#D1E5F0", "#92C5DE", "#4393C3", "#2166AC"],
    "red_green": ["#D73027", "#F46D43", "#FDAE61", "#FEE08B", "#FFFFBF", "#D9EF8B", "#A6D96A", "#66BD63", "#1A9850"],
    "purple_orange": ["#7F3B08", "#B35806", "#E08214", "#FDB863", "#FEE0B6", "#F7F7F7", "#D8DAEB", "#B2ABD2", "#8073AC", "#542788"],
}

# All palettes combined
ALL_PALETTES = {
    **{f"colorblind_safe_{k}": v for k, v in COLORBLIND_SAFE.items()},
    **{f"scientific_{k}": v for k, v in SCIENTIFIC.items()},
    **{f"categorical_{k}": v for k, v in CATEGORICAL.items()},
    **{f"corporate_{k}": v for k, v in CORPORATE.items()},
    **{f"sequential_{k}": v for k, v in SEQUENTIAL.items()},
    **{f"diverging_{k}": v for k, v in DIVERGING.items()},
}


def get_palette(palette_name: str) -> list[str]:
    """
    Get a color palette by name.

    Args:
        palette_name: Name of the palette (with or without category prefix)

    Returns:
        List of hex color codes

    Raises:
        KeyError: If palette not found
    """
    # Try direct lookup first
    if palette_name in ALL_PALETTES:
        return ALL_PALETTES[palette_name]

    # Try without prefix
    for key, value in ALL_PALETTES.items():
        if key.endswith(f"_{palette_name}"):
            return value

    # Not found
    raise KeyError(
        f"Palette '{palette_name}' not found. Use list_palettes() to see available palettes."
    )


def list_palettes(category: str = None) -> dict[str, list[str]]:
    """
    List available color palettes.

    Args:
        category: Optional category filter (colorblind_safe, scientific, categorical, corporate, sequential, diverging)

    Returns:
        Dictionary of palette names to color lists
    """
    if category:
        prefix = f"{category}_"
        return {k: v for k, v in ALL_PALETTES.items() if k.startswith(prefix)}
    return ALL_PALETTES


def palette_categories() -> dict[str, str]:
    """
    Get palette categories with descriptions.

    Returns:
        Dictionary mapping category names to descriptions
    """
    return {
        "colorblind_safe": "Accessible color schemes for colorblind viewers",
        "scientific": "Perceptually uniform palettes (viridis, plasma, inferno, magma)",
        "categorical": "Distinct colors for categorical data",
        "corporate": "Professional color schemes for business presentations",
        "sequential": "Gradual color scales for ordered data",
        "diverging": "Two-tone scales for data with a midpoint",
    }


def get_palette_info(palette_name: str) -> dict:
    """
    Get information about a specific palette.

    Args:
        palette_name: Name of the palette

    Returns:
        Dictionary with palette info including colors and count
    """
    colors = get_palette(palette_name)

    # Determine category
    category = "unknown"
    for cat in palette_categories().keys():
        if palette_name.startswith(cat):
            category = cat
            break

    return {
        "name": palette_name,
        "category": category,
        "colors": colors,
        "count": len(colors),
    }


def create_scale_config(palette_name: str, aesthetic: str = "color", type: str = "discrete") -> dict:
    """
    Create a scale configuration using a palette.

    Args:
        palette_name: Name of the palette to use
        aesthetic: Aesthetic to apply to (color, fill)
        type: Scale type (discrete, gradient)

    Returns:
        Scale configuration dictionary
    """
    colors = get_palette(palette_name)

    if type == "discrete":
        return {
            "aesthetic": aesthetic,
            "type": "discrete",
            "params": {"values": colors},
        }
    elif type == "gradient":
        # For gradient, use first and last colors
        return {
            "aesthetic": aesthetic,
            "type": "gradient",
            "params": {"low": colors[0], "high": colors[-1]},
        }
    else:
        raise ValueError(f"Unknown scale type: {type}")
