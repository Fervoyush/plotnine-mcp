# Future Enhancement Ideas for Plotnine MCP

This document outlines potential improvements and new features for the plotnine MCP server. Ideas are categorized by type and marked with implementation difficulty and potential impact.

**Legend:**
- 🟢 Easy (1-2 hours)
- 🟡 Medium (3-6 hours)
- 🔴 Hard (1-2 days)
- ⭐ High Impact
- ⚡ Quick Win

---

## ✅ Completed Features

- [x] Multi-layer plots support
- [x] 20+ geometry types
- [x] Multiple data sources (file, URL, inline)
- [x] Comprehensive theming and customization

---

## 🎨 Core Functionality Enhancements

### 1. Plot Templates ⭐ 🟡
**Status:** Not started
**Difficulty:** Medium
**Impact:** High - Great for beginners

Preset configurations for common visualization patterns:

**Templates to include:**
- `time_series` - Line plot with date formatting
- `correlation_matrix` - Heatmap with correlation values
- `distribution_comparison` - Violin/boxplot comparison
- `scatter_with_trend` - Points + regression line + equation
- `category_breakdown` - Bar chart with percentages
- `before_after` - Paired comparison plots

**Implementation approach:**
```python
# In plot_templates.py
TEMPLATES = {
    "time_series": {
        "geoms": [{"type": "line"}],
        "scales": [{"aesthetic": "x", "type": "datetime"}],
        "theme": {"base": "minimal"},
    },
    # ... more templates
}

# New MCP tool: create_plot_from_template
```

**User experience:**
```
"Create a time series plot from sales.csv with date and revenue columns"
→ Automatically applies time series template
```

### 2. Statistical Annotations ⭐ 🟡
**Status:** Not started
**Difficulty:** Medium
**Impact:** High - Adds analytical value

Auto-add statistical information to plots:

**Features:**
- Correlation coefficients on scatter plots
- P-values and significance markers
- Confidence intervals (already supported via smooth)
- Trend line equations
- Summary statistics (mean, median) as text annotations
- Count labels on bar charts

**Implementation approach:**
```python
# Add to plot_builder.py
def add_statistical_annotations(plot, data, geom_type, config):
    if geom_type == "point" and config.get("show_correlation"):
        corr = data[x].corr(data[y])
        plot += geom_text(aes(label=f"r = {corr:.3f}"))
    # ... more stat annotations
```

**Configuration:**
```json
{
  "geoms": [...],
  "annotations": {
    "show_correlation": true,
    "show_equation": true,
    "show_summary_stats": ["mean", "median"]
  }
}
```

### 3. Data Transformations ⭐ 🔴
**Status:** Not started
**Difficulty:** Hard
**Impact:** High - Reduces pre-processing needs

Built-in data manipulation before plotting:

**Transformations to support:**
- Filter: `{"filter": "age > 18"}`
- Group and summarize: `{"group_by": "category", "summarize": {"value": "mean"}}`
- Pivot/reshape: `{"pivot": {"index": "date", "columns": "category"}}`
- Rolling averages: `{"rolling": {"window": 7, "column": "value"}}`
- Cumulative sums: `{"cumsum": "sales"}`

**Implementation approach:**
```python
# In data_transforms.py
def apply_transforms(data: pd.DataFrame, transforms: dict) -> pd.DataFrame:
    if "filter" in transforms:
        data = data.query(transforms["filter"])
    if "group_by" in transforms:
        data = data.groupby(...).agg(...)
    # ... more transforms
    return data
```

**User experience:**
```json
{
  "data_source": {...},
  "transforms": {
    "filter": "sales > 1000",
    "group_by": "region",
    "summarize": {"revenue": "sum"}
  },
  "aes": {...}
}
```

### 4. Animation Support 🔴
**Status:** Not started
**Difficulty:** Hard
**Impact:** Medium - Cool but niche

Create animated visualizations for time-series or transitions:

**Features:**
- Frame-by-frame generation
- GIF/MP4 output
- Smooth transitions between states
- Animation controls (speed, loop)

