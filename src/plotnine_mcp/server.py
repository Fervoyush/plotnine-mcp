"""
Plotnine MCP Server - Main server implementation.
"""

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent

from .data_loader import load_data, DataLoadError
from .plot_builder import build_plot, save_plot, PlotBuildError
from .templates import list_templates as get_template_list, apply_template, suggest_template
from .palettes import list_palettes, get_palette, palette_categories, create_scale_config
from .transforms import apply_transforms
from .schemas import (
    DataSource,
    Aesthetics,
    GeomConfig,
    ScaleConfig,
    ThemeConfig,
    FacetConfig,
    LabelsConfig,
    CoordConfig,
    StatConfig,
    OutputConfig,
)

# Create server instance
server = Server("plotnine-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="create_plot",
            description="""Create a plotnine visualization from data.

This tool allows you to create highly customizable plots using the grammar of graphics.
You can specify data sources (file, URL, or inline), aesthetic mappings, geometries,
scales, themes, facets, labels, and coordinate systems.

NEW: Multi-layer plots! Use 'geoms' array to combine multiple geometries in one plot.

Example usage:
- Simple scatter plot: provide data_source, aes (x, y), and geom (type: "point")
- Multi-layer plot: use geoms array with multiple geometries (e.g., point + smooth)
- Line plot with custom theme: add theme config with base and customizations
- Faceted plot: include facet config to split by categorical variables
- Multiple scales: provide list of scale configs for x, y, color, etc.

All parameters support extensive customization through nested objects.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_source": {
                        "type": "object",
                        "description": "Data source configuration (file, URL, or inline data)",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["file", "url", "inline"],
                                "description": "Source type",
                            },
                            "path": {
                                "type": "string",
                                "description": "File path or URL (for file/url types)",
                            },
                            "data": {
                                "type": "array",
                                "items": {"type": "object"},
                                "description": "Inline data as array of objects (for inline type)",
                            },
                            "format": {
                                "type": "string",
                                "enum": ["csv", "json", "parquet", "excel"],
                                "description": "Data format (auto-detected if not specified)",
                            },
                        },
                        "required": ["type"],
                    },
                    "aes": {
                        "type": "object",
                        "description": "Aesthetic mappings (column names from data)",
                        "properties": {
                            "x": {"type": "string", "description": "X-axis variable"},
                            "y": {"type": "string", "description": "Y-axis variable"},
                            "color": {"type": "string", "description": "Color variable"},
                            "fill": {"type": "string", "description": "Fill variable"},
                            "size": {"type": "string", "description": "Size variable"},
                            "alpha": {"type": "string", "description": "Alpha (transparency) variable"},
                            "shape": {"type": "string", "description": "Shape variable"},
                            "linetype": {"type": "string", "description": "Linetype variable"},
                            "group": {"type": "string", "description": "Grouping variable"},
                        },
                    },
                    "geom": {
                        "type": "object",
                        "description": "Single geometry specification (use 'geoms' for multi-layer plots)",
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "Geometry type: point, line, bar, histogram, boxplot, violin, area, density, smooth, jitter, tile, text, errorbar, hline, vline, abline, path, polygon, ribbon, col",
                            },
                            "params": {
                                "type": "object",
                                "description": "Additional geom parameters (e.g., size, alpha, color, fill, etc.)",
                            },
                        },
                        "required": ["type"],
                    },
                    "geoms": {
                        "type": "array",
                        "description": "Multiple geometry specifications for layered plots (e.g., scatter + smooth, boxplot + jitter)",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "description": "Geometry type: point, line, bar, histogram, boxplot, violin, area, density, smooth, jitter, tile, text, errorbar, hline, vline, abline, path, polygon, ribbon, col",
                                },
                                "params": {
                                    "type": "object",
                                    "description": "Additional geom parameters (e.g., size, alpha, color, fill, etc.)",
                                },
                            },
                            "required": ["type"],
                        },
                    },
                    "scales": {
                        "type": "array",
                        "description": "Scale configurations for axes and aesthetics",
                        "items": {
                            "type": "object",
                            "properties": {
                                "aesthetic": {
                                    "type": "string",
                                    "description": "Which aesthetic: x, y, color, fill, size, etc.",
                                },
                                "type": {
                                    "type": "string",
                                    "description": "Scale type: continuous, discrete, log10, sqrt, datetime, gradient, brewer, etc.",
                                },
                                "params": {
                                    "type": "object",
                                    "description": "Scale parameters (limits, breaks, labels, etc.)",
                                },
                            },
                            "required": ["aesthetic", "type"],
                        },
                    },
                    "theme": {
                        "type": "object",
                        "description": "Theme configuration",
                        "properties": {
                            "base": {
                                "type": "string",
                                "description": "Base theme: gray, bw, minimal, classic, dark, light, void",
                                "default": "gray",
                            },
                            "customizations": {
                                "type": "object",
                                "description": "Theme customizations (figure_size, legend_position, text properties, etc.)",
                            },
                        },
                    },
                    "facets": {
                        "type": "object",
                        "description": "Faceting configuration",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["wrap", "grid"],
                                "description": "Facet type",
                            },
                            "facets": {
                                "type": "string",
                                "description": "Faceting formula for facet_wrap (e.g., '~ variable')",
                            },
                            "rows": {
                                "type": "string",
                                "description": "Row variable for facet_grid",
                            },
                            "cols": {
                                "type": "string",
                                "description": "Column variable for facet_grid",
                            },
                            "params": {
                                "type": "object",
                                "description": "Additional facet parameters (ncol, scales, etc.)",
                            },
                        },
                    },
                    "labels": {
                        "type": "object",
                        "description": "Plot labels",
                        "properties": {
                            "title": {"type": "string", "description": "Plot title"},
                            "x": {"type": "string", "description": "X-axis label"},
                            "y": {"type": "string", "description": "Y-axis label"},
                            "caption": {"type": "string", "description": "Plot caption"},
                            "subtitle": {"type": "string", "description": "Plot subtitle"},
                        },
                    },
                    "coords": {
                        "type": "object",
                        "description": "Coordinate system configuration",
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "Coordinate type: cartesian, flip, fixed, trans",
                            },
                            "params": {
                                "type": "object",
                                "description": "Coordinate parameters",
                            },
                        },
                    },
                    "stats": {
                        "type": "array",
                        "description": "Statistical transformation configurations",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "description": "Stat type: smooth, bin, density, summary",
                                },
                                "params": {
                                    "type": "object",
                                    "description": "Stat parameters",
                                },
                            },
                            "required": ["type"],
                        },
                    },
                    "transforms": {
                        "type": "array",
                        "description": "Data transformations to apply before plotting (filter, group_summarize, sort, select, rename, mutate, drop_na, fill_na, sample, unique, rolling, pivot)",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "description": "Transform type",
                                },
                            },
                            "required": ["type"],
                        },
                    },
                    "output": {
                        "type": "object",
                        "description": "Output configuration",
                        "properties": {
                            "format": {
                                "type": "string",
                                "enum": ["png", "pdf", "svg"],
                                "default": "png",
                            },
                            "filename": {
                                "type": "string",
                                "description": "Output filename (auto-generated if not provided)",
                            },
                            "width": {"type": "number", "default": 8, "description": "Width in inches"},
                            "height": {"type": "number", "default": 6, "description": "Height in inches"},
                            "dpi": {"type": "integer", "default": 300, "description": "DPI for raster formats"},
                            "directory": {
                                "type": "string",
                                "default": "./output",
                                "description": "Output directory",
                            },
                        },
                    },
                },
                "required": ["data_source", "aes"],
            },
        ),
        Tool(
            name="list_geom_types",
            description="List all available geometry types that can be used in plots",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="preview_data",
            description="""Preview and inspect data before creating plots.

Returns a comprehensive summary including:
- Dataset shape (rows and columns)
- Column names and data types
- First few rows of data
- Basic statistics for numeric columns
- Missing value counts

This helps verify data loaded correctly and understand its structure.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_source": {
                        "type": "object",
                        "description": "Data source configuration (file, URL, or inline data)",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["file", "url", "inline"],
                                "description": "Source type",
                            },
                            "path": {
                                "type": "string",
                                "description": "File path or URL (for file/url types)",
                            },
                            "data": {
                                "type": "array",
                                "items": {"type": "object"},
                                "description": "Inline data as array of objects (for inline type)",
                            },
                            "format": {
                                "type": "string",
                                "enum": ["csv", "json", "parquet", "excel"],
                                "description": "Data format (auto-detected if not specified)",
                            },
                        },
                        "required": ["type"],
                    },
                    "rows": {
                        "type": "integer",
                        "default": 5,
                        "description": "Number of rows to preview (default: 5)",
                    },
                },
                "required": ["data_source"],
            },
        ),
        Tool(
            name="list_themes",
            description="List all available themes for plot styling",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="export_plot_config",
            description="""Export plot configuration to a JSON file for reuse.

This saves the exact configuration used to create a plot, allowing you to:
- Recreate the same plot later
- Share configurations with others
- Version control your visualizations
- Use as templates for similar plots""",
            inputSchema={
                "type": "object",
                "properties": {
                    "config": {
                        "type": "object",
                        "description": "The plot configuration to export (same structure as create_plot)",
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename (e.g., 'my_plot_config.json')",
                    },
                    "directory": {
                        "type": "string",
                        "default": "./plot_configs",
                        "description": "Directory to save config file",
                    },
                },
                "required": ["config", "filename"],
            },
        ),
        Tool(
            name="import_plot_config",
            description="""Import and use a saved plot configuration.

Load a previously exported plot configuration and create a plot from it.
You can optionally override specific parameters (like data_source) while
keeping the rest of the configuration intact.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "config_path": {
                        "type": "string",
                        "description": "Path to the saved configuration JSON file",
                    },
                    "overrides": {
                        "type": "object",
                        "description": "Optional overrides for config parameters (e.g., new data_source)",
                    },
                },
                "required": ["config_path"],
            },
        ),
        Tool(
            name="list_plot_templates",
            description="List all available plot templates with descriptions. Templates provide preset configurations for common visualization patterns like time series, scatter with trend, distribution comparison, etc.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="create_plot_from_template",
            description="""Create a plot using a predefined template.

Templates provide optimized configurations for common plot types:
- time_series: Line plot with date formatting
- scatter_with_trend: Points with regression line
- distribution_comparison: Violin + jitter for group comparison
- category_breakdown: Bar chart with categories
- correlation_heatmap: Tile plot for correlations
- boxplot_comparison: Boxplot with points overlay
- multi_line: Multiple lines for trend comparison
- histogram_with_density: Histogram with density curve
- before_after: Side-by-side comparison

You only need to provide data and aesthetics; the template handles the rest.
You can override any template settings if needed.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_name": {
                        "type": "string",
                        "description": "Name of the template to use",
                    },
                    "data_source": {
                        "type": "object",
                        "description": "Data source configuration",
                    },
                    "aes": {
                        "type": "object",
                        "description": "Aesthetic mappings (must include required aesthetics for template)",
                    },
                    "labels": {
                        "type": "object",
                        "description": "Optional plot labels (title, x, y, etc.)",
                    },
                    "output": {
                        "type": "object",
                        "description": "Optional output configuration",
                    },
                    "overrides": {
                        "type": "object",
                        "description": "Optional overrides for template config (geoms, theme, etc.)",
                    },
                },
                "required": ["template_name", "data_source", "aes"],
            },
        ),
        Tool(
            name="suggest_plot_templates",
            description="""Analyze data and suggest appropriate plot templates.

Examines data characteristics (number of numeric/categorical columns,
presence of time data) and optionally a user goal to recommend suitable
templates.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_source": {
                        "type": "object",
                        "description": "Data source to analyze",
                    },
                    "goal": {
                        "type": "string",
                        "description": "Optional user goal (e.g., 'compare distributions', 'show trend', 'correlation')",
                    },
                },
                "required": ["data_source"],
            },
        ),
        Tool(
            name="list_color_palettes",
            description="""List available color palettes with preview colors.

Palettes are organized by category:
- colorblind_safe: Accessible palettes (Okabe-Ito, Tol)
- scientific: Perceptually uniform (viridis, plasma, inferno, magma)
- categorical: Distinct colors for categories
- corporate: Professional business colors
- sequential: Gradual scales for ordered data
- diverging: Two-tone scales for data with midpoints

Use these palettes by adding a scale configuration to your plot.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional category filter (colorblind_safe, scientific, categorical, corporate, sequential, diverging)",
                    },
                },
            },
        ),
        Tool(
            name="batch_create_plots",
            description="""Create multiple plots in one batch operation.

Useful for:
- Creating plots for all numeric columns in a dataset
- Generating pairwise scatter plots
- Creating plots for each category separately
- Comparing different plot types

Each plot configuration is processed independently, and all plots are created in sequence.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "plots": {
                        "type": "array",
                        "description": "Array of plot configurations (same structure as create_plot)",
                        "items": {"type": "object"},
                    },
                },
                "required": ["plots"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "create_plot":
            return await create_plot_handler(arguments)
        elif name == "list_geom_types":
            return await list_geom_types_handler()
        elif name == "preview_data":
            return await preview_data_handler(arguments)
        elif name == "list_themes":
            return await list_themes_handler()
        elif name == "export_plot_config":
            return await export_plot_config_handler(arguments)
        elif name == "import_plot_config":
            return await import_plot_config_handler(arguments)
        elif name == "list_plot_templates":
            return await list_plot_templates_handler()
        elif name == "create_plot_from_template":
            return await create_plot_from_template_handler(arguments)
        elif name == "suggest_plot_templates":
            return await suggest_plot_templates_handler(arguments)
        elif name == "list_color_palettes":
            return await list_color_palettes_handler(arguments)
        elif name == "batch_create_plots":
            return await batch_create_plots_handler(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def create_plot_handler(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle create_plot tool calls."""
    try:
        # Parse and validate arguments
        data_source = DataSource(**arguments["data_source"])
        aes_config = Aesthetics(**arguments["aes"])

        # Handle geom vs geoms (backward compatibility)
        geom_config = None
        geom_configs = None
        if "geom" in arguments and arguments["geom"]:
            geom_config = GeomConfig(**arguments["geom"])
        if "geoms" in arguments and arguments["geoms"]:
            geom_configs = [GeomConfig(**g) for g in arguments["geoms"]]

        if not geom_config and not geom_configs:
            return [
                TextContent(
                    type="text",
                    text="Error: Either 'geom' or 'geoms' must be provided.\n\nUse 'geom' for single layer or 'geoms' for multi-layer plots.",
                )
            ]

        # Optional configurations
        scales = None
        if "scales" in arguments and arguments["scales"]:
            scales = [ScaleConfig(**s) for s in arguments["scales"]]

        theme_config = None
        if "theme" in arguments and arguments["theme"]:
            theme_config = ThemeConfig(**arguments["theme"])

        facet_config = None
        if "facets" in arguments and arguments["facets"]:
            facet_config = FacetConfig(**arguments["facets"])

        labels_config = None
        if "labels" in arguments and arguments["labels"]:
            labels_config = LabelsConfig(**arguments["labels"])

        coord_config = None
        if "coords" in arguments and arguments["coords"]:
            coord_config = CoordConfig(**arguments["coords"])

        stats = None
        if "stats" in arguments and arguments["stats"]:
            stats = [StatConfig(**s) for s in arguments["stats"]]

        output_config = OutputConfig(**(arguments.get("output", {})))

        # Load data
        try:
            data = load_data(data_source)
        except DataLoadError as e:
            return [
                TextContent(
                    type="text",
                    text=f"Data loading error: {str(e)}\n\nPlease check:\n- File path or URL is correct\n- File format is supported\n- Data is properly formatted",
                )
            ]

        # Apply data transformations if provided
        if "transforms" in arguments and arguments["transforms"]:
            try:
                data = apply_transforms(data, arguments["transforms"])
            except ValueError as e:
                return [
                    TextContent(
                        type="text",
                        text=f"Data transformation error: {str(e)}\n\nPlease check your transformation configurations.",
                    )
                ]

        # Build plot
        try:
            plot = build_plot(
                data=data,
                aes_config=aes_config,
                geom_config=geom_config,
                geom_configs=geom_configs,
                scales=scales,
                theme_config=theme_config,
                facet_config=facet_config,
                labels_config=labels_config,
                coord_config=coord_config,
                stats=stats,
            )
        except PlotBuildError as e:
            return [
                TextContent(
                    type="text",
                    text=f"Plot building error: {str(e)}\n\nPlease check:\n- Column names exist in data\n- Aesthetic mappings are valid\n- Geom type is supported\n- Scale/theme configurations are correct",
                )
            ]

        # Save plot
        try:
            result = save_plot(plot, output_config)
        except PlotBuildError as e:
            return [
                TextContent(
                    type="text",
                    text=f"Plot saving error: {str(e)}\n\nPlease check:\n- Output directory is writable\n- Filename is valid\n- Output format is supported",
                )
            ]

        # Return success message with details
        success_message = f"""Plot created successfully!

Output file: {result['path']}
Format: {result['format']}
Dimensions: {result['width']} x {result['height']} inches
DPI: {result['dpi']}

Data summary:
- Rows: {len(data)}
- Columns: {', '.join(data.columns.tolist())}
"""

        return [TextContent(type="text", text=success_message)]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Unexpected error: {str(e)}\n\nPlease check your input parameters and try again.",
            )
        ]


