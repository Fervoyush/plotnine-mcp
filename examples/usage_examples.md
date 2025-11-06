# Plotnine MCP Usage Examples

This document provides practical examples of using the plotnine MCP server through chat.

## Simple Examples

### 1. Basic Scatter Plot

**User**: "Create a scatter plot from examples/sample_data.csv with x on the x-axis and y on the y-axis"

**Expected behavior**: Creates a simple scatter plot showing the relationship between x and y.

### 2. Colored Scatter Plot

**User**: "Make a scatter plot from examples/sample_data.csv with x vs y, colored by category"

**Expected behavior**: Creates a scatter plot with points colored according to the category column.

### 3. Line Plot

**User**: "Create a line plot from examples/sample_data.csv showing x vs y"

**Expected behavior**: Creates a line plot connecting the points in order.

## Intermediate Examples

### 4. Customized Theme

**User**: "Plot x vs y from examples/sample_data.csv as points, use a minimal theme"

**Expected behavior**: Creates a scatter plot with the minimal theme applied.

### 5. Multiple Aesthetics

**User**: "Create a scatter plot from examples/sample_data.csv with x on x-axis, y on y-axis, colored by category, and sized by the size column"

**Expected behavior**: Creates a scatter plot with both color and size aesthetics mapped.

### 6. Bar Chart

**User**: "Make a bar chart from examples/sample_data.csv showing average y values for each category"

**Expected behavior**: Creates a bar chart summarizing data by category.

## Advanced Examples

### 7. Faceted Plot

**User**: "Create a scatter plot from examples/sample_data.csv with x vs y, faceted by category"

**Expected behavior**: Creates separate scatter plots for each category in a grid layout.

### 8. Styled Plot with Labels

**User**: "Create a scatter plot from examples/sample_data.csv with:
- x on x-axis, y on y-axis
- colored by category
- minimal theme with figure size 10x6
- title 'Sample Data Analysis'
- x-axis label 'X Values'
- y-axis label 'Y Values'"

**Expected behavior**: Creates a fully styled scatter plot with custom labels and theme.

### 9. Plot with Smooth Trend

**User**: "Make a scatter plot from examples/sample_data.csv with x vs y, add a smooth trend line"

**Expected behavior**: Creates a scatter plot with a smoothed trend line overlay.

### 10. Custom Output

**User**: "Create a scatter plot from examples/sample_data.csv with x vs y, save as PDF with filename 'my_plot.pdf' in the output directory"

**Expected behavior**: Creates the plot and saves it as a PDF with the specified filename.

## Complex Examples

### 11. Multi-layer Plot

**User**: "Create a plot from examples/sample_data.csv with:
- Points showing x vs y colored by category
- Line connecting the points
- Minimal theme
- Figure size 12x8
- Title 'Combined Point and Line Plot'"

**Note**: This requires multiple geom layers. Currently, the server supports one geom per plot. To achieve this, you'd need to call the tool twice or enhance the server to support multiple geoms.

### 12. Inline Data Example

**User**: "Create a bar chart with this data: [{'name': 'A', 'value': 10}, {'name': 'B', 'value': 20}, {'name': 'C', 'value': 15}], with name on x-axis and value on y-axis"

**Expected behavior**: Creates a bar chart from the inline JSON data.

### 13. Histogram

**User**: "Create a histogram of the y column from examples/sample_data.csv with 5 bins"

**Expected behavior**: Creates a histogram showing the distribution of y values.

### 14. Boxplot by Category

**User**: "Make a boxplot from examples/sample_data.csv showing y values grouped by category"

**Expected behavior**: Creates side-by-side boxplots for each category.

## Testing Instructions

1. Install the MCP server following the README instructions
2. Restart Claude Desktop
3. Try each example by typing the user message
4. Verify that the plots are created in the `output` directory
5. Check that the plots match the expected behavior

## Tips for Natural Language Usage

The server is designed to understand natural plot requests. You can:

- Use synonyms: "scatter plot", "scatter chart", "point plot"
- Be concise: "plot x vs y" instead of full parameter specifications
- Add constraints: "with a dark theme", "save as PDF", "figure size 10x6"
- Combine features: "scatter plot with smooth line, faceted by category, minimal theme"

## Known Limitations

1. Single geom per plot (cannot overlay multiple geometries in one call)
2. Complex statistical transformations may require explicit configuration
3. Custom color palettes require scale configuration
4. Advanced theme customizations need explicit parameter specification

## Future Enhancements

- Support for multiple geoms in a single plot
- Animation support for time series
- Interactive plots with plotly backend
- Preset plot templates for common use cases
- Data transformation utilities
