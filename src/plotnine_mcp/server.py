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

Example usage:
- Simple scatter plot: provide data_source, aes (x, y), and geom (type: "point")
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
                        "description": "Geometry specification",
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
                "required": ["data_source", "aes", "geom"],
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
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "create_plot":
            return await create_plot_handler(arguments)
        elif name == "list_geom_types":
            return await list_geom_types_handler()
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
        geom_config = GeomConfig(**arguments["geom"])

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

        # Build plot
        try:
            plot = build_plot(
                data=data,
                aes_config=aes_config,
                geom_config=geom_config,
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