async def list_geom_types_handler() -> list[TextContent]:
    """Handle list_geom_types tool calls."""
    from .plot_builder import GEOM_MAP

    geom_list = sorted(GEOM_MAP.keys())
    geom_descriptions = {
        "point": "Scatter plot points",
        "line": "Line plot connecting points",
        "bar": "Bar chart (stat='count' by default)",
        "col": "Column chart (stat='identity')",
        "histogram": "Histogram of continuous data",
        "boxplot": "Box and whisker plot",
        "violin": "Violin plot for distribution",
        "area": "Area plot (filled line)",
        "density": "Density plot",
        "smooth": "Smoothed conditional means",
        "jitter": "Jittered points (for overplotting)",
        "tile": "Tile/heatmap",
        "text": "Text annotations",
        "errorbar": "Error bars",
        "hline": "Horizontal reference line",
        "vline": "Vertical reference line",
        "abline": "Diagonal reference line",
        "path": "Path connecting points in order",
        "polygon": "Filled polygon",
        "ribbon": "Ribbon (for confidence intervals)",
    }

    message = "Available geometry types:\n\n"
    for geom in geom_list:
        desc = geom_descriptions.get(geom, "")
        message += f"- {geom}: {desc}\n"

    return [TextContent(type="text", text=message)]


