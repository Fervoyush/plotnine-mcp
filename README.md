# Plotnine MCP Server

> **A Model Context Protocol (MCP) server that brings ggplot2's grammar of graphics to Python through plotnine, enabling AI-powered data visualization via natural language.**

Create publication-quality statistical graphics through chat using plotnine's Python implementation of R's beloved ggplot2. This modular MCP server allows Claude and other AI assistants to generate highly customizable visualizations by composing layers through the grammar of graphics paradigm.

## Features

### Core Visualization
- **🎨 Multi-Layer Plots**: Combine multiple geometries in a single plot (scatter + trend lines, boxplots + jitter, etc.)
- **Grammar of Graphics**: Compose plots using aesthetics, geometries, scales, themes, facets, and coordinates
- **20+ Geometry Types**: Points, lines, bars, histograms, boxplots, violins, and more
- **Multiple Data Sources**: Load data from files (CSV, JSON, Parquet, Excel), URLs, or inline JSON
- **Multiple Output Formats**: PNG, PDF, SVG with configurable dimensions and DPI

### Smart Features (NEW!)
- **📋 9 Plot Templates**: Pre-configured templates for common patterns (time series, scatter with trend, distribution comparison, etc.)
- **🤖 AI Template Suggestions**: Analyzes your data and recommends appropriate plot types
- **🎨 21 Color Palettes**: Colorblind-safe, scientific, categorical, corporate, sequential, and diverging palettes
- **📊 Data Preview**: Inspect data before plotting with comprehensive summaries
- **🎯 Smart Error Messages**: Fuzzy matching suggests corrections for typos in column names, geom types, and themes
- **💾 Config Export/Import**: Save and reuse plot configurations as JSON files

### Data Manipulation (NEW!)
- **🔄 12 Data Transformations**: filter, group_summarize, sort, select, rename, mutate, drop_na, fill_na, sample, unique, rolling, pivot
- **⚡ Batch Processing**: Create multiple plots in one operation
- **🔗 Chained Transforms**: Apply multiple transformations in sequence

### Theming & Customization
- **Flexible Theming**: Built-in themes with extensive customization options
- **Statistical Transformations**: Add smoothing, binning, density estimation, and summaries
- **Faceting**: Split plots by categorical variables using wrap or grid layouts

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

### 3. Configure Your MCP Client

#### Finding Your Installation Path

First, find where the `plotnine-mcp` command was installed:

```bash
which plotnine-mcp
```

This will show something like `/path/to/python/bin/plotnine-mcp`. Use this full path in the configurations below.

#### Claude Desktop

Add the server to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Recommended (using entry point):**
```json
{
  "mcpServers": {
    "plotnine": {
      "command": "/path/to/your/python/bin/plotnine-mcp",
      "args": []
    }
  }
}
```

**Alternative (using python -m):**
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

If you installed in a virtual environment, replace with the full path:
```json
{
  "mcpServers": {
    "plotnine": {
      "command": "/path/to/venv/bin/plotnine-mcp",
      "args": []
    }
  }
}
```

#### Cursor

**Recommended approach:** Configure via `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "plotnine": {
      "command": "/path/to/your/python/bin/plotnine-mcp",
      "args": []
    }
  }
}
```

**Alternative:** Add to Cursor global settings by opening the command palette (`Cmd/Ctrl+Shift+P`) and searching for "Preferences: Open User Settings (JSON)":

```json
{
  "mcp.servers": {
    "plotnine": {
      "command": "/path/to/your/python/bin/plotnine-mcp",
      "args": []
    }
  }
}
```

**Using python -m alternative:**
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

#### VSCode (with Cline/Roo-Cline)

Add to your VSCode MCP settings file:

**macOS/Linux**: `~/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json`

**Windows**: `%APPDATA%\Code\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "plotnine": {
      "command": "/path/to/your/python/bin/plotnine-mcp",
      "args": []
    }
  }
}
```

For other MCP clients in VSCode, consult their specific documentation for MCP server configuration.

### 4. Restart Your Application

Restart Claude Desktop, Cursor, or VSCode for the changes to take effect. The plotnine MCP server should now be available!

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

## Available Tools (11 Total)

### Core Tools

#### create_plot

Create a plotnine visualization with full customization.

**Required Parameters:**
- `data_source`: Data source configuration
- `aes`: Aesthetic mappings (column names)
- `geom` or `geoms`: Geometry specification(s)

**Optional Parameters:**
- `scales`: Array of scale configurations
- `theme`: Theme configuration
- `facets`: Faceting configuration
- `labels`: Plot labels (title, x, y, caption, subtitle)
- `coords`: Coordinate system configuration
- `stats`: Statistical transformations
- `transforms`: Data transformations (NEW!)
- `output`: Output configuration (format, size, DPI, directory)

#### list_geom_types

List all 20+ available geometry types with descriptions.

### Data Tools (NEW!)

#### preview_data

Preview and inspect data before creating plots. Returns dataset shape, column types, first rows, statistics, and missing values.

**Parameters:**
- `data_source`: Data source configuration
- `rows`: Number of rows to preview (default: 5)

### Template Tools (NEW!)

#### list_plot_templates