**Use cases:**
- Time-series evolution over time
- Category transitions
- Parameter sensitivity analysis

**Dependencies:**
- `imageio` for GIF creation
- `ffmpeg` for MP4 (optional)

---

## 🚀 User Experience Improvements

### 5. Smart Plot Suggestions ⭐⚡ 🟡
**Status:** Not started
**Difficulty:** Medium
**Impact:** High - Leverages AI context

Analyze data and recommend appropriate plot types:

**Implementation:**
```python
# New tool: suggest_plot_type
def suggest_plot_type(data: pd.DataFrame, goal: str) -> dict:
    """
    Analyze data characteristics and user goal to suggest plots.

    Returns recommendation with reasoning.
    """
    n_numeric = len(data.select_dtypes(include=[np.number]).columns)
    n_categorical = len(data.select_dtypes(include=['object', 'category']).columns)
    has_time = any(col in str(data.columns) for col in ['date', 'time'])

    suggestions = []

    if has_time and n_numeric >= 1:
        suggestions.append({
            "type": "time_series",
            "reason": "Time-based data detected",
            "geoms": ["line"]
        })

    # ... more logic

    return suggestions
```

**User experience:**
```
User: "What's the best way to visualize this dataset?"
Assistant: Analyzes data and suggests appropriate plot types with reasoning
```

### 6. Data Preview Tool ⚡ 🟢
**Status:** Not started
**Difficulty:** Easy
**Impact:** Medium - Helps debugging

Inspect loaded data before plotting:

**Features:**
- Show first N rows
- Column types and names
- Basic statistics (min, max, mean, etc.)
- Missing value counts
- Data shape

**Implementation:**
```python
# New MCP tool: preview_data
@server.call_tool()
async def preview_data(data_source: dict, rows: int = 5):
    data = load_data(DataSource(**data_source))

    preview = {
        "shape": data.shape,
        "columns": data.dtypes.to_dict(),
        "head": data.head(rows).to_dict('records'),
        "summary": data.describe().to_dict(),
        "missing": data.isnull().sum().to_dict()
    }

    return format_preview(preview)
```

### 7. Plot Configuration Export/Import ⚡ 🟢
**Status:** Not started
**Difficulty:** Easy
**Impact:** Medium - Enables reproducibility

Save and load plot specifications:

**Features:**
- Export plot config as JSON file
- Import saved configurations
- Share configurations between users
- Version control friendly

**Implementation:**
```python
# New tool: export_plot_config
# Saves the exact JSON used to create a plot

# New tool: create_plot_from_config
# Loads a saved JSON configuration
```

### 8. Interactive Preview (Base64) 🟡
**Status:** Not started
**Difficulty:** Medium
**Impact:** Medium - Better UX in chat

Return thumbnail in MCP response:

**Implementation:**
```python
def save_plot(..., return_base64: bool = False):
    # ... save plot

    if return_base64:
        with open(output_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode()
        return {
            "path": output_path,
            "preview": f"data:image/png;base64,{img_data}"
        }
```

**Note:** Check MCP spec for image support

### 9. Better Error Messages ⚡ 🟢
**Status:** Partially done
**Difficulty:** Easy
**Impact:** High - Improves all users' experience

Enhanced error handling with suggestions:

**Improvements:**
- Column name suggestions (fuzzy matching)
- Example corrections
- Data type compatibility checks
- Common mistake patterns

**Implementation:**
```python
class SmartErrorHandler:
    def suggest_column(self, column: str, available: list[str]) -> str:
        # Use difflib for fuzzy matching
        matches = difflib.get_close_matches(column, available)
        if matches:
            return f"Column '{column}' not found. Did you mean: {matches[0]}?"
        return f"Column '{column}' not found. Available: {', '.join(available)}"
```

---

## 🔧 Advanced Features

### 10. Custom Color Palettes Library 🟡
**Status:** Not started
**Difficulty:** Medium
**Impact:** Medium - Aesthetic control

Named palette library and custom schemes:

**Features:**
- Built-in palettes (viridis, colorbrewer, seaborn)
- Brand color schemes
- Accessibility-focused (colorblind-safe)
- Custom palette builder

**Implementation:**
```python
PALETTES = {
    "viridis": ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde724"],
    "colorblind_safe": [...],
    "corporate": {
        "primary": "#1f77b4",
        "secondary": "#ff7f0e",
        # ...
    }
}

# New tool: list_color_palettes
# New parameter in create_plot: {"palette": "viridis"}
```

### 11. Plot Composition (Subplots) 🔴
**Status:** Not started
**Difficulty:** Hard
**Impact:** High - Report generation

Combine multiple plots into grids:

**Features:**
- Grid layouts (2x2, 3x1, etc.)
- Shared axes and legends
- Custom positioning
- Overall title and annotations

**Challenge:** plotnine doesn't have native subplot support like matplotlib

**Possible approach:**
- Save individual plots
- Use PIL/matplotlib to combine
- Or return configuration for external tool

### 12. Batch Processing 🟡
**Status:** Not started
**Difficulty:** Medium
**Impact:** Medium - Automation

Generate multiple plots from one dataset:

**Use cases:**
- "Create scatter plots for all numeric variable pairs"
- "Generate histograms for each numeric column"
- "Plot time series for each category separately"

**Implementation:**
```python
# New tool: batch_create_plots
{
  "data_source": {...},
  "batch_type": "pairwise_scatter",
  "columns": ["age", "height", "weight"],
  "output_pattern": "plot_{col1}_vs_{col2}.png"
}
```

### 13. Plugin Architecture 🔴
**Status:** Not started
**Difficulty:** Hard
**Impact:** Low - For advanced users

Allow custom extensions:

**Features:**
- Custom geom definitions
- User-defined transformations
- Theme extensions
- Custom statistics

**Implementation:**
```python
# plugin system
class PlotPlugin:
    def register_geom(self, name: str, geom_class):
        GEOM_MAP[name] = geom_class

    def register_transform(self, name: str, transform_func):
        TRANSFORMS[name] = transform_func
```

### 14. Streaming Data & Large Datasets 🔴
**Status:** Not started
**Difficulty:** Hard
**Impact:** Medium - Scalability

Handle data too large for memory:

**Features:**
- Data sampling strategies
- Chunked processing
- Progressive rendering
- Connection to databases

**Implementation:**
- Use pandas chunking
- Implement smart sampling
- Add progress indicators

---

## 📊 Integration & Output

### 15. Additional Output Formats 🟡
**Status:** Partial (PNG, PDF, SVG done)
**Difficulty:** Medium
**Impact:** Medium

**New formats:**
- **HTML with interactivity** (plotly backend)
- **Jupyter notebook cells**
- **LaTeX/TikZ** for publications
- **PowerPoint slides** (via python-pptx)

**Implementation:**
```python
# For HTML/interactive
output_config = {
    "format": "html",
    "interactive": true,
    "backend": "plotly"  # Convert plotnine to plotly
}
```

### 16. Database Connections 🟡
**Status:** Not started
**Difficulty:** Medium
**Impact:** Medium

Direct database queries:

**Supported databases:**
- PostgreSQL
- MySQL
- SQLite
- BigQuery (via pandas-gbq)

**Implementation:**
```json
{
  "data_source": {
    "type": "database",
    "connection_string": "postgresql://...",
    "query": "SELECT * FROM sales WHERE date > '2024-01-01'"
  }
}
```

**Security considerations:**
- Credential management
- Query sanitization
- Connection pooling

### 17. API Data Sources 🟡
**Status:** Not started
**Difficulty:** Medium
**Impact:** Medium

Integrations with popular APIs:

**APIs to support:**
- REST APIs (generic)
- Google Sheets
- Airtable
- GitHub stats
- Weather APIs

**Implementation:**
```json
{
  "data_source": {
    "type": "google_sheets",
    "sheet_id": "...",
    "credentials": "path/to/creds.json"
  }
}
```