async def preview_data_handler(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle preview_data tool calls."""
    try:
        # Parse data source
        data_source = DataSource(**arguments["data_source"])
        rows = arguments.get("rows", 5)

        # Load data
        try:
            data = load_data(data_source)
        except DataLoadError as e:
            return [
                TextContent(
                    type="text",
                    text=f"Data loading error: {str(e)}\n\nPlease check:\n- File path or URL is correct\n- File format is supported\n- Data is properly formatted",
                )
            ]

        # Build preview message
        message = "Data Preview\n" + "=" * 50 + "\n\n"

        # Dataset shape
        message += f"Shape: {data.shape[0]} rows × {data.shape[1]} columns\n\n"

        # Column information
        message += "Columns:\n"
        for col in data.columns:
            dtype = str(data[col].dtype)
            message += f"  - {col} ({dtype})\n"
        message += "\n"

        # First N rows
        message += f"First {min(rows, len(data))} rows:\n"
        message += "-" * 50 + "\n"
        preview_df = data.head(rows)
        message += preview_df.to_string(index=False) + "\n\n"

        # Basic statistics for numeric columns
        numeric_cols = data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            message += "Numeric Column Statistics:\n"
            message += "-" * 50 + "\n"
            stats_df = data[numeric_cols].describe()
            message += stats_df.to_string() + "\n\n"

        # Missing values
        missing = data.isnull().sum()
        if missing.sum() > 0:
            message += "Missing Values:\n"
            message += "-" * 50 + "\n"
            for col, count in missing[missing > 0].items():
                pct = (count / len(data)) * 100
                message += f"  - {col}: {count} ({pct:.1f}%)\n"
        else:
            message += "No missing values found.\n"

        return [TextContent(type="text", text=message)]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error previewing data: {str(e)}\n\nPlease check your data source configuration.",
            )
        ]


async def list_themes_handler() -> list[TextContent]:
    """Handle list_themes tool calls."""
    from .plot_builder import THEME_MAP

    theme_descriptions = {
        "gray": "Gray background with white gridlines (ggplot2 default)",
        "bw": "Black and white theme with no background",
        "minimal": "Minimalist theme with minimal gridlines",
        "classic": "Classic look with axis lines and no gridlines",
        "dark": "Dark background theme",
        "light": "Light theme with subtle gray background",
        "void": "Empty theme with no elements (for custom designs)",
    }

    message = "Available Themes\n" + "=" * 50 + "\n\n"
    message += "Base themes:\n"
    for theme_name in sorted(THEME_MAP.keys()):
        desc = theme_descriptions.get(theme_name, "")
        message += f"  - {theme_name}: {desc}\n"

    message += "\n" + "=" * 50 + "\n"
    message += "Customization options:\n"
    message += "  - figure_size: [width, height] in inches\n"
    message += "  - legend_position: 'right', 'left', 'top', 'bottom', 'none'\n"
    message += "  - legend_direction: 'vertical', 'horizontal'\n"
    message += "  - panel_background: background color/style\n"
    message += "  - plot_background: overall plot background\n"
    message += "  - text: global text properties\n"
    message += "  - axis_text: axis label styling\n"
    message += "  - axis_title: axis title styling\n"

    message += "\nExample usage:\n"
    message += '  "theme": {\n'
    message += '    "base": "minimal",\n'
    message += '    "customizations": {\n'
    message += '      "figure_size": [12, 6],\n'
    message += '      "legend_position": "bottom"\n'
    message += '    }\n'
    message += '  }\n'

    return [TextContent(type="text", text=message)]


async def export_plot_config_handler(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle export_plot_config tool calls."""
    try:
        from pathlib import Path

        config = arguments["config"]
        filename = arguments["filename"]
        directory = arguments.get("directory", "./plot_configs")

        # Create directory if it doesn't exist
        output_dir = Path(directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Ensure filename ends with .json
        if not filename.endswith(".json"):
            filename += ".json"

        output_path = output_dir / filename

        # Write config to file
        with open(output_path, "w") as f:
            json.dump(config, f, indent=2)

        message = f"""Plot configuration exported successfully!

File: {output_path}
Size: {output_path.stat().st_size} bytes

You can now:
- Use 'import_plot_config' to recreate this plot
- Share this file with others
- Version control your visualization configs
- Edit the JSON to customize parameters"""

        return [TextContent(type="text", text=message)]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error exporting config: {str(e)}\n\nPlease check:\n- Config is valid JSON\n- Filename is valid\n- Directory is writable",
            )
        ]


