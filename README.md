# Plotnine MCP Server

> **A Model Context Protocol (MCP) server that brings ggplot2's grammar of graphics to Python through plotnine, enabling AI-powered data visualization via natural language.**

Create publication-quality statistical graphics through chat using plotnine's Python implementation of R's beloved ggplot2. This modular MCP server allows Claude and other AI assistants to generate highly customizable visualizations by composing layers through the grammar of graphics paradigm.

## Features

- **Multiple Data Sources**: Load data from files (CSV, JSON, Parquet, Excel), URLs, or inline JSON
- **Grammar of Graphics**: Compose plots using aesthetics, geometries, scales, themes, facets, and coordinates
- **20+ Geometry Types**: Points, lines, bars, histograms, boxplots, violins, and more
- **Flexible Theming**: Built-in themes with extensive customization options
- **Statistical Transformations**: Add smoothing, binning, density estimation, and summaries
- **Faceting**: Split plots by categorical variables using wrap or grid layouts
- **Multiple Output Formats**: PNG, PDF, SVG with configurable dimensions and DPI

## Installation

### 1. Clone or download this repository

```bash
cd plotnine-mcp
```

### 2. Install dependencies

Using pip:
```bash
pip install -e .
```

For full functionality (parquet and Excel support):
```bash
pip install -e ".[full]"
```

### 3. Configure Claude Desktop

Add the server to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "plotnine": {
      "command": "python",
      "args": ["-m", "plotnine_mcp.server"]
    }
  }
}
```

If you installed in a virtual environment, use the full path to python:
```json
{
  "mcpServers": {
    "plotnine": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "plotnine_mcp.server"]
    }
  }
}
```

### 4. Restart Claude Desktop

The plotnine MCP server should now be available!

## Usage

### Basic Example

```
Create a scatter plot from data.csv with x=age and y=height
```

### Advanced Example

```
Create a line plot from sales_data.csv showing:
- x: date, y: revenue, color by region
- Use a minimal theme with figure size 12x6
- Add a smooth trend line
- Facet by product category
- Label the plot "Q4 Sales Performance"
- Save as PDF
```

## Available Tools

### create_plot

Create a plotnine visualization with full customization.

**Required Parameters:**
- `data_source`: Data source configuration
  - `type`: "file", "url", or "inline"
  - `path`: File path or URL (for file/url types)
  - `data`: Array of objects (for inline type)
  - `format`: "csv", "json", "parquet", or "excel" (auto-detected)

- `aes`: Aesthetic mappings (column names)
  - `x`, `y`: Axis variables
  - `color`, `fill`: Color aesthetics
  - `size`, `alpha`, `shape`, `linetype`: Additional aesthetics
  - `group`: Grouping variable

- `geom`: Geometry specification
  - `type`: Geometry type (point, line, bar, etc.)
  - `params`: Additional parameters (size, alpha, color, etc.)

**Optional Parameters:**
- `scales`: Array of scale configurations
- `theme`: Theme configuration with base and customizations
- `facets`: Faceting configuration
- `labels`: Plot labels (title, x, y, caption, subtitle)
- `coords`: Coordinate system configuration
- `stats`: Statistical transformations
- `output`: Output configuration (format, size, DPI, directory)

### list_geom_types

List all available geometry types with descriptions.

## Geometry Types

- **point**: Scatter plot points
- **line**: Line plot connecting points
- **bar**: Bar chart (counts by default)
- **col**: Column chart (identity stat)
- **histogram**: Histogram of continuous data
- **boxplot**: Box and whisker plot
- **violin**: Violin plot for distributions
- **area**: Filled area under line
- **density**: Kernel density plot
- **smooth**: Smoothed conditional means
- **jitter**: Jittered points (reduces overplotting)
- **tile**: Heatmap/tile plot
- **text**: Text annotations
- **errorbar**: Error bars
- **hline/vline/abline**: Reference lines
- **path**: Path connecting points in order
- **polygon**: Filled polygon
- **ribbon**: Ribbon for intervals

## Examples

### Simple Scatter Plot

```json
{
  "data_source": {
    "type": "file",
    "path": "./data/iris.csv"
  },
  "aes": {
    "x": "sepal_length",
    "y": "sepal_width",
    "color": "species"
  },
  "geom": {
    "type": "point",
    "params": {"size": 3, "alpha": 0.7}
  }
}
```

### Line Plot with Theme

```json
{
  "data_source": {
    "type": "url",
    "path": "https://example.com/timeseries.csv"
  },
  "aes": {
    "x": "date",
    "y": "value",
    "color": "category"
  },
  "geom": {
    "type": "line",
    "params": {"size": 1.5}
  },
  "scales": [
    {
      "aesthetic": "x",
      "type": "datetime",
      "params": {"date_breaks": "1 month"}
    }
  ],
  "theme": {
    "base": "minimal",
    "customizations": {
      "figure_size": [12, 6],
      "legend_position": "bottom"
    }
  },
  "labels": {
    "title": "Time Series Analysis",
    "x": "Date",
    "y": "Value"
  }
}
```

### Faceted Boxplot

```json
{
  "data_source": {
    "type": "inline",
    "data": [
      {"group": "A", "category": "X", "value": 10},
      {"group": "A", "category": "Y", "value": 15},
      {"group": "B", "category": "X", "value": 12}
    ]
  },
  "aes": {
    "x": "group",
    "y": "value",
    "fill": "group"
  },
  "geom": {
    "type": "boxplot"
  },
  "facets": {
    "type": "wrap",
    "facets": "~ category"
  },
  "theme": {
    "base": "bw"
  }
}
```

## Chat Examples

You can create plots through natural language:

**"Create a histogram of the 'age' column from users.csv"**

**"Make a scatter plot with smooth trend line showing price vs size, colored by category"**

**"Plot a line chart from sales.csv with date on x-axis and revenue on y-axis, faceted by region, using a dark theme"**

**"Create a violin plot comparing distributions of test scores across different schools"**

## Configuration Options

### Themes

Available base themes:
- `gray` (default)
- `bw` (black and white)
- `minimal`
- `classic`
- `dark`
- `light`
- `void`

### Scale Types

- **Positional**: continuous, discrete, log10, sqrt, datetime
- **Color/Fill**: gradient, discrete, brewer

### Coordinate Systems

- `cartesian` (default)
- `flip` (swap x and y)
- `polar` (for pie charts)
- `fixed` (fixed aspect ratio)

## Output

By default, plots are saved to `./output` directory as PNG files with 300 DPI. You can customize:

- **format**: png, pdf, svg
- **filename**: Custom filename (auto-generated by default)
- **width/height**: Dimensions in inches
- **dpi**: Resolution for raster formats
- **directory**: Output directory path

## Troubleshooting

### "Module not found" errors

Ensure you've installed the package:
```bash
pip install -e .
```

### Parquet/Excel support

Install optional dependencies:
```bash
pip install -e ".[full]"
```

### "Cannot find data file"

Use absolute paths or paths relative to where Claude Desktop is running.

### Plot not rendering

Check that:
- Column names in `aes` match your data
- Data types are appropriate for the geometry
- Required aesthetics are provided (e.g., `x` and `y` for most geoms)

## Development

### Running tests
```bash
pytest
```

### Code formatting
```bash
black src/
ruff check src/
```

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Resources

- [plotnine documentation](https://plotnine.readthedocs.io/)
- [MCP specification](https://modelcontextprotocol.io/)
- [Grammar of Graphics](https://ggplot2.tidyverse.org/)