List all 9 available plot templates with descriptions:
- time_series
- scatter_with_trend
- distribution_comparison
- category_breakdown
- correlation_heatmap
- boxplot_comparison
- multi_line
- histogram_with_density
- before_after

#### create_plot_from_template

Create a plot using a predefined template. Just provide data and aesthetics; the template handles the rest.

**Parameters:**
- `template_name`: Name of the template
- `data_source`: Data source configuration
- `aes`: Aesthetic mappings
- `labels`: Optional labels
- `output`: Optional output config
- `overrides`: Optional overrides for template settings

#### suggest_plot_templates

Analyze your data and get AI-powered plot recommendations based on column types and optional goal.

**Parameters:**
- `data_source`: Data source to analyze
- `goal`: Optional goal (e.g., "compare distributions", "show trend")

### Style Tools (NEW!)

#### list_themes

List all available themes for plot styling with descriptions and customization options.

#### list_color_palettes

List 21 color palettes across 6 categories:
- Colorblind-safe (3 palettes)
- Scientific (4 palettes)
- Categorical (4 palettes)
- Corporate (3 palettes)
- Sequential (4 palettes)
- Diverging (3 palettes)

**Parameters:**
- `category`: Optional category filter

### Configuration Tools

#### export_plot_config

Export plot configuration to JSON for reuse and sharing.

**Parameters:**
- `config`: The plot configuration to export
- `filename`: Output filename
- `directory`: Output directory (default: './plot_configs')

#### import_plot_config

Import and use a saved plot configuration with optional overrides.

**Parameters:**
- `config_path`: Path to saved configuration
- `overrides`: Optional parameter overrides

### Batch Tools (NEW!)

#### batch_create_plots

Create multiple plots in one operation. Perfect for generating plots for all columns, pairwise comparisons, or different visualizations of the same data.

**Parameters:**
- `plots`: Array of plot configurations

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

### Multi-Layer Plot: Scatter + Smooth Trend

**NEW!** Layer multiple geometries to create complex visualizations:

```json
{
  "data_source": {
    "type": "file",
    "path": "./data/measurements.csv"
  },
  "aes": {
    "x": "time",
    "y": "value",
    "color": "sensor"
  },
  "geoms": [
    {
      "type": "point",
      "params": {"size": 2, "alpha": 0.6}
    },
    {
      "type": "smooth",
      "params": {"method": "lm", "se": false}
    }
  ],
  "theme": {
    "base": "minimal",
    "customizations": {"figure_size": [12, 6]}
  },
  "labels": {
    "title": "Sensor Readings with Trend Lines",
    "x": "Time",
    "y": "Measurement"
  }
}
```

### Boxplot with Jittered Points

Show both distribution summary and individual data points:

```json
{
  "data_source": {
    "type": "file",
    "path": "./data/experiment.csv"
  },
  "aes": {
    "x": "treatment",
    "y": "response",
    "fill": "treatment"
  },
  "geoms": [
    {
      "type": "boxplot",
      "params": {"alpha": 0.7}
    },
    {
      "type": "jitter",
      "params": {"width": 0.2, "alpha": 0.5, "size": 1}
    }
  ],
  "theme": {
    "base": "bw"
  },
  "labels": {
    "title": "Treatment Effects with Individual Observations"
  }
}
```

## Chat Examples

You can create plots through natural language:

**"Create a histogram of the 'age' column from users.csv"**

**"Make a scatter plot with smooth trend line showing price vs size, colored by category"**

**"Plot a line chart from sales.csv with date on x-axis and revenue on y-axis, faceted by region, using a dark theme"**

**"Create a violin plot comparing distributions of test scores across different schools"**

**"Make a boxplot with individual points overlaid showing temperature by season"**

**"Create a scatter plot with a linear trend line for each category, showing the relationship between hours studied and test scores"**

### Using New Tools

**"Preview the data from sales.csv before plotting"**

**"What themes are available?"**

**"Show me all available plot templates"**

**"Suggest appropriate plot types for my data"**

**"Create a time series plot using the template"**

**"List color palettes in the scientific category"**

**"Export this plot configuration so I can reuse it later"**

**"Load the plot config from my_config.json and use it with a different dataset"**

**"Create a plot from the saved configuration but change the theme to minimal"**

**"Create plots for each category in my dataset"** (batch processing)

**"Filter the data to show only active users, then create a histogram"** (data transformations)

## New Examples

### Using Templates

Create a scatter plot with trend line using a template:

```
"Use the scatter_with_trend template to plot height vs weight from my data"
```

This automatically creates a plot with:
- Scatter points (with transparency)
- Linear regression line
- Confidence interval
- Minimal theme

### Using Color Palettes

```
"Create a bar chart colored using the colorblind-safe Okabe-Ito palette"
```

### Data Transformations

```
"Filter sales data to show only Q4, group by region, sum the revenue, and create a bar chart"
```

This applies transformations before plotting:
1. Filter: `"quarter == 'Q4'"`
2. Group & summarize: by region, sum revenue
3. Plot: bar chart of results

### Batch Processing

```
"Create histogram plots for all numeric columns in my dataset"
```

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
- `fixed` (fixed aspect ratio)
- `trans` (transformed coordinates)

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