async def import_plot_config_handler(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle import_plot_config tool calls."""
    try:
        from pathlib import Path

        config_path = Path(arguments["config_path"])
        overrides = arguments.get("overrides", {})

        # Check if file exists
        if not config_path.exists():
            return [
                TextContent(
                    type="text",
                    text=f"Configuration file not found: {config_path}\n\nPlease check the path and try again.",
                )
            ]

        # Load config from file
        with open(config_path, "r") as f:
            config = json.load(f)

        # Apply overrides if provided
        if overrides:
            config.update(overrides)

        # Create plot using the loaded config
        result = await create_plot_handler(config)

        # Prepend info about the config source
        original_message = result[0].text if result else ""
        new_message = f"""Plot created from imported configuration!

Config file: {config_path}
Overrides applied: {len(overrides)} parameter(s)

{original_message}"""

        return [TextContent(type="text", text=new_message)]

    except json.JSONDecodeError as e:
        return [
            TextContent(
                type="text",
                text=f"Invalid JSON in config file: {str(e)}\n\nPlease check that the file contains valid JSON.",
            )
        ]
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error importing config: {str(e)}\n\nPlease check:\n- Config file is valid\n- All required fields are present",
            )
        ]


async def list_plot_templates_handler() -> list[TextContent]:
    """Handle list_plot_templates tool calls."""
    templates = get_template_list()

    message = "Available Plot Templates\n" + "=" * 60 + "\n\n"

    for name, description in sorted(templates.items()):
        message += f"• {name}\n  {description}\n\n"

    message += "\n" + "=" * 60 + "\n"
    message += "Usage:\n"
    message += "Use 'create_plot_from_template' with the template name,\n"
    message += "data source, and required aesthetics.\n\n"
    message += "Use 'suggest_plot_templates' to get recommendations\n"
    message += "based on your data characteristics."

    return [TextContent(type="text", text=message)]


async def create_plot_from_template_handler(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle create_plot_from_template tool calls."""
    try:
        template_name = arguments["template_name"]
        data_source = arguments["data_source"]
        aes = arguments["aes"]
        overrides = arguments.get("overrides", {})

        # Apply labels and output if provided
        if "labels" in arguments:
            overrides["labels"] = arguments["labels"]
        if "output" in arguments:
            overrides["output"] = arguments["output"]

        # Apply template to create config
        try:
            config = apply_template(template_name, data_source, aes, overrides)
        except (KeyError, ValueError) as e:
            return [
                TextContent(
                    type="text",
                    text=f"Template error: {str(e)}\n\nUse 'list_plot_templates' to see available templates.",
                )
            ]

        # Create plot using the config
        result = await create_plot_handler(config)

        # Prepend template info
        original_message = result[0].text if result else ""
        new_message = f"""Plot created using template: {template_name}

{original_message}"""

        return [TextContent(type="text", text=new_message)]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error creating plot from template: {str(e)}\n\nPlease check your template name and aesthetics.",
            )
        ]