### 18. Real-time Dashboard Mode 🔴
**Status:** Not started
**Difficulty:** Hard
**Impact:** Low - Different use case

Live updating visualizations:

**Features:**
- Auto-refresh at intervals
- WebSocket support
- Multiple plot monitoring
- Alert conditions

**Note:** This might be beyond MCP scope

---

## 🤖 AI-Powered Features

### 19. Natural Language Color Descriptions 🟡
**Status:** Not started
**Difficulty:** Medium
**Impact:** Low - Nice to have

Convert text descriptions to colors:

**Examples:**
- "make it warmer" → Shift palette toward reds/oranges
- "corporate professional" → Blues and grays
- "sunset theme" → Orange to purple gradient

**Implementation:**
- Use Claude/LLM to interpret requests
- Map to color palettes
- Apply to plot

### 20. Style Transfer 🔴
**Status:** Not started
**Difficulty:** Hard
**Impact:** Low - Experimental

Apply visual style from example images:

**Concept:**
- User provides example plot image
- Extract colors, fonts, spacing
- Apply to new plots

**Challenge:** Very experimental, low priority

### 21. Auto-Caption Generation 🟡
**Status:** Not started
**Difficulty:** Medium
**Impact:** Medium - Accessibility

Generate descriptive captions:

**Features:**
- Summary of what plot shows
- Key insights (trends, outliers)
- Accessibility descriptions
- Alt text for images

**Implementation:**
```python
# Analyze plot data and configuration
# Use LLM to generate caption
caption = f"Scatter plot showing {insight} with correlation of {corr:.2f}"
```

---

## 🎯 Recommended Implementation Order

### Phase 1: Quick Wins (Next session)
1. ⚡ Data preview tool
2. ⚡ Better error messages
3. ⚡ Plot config export/import
4. ⚡ List themes tool

**Time estimate:** 4-6 hours
**Impact:** Immediate UX improvements

### Phase 2: High Impact Features
1. ⭐ Plot templates
2. ⭐ Statistical annotations
3. ⭐ Smart plot suggestions
4. Custom color palettes

**Time estimate:** 2-3 days
**Impact:** Major functionality boost

### Phase 3: Advanced Features
1. Data transformations
2. Batch processing
3. Additional output formats
4. Database connections

**Time estimate:** 1 week
**Impact:** Professional-grade tool

### Phase 4: Experimental
1. Animation support
2. Plot composition
3. AI-powered features
4. Plugin architecture

**Time estimate:** 2+ weeks
**Impact:** Cutting-edge features

---

## 📝 Notes & Considerations

### Technical Debt to Address
- Add comprehensive error handling throughout
- Improve test coverage (currently basic)
- Add type hints consistently
- Performance optimization for large datasets

### Documentation Needs
- Video tutorials
- API reference
- Contributing guidelines
- Cookbook with common patterns

### Community Building
- Submit to MCP registry
- Create example gallery
- Blog post / announcement
- Discord/Slack community

### Alternative Approaches
- **Plotly backend:** For interactivity (breaks plotnine compatibility)
- **Altair integration:** Vega-based alternative
- **Seaborn wrapper:** Simplified API on top

---

## 🤝 Contributing Ideas

We welcome suggestions! To propose new features:

1. Create an issue on GitHub
2. Describe the use case and benefit
3. Provide example usage
4. Tag with `enhancement` label

---

## 📚 Resources for Implementation

### Libraries to Consider
- `scikit-misc` - For loess smoothing
- `imageio` - Animation support
- `sqlalchemy` - Database connections
- `plotly` - Interactive plots
- `seaborn` - Additional palettes
- `geopandas` - Map visualizations (future)

### Documentation References
- [plotnine docs](https://plotnine.readthedocs.io/)
- [ggplot2 reference](https://ggplot2.tidyverse.org/)
- [MCP specification](https://modelcontextprotocol.io/)
- [pandas API](https://pandas.pydata.org/docs/)

---

**Last Updated:** 2025-11-06
**Current Version:** v0.1.0 (development with multi-layer support)
**Next Milestone:** v1.0.0 - Official release (when ready)