async def suggest_plot_templates_handler(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle suggest_plot_templates tool calls."""
    try:
        data_source = DataSource(**arguments["data_source"])
        goal = arguments.get("goal")

        # Load data to analyze
        try:
            data = load_data(data_source)
        except DataLoadError as e:
            return [
                TextContent(
                    type="text",
                    text=f"Data loading error: {str(e)}\n\nCannot analyze data for suggestions.",
                )
            ]

        # Analyze data characteristics
        import numpy as np

        numeric_cols = data.select_dtypes(include=[np.number]).columns
        categorical_cols = data.select_dtypes(include=["object", "category"]).columns

        # Check for datetime columns
        has_time = False
        for col in data.columns:
            if "date" in col.lower() or "time" in col.lower():
                has_time = True
                break
            # Also check dtype
            if data[col].dtype == "datetime64[ns]":
                has_time = True
                break

        num_numeric = len(numeric_cols)
        num_categorical = len(categorical_cols)

        # Get suggestions
        suggestions = suggest_template(num_numeric, num_categorical, has_time, goal)

        # Format message
        message = "Template Suggestions\n" + "=" * 60 + "\n\n"
        message += f"Data characteristics:\n"
        message += f"  • Numeric columns: {num_numeric} ({', '.join(numeric_cols) if num_numeric > 0 else 'none'})\n"
        message += f"  • Categorical columns: {num_categorical} ({', '.join(categorical_cols) if num_categorical > 0 else 'none'})\n"
        message += f"  • Time-based data: {'Yes' if has_time else 'No'}\n"

        if goal:
            message += f"  • User goal: {goal}\n"

        message += "\n"

        if suggestions:
            message += f"Recommended templates ({len(suggestions)}):\n\n"
            all_templates = get_template_list()
            for i, template_name in enumerate(suggestions, 1):
                desc = all_templates.get(template_name, "")
                message += f"{i}. {template_name}\n"
                message += f"   {desc}\n\n"
        else:
            message += "No specific templates recommended for this data.\n"
            message += "Try 'list_plot_templates' to see all available options.\n"

        message += "\n" + "=" * 60 + "\n"
        message += "Use 'create_plot_from_template' with one of these templates."

        return [TextContent(type="text", text=message)]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error analyzing data: {str(e)}",
            )
        ]


async def list_color_palettes_handler(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle list_color_palettes tool calls."""
    try:
        category = arguments.get("category")

        message = "Color Palettes\n" + "=" * 60 + "\n\n"

        if category:
            # Show specific category
            palettes = list_palettes(category)
            categories = palette_categories()
            desc = categories.get(category, "")

            message += f"Category: {category}\n"
            message += f"{desc}\n\n"

            for name, colors in sorted(palettes.items()):
                # Remove category prefix for display
                display_name = name.replace(f"{category}_", "")
                message += f"• {display_name} ({len(colors)} colors)\n"
                message += f"  Colors: {', '.join(colors[:5])}"
                if len(colors) > 5:
                    message += f" ... and {len(colors) - 5} more"
                message += "\n\n"
        else:
            # Show all categories
            categories = palette_categories()
            message += "Available Categories:\n\n"

            for cat, desc in categories.items():
                palettes = list_palettes(cat)
                message += f"• {cat} ({len(palettes)} palettes)\n"
                message += f"  {desc}\n\n"

            message += "\n" + "=" * 60 + "\n"
            message += "Usage:\n"
            message += "- Use list_color_palettes with a category to see specific palettes\n"
            message += "- Add palettes to plots via the 'scales' parameter\n\n"
            message += "Example:\n"
            message += '  "scales": [{\n'
            message += '    "aesthetic": "color",\n'
            message += '    "type": "discrete",\n'
            message += '    "params": {"values": ["#E69F00", "#56B4E9", ...]}\n'
            message += '  }]'

        return [TextContent(type="text", text=message)]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error listing palettes: {str(e)}",
            )
        ]


async def batch_create_plots_handler(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle batch_create_plots tool calls."""
    try:
        plots = arguments.get("plots", [])

        if not plots:
            return [
                TextContent(
                    type="text",
                    text="No plots provided. Please include an array of plot configurations in the 'plots' parameter.",
                )
            ]

        message = f"Batch Plot Creation\n" + "=" * 60 + "\n\n"
        message += f"Creating {len(plots)} plot(s)...\n\n"

        results = []
        successful = 0
        failed = 0

        for i, plot_config in enumerate(plots, 1):
            try:
                # Create plot using existing handler
                result = await create_plot_handler(plot_config)

                if result and "successfully" in result[0].text:
                    successful += 1
                    # Extract filename from result
                    result_text = result[0].text
                    if "Output file:" in result_text:
                        filename_line = [
                            line for line in result_text.split("\n") if "Output file:" in line
                        ][0]
                        filename = filename_line.split(": ")[1]
                        message += f"{i}. ✓ {filename}\n"
                    else:
                        message += f"{i}. ✓ Plot created\n"
                else:
                    failed += 1
                    error_msg = result[0].text if result else "Unknown error"
                    message += f"{i}. ✗ Failed: {error_msg[:100]}...\n"

                results.append({"index": i, "success": successful > failed, "result": result})

            except Exception as e:
                failed += 1
                message += f"{i}. ✗ Error: {str(e)[:100]}...\n"
                results.append({"index": i, "success": False, "error": str(e)})

        message += "\n" + "=" * 60 + "\n"
        message += f"Summary:\n"
        message += f"  • Total: {len(plots)}\n"
        message += f"  • Successful: {successful}\n"
        message += f"  • Failed: {failed}\n"

        if successful > 0:
            message += f"\n✓ {successful} plot(s) created successfully!"

        return [TextContent(type="text", text=message)]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Batch creation error: {str(e)}\n\nPlease check your plot configurations.",
            )
        ]


def main():
    """Run the MCP server."""
    import sys
    from mcp.server.stdio import stdio_server

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    asyncio.run(run())


if __name__ == "__main__":
    main()
