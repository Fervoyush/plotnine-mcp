# Implementation Reference

This document provides a comprehensive technical reference for the plotnine MCP server's current implementation. It covers architecture, design decisions, code organization, and implementation details for future developers.

**Version:** 0.2.0
**Last Updated:** 2025-11-06

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Module Structure](#module-structure)
- [Data Flow](#data-flow)
- [Implemented Features](#implemented-features)
- [Design Decisions](#design-decisions)
- [Testing Strategy](#testing-strategy)
- [Known Limitations](#known-limitations)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────┐
│   MCP Client    │  (Claude Desktop, Cursor, VSCode)
│  (AI Assistant) │
└────────┬────────┘
         │ MCP Protocol (stdio)
         ↓
┌─────────────────┐
│  server.py      │  Main MCP Server
│  - Tool defs    │  - Handles tool registration
│  - Handlers     │  - Processes requests
└────────┬────────┘
         │
    ┌────┴─────────────────┬──────────────┐
    ↓                      ↓              ↓
┌──────────┐      ┌─────────────┐  ┌──────────────┐
│data_     │      │plot_        │  │schemas.py    │
│loader.py │      │builder.py   │  │- Pydantic    │
│          │      │             │  │  models      │
└──────────┘      └─────────────┘  └──────────────┘
    │                    │
    ↓                    ↓
┌──────────┐      ┌─────────────┐
│ pandas   │      │  plotnine   │
│DataFrame │      │   (ggplot)  │
└──────────┘      └─────────────┘
```

### Technology Stack

- **Python:** 3.10+
- **MCP SDK:** 1.0.0+ (Model Context Protocol)
- **Core Libraries:**
  - `plotnine` 0.13.0+ (visualization)
  - `pandas` 2.0.0+ (data handling)
  - `pydantic` 2.0.0+ (validation)
  - `requests` 2.31.0+ (HTTP data sources)
  - `pillow` 10.0.0+ (image handling)

### Design Philosophy

1. **Grammar of Graphics:** Follow ggplot2's layered approach
2. **Modular:** Each component is independent and testable
3. **Type-Safe:** Use Pydantic for validation
4. **Backward Compatible:** New features don't break existing usage
5. **AI-Friendly:** Clear tool descriptions and error messages

---

## Module Structure

### `/src/plotnine_mcp/`

#### `server.py` (450 lines)

**Purpose:** Main MCP server implementation

**Key Components:**

```python
server = Server("plotnine-mcp")

@server.list_tools()
async def list_tools() -> list[Tool]:
    # Returns tool definitions
    # Tools: create_plot, list_geom_types

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    # Routes to specific handlers
    # Handles: create_plot_handler, list_geom_types_handler

async def create_plot_handler(arguments: dict) -> list[TextContent]:
    # Main plot creation logic
    # 1. Parse and validate arguments
    # 2. Load data
    # 3. Build plot
    # 4. Save plot
    # 5. Return result
```

**Tool Definitions:**

1. **create_plot**
   - **Inputs:** data_source, aes, geom/geoms, scales, theme, facets, labels, coords, stats, output
   - **Output:** TextContent with file path and summary
   - **Validation:** Via Pydantic schemas

2. **list_geom_types**
   - **Inputs:** None
   - **Output:** List of available geometries with descriptions

**Error Handling:**
- `DataLoadError` → User-friendly data loading errors
- `PlotBuildError` → Plot construction errors with suggestions
- Generic exceptions → Caught and formatted

#### `data_loader.py` (165 lines)

**Purpose:** Load data from various sources into pandas DataFrames

**Key Functions:**

```python
def load_data(data_source: DataSource) -> pd.DataFrame:
    """Main entry point for data loading"""
    # Dispatches to specific loaders based on type

def _load_inline_data(data_source: DataSource) -> pd.DataFrame:
    """Load from JSON array"""
    return pd.DataFrame(data_source.data)

def _load_file_data(data_source: DataSource) -> pd.DataFrame:
    """Load from local file"""
    # - Resolves path
    # - Auto-detects format
    # - Calls appropriate pandas reader

def _load_url_data(data_source: DataSource) -> pd.DataFrame:
    """Load from URL"""
    # - Fetches with requests
    # - Auto-detects format
    # - Reads from BytesIO

def _detect_format_from_path(path: Path) -> str:
    """Detect file format from extension"""
    # Maps: .csv → "csv", .json → "json", etc.

def _read_file_by_format(source: Any, format_type: str) -> pd.DataFrame:
    """Read file based on detected format"""
    # Calls: pd.read_csv, pd.read_json, pd.read_parquet, pd.read_excel
```

**Supported Formats:**
- **CSV:** via `pandas.read_csv()`
- **JSON:** via `pandas.read_json()`
- **Parquet:** via `pandas.read_parquet()` (requires pyarrow)
- **Excel:** via `pandas.read_excel()` (requires openpyxl)

**Auto-Detection:**
- File: Based on extension (.csv, .json, .parquet, .xlsx)
- URL: Based on URL path or Content-Type header
- Fallback: Defaults to CSV

**Error Cases:**
- File not found
- Unsupported format
- Network errors (URLs)
- Malformed data

#### `plot_builder.py` (475 lines)

**Purpose:** Build plotnine plots from configuration

**Key Components:**

```python
GEOM_MAP = {
    "point": geom_point,
    "line": geom_line,
    "bar": geom_bar,
    # ... 20+ geometries
}

def build_plot(
    data: pd.DataFrame,
    aes_config: Aesthetics,
    geom_config: Optional[GeomConfig] = None,
    geom_configs: Optional[list[GeomConfig]] = None,
    # ... other optional configs
) -> ggplot:
    """
    Main plot building function

    Process:
    1. Handle backward compatibility (geom → geom_configs)
    2. Build aesthetics from config
    3. Create base ggplot object
    4. Add geometry layers (single or multiple)
    5. Add statistical transformations
    6. Apply scales
    7. Add facets
    8. Add labels
    9. Apply coordinate system
    10. Apply theme
    """

def _build_aesthetics(aes_config: Aesthetics) -> aes:
    """Convert Aesthetics schema to plotnine aes object"""
    # Maps: x, y, color, fill, size, alpha, shape, linetype, group

def _build_geom(geom_config: GeomConfig):
    """Convert GeomConfig to plotnine geom"""
    # Looks up in GEOM_MAP
    # Applies params

def _build_scale(scale_config: ScaleConfig):
    """Build scale from configuration"""
    # Maps to: scale_x_continuous, scale_y_log10, etc.

def _build_theme(theme_config: ThemeConfig):
    """Build theme from configuration"""
    # Base themes: gray, bw, minimal, classic, dark, light, void
    # Applies customizations: figure_size, legend_position, etc.

def _build_facet(facet_config: FacetConfig):
    """Build facet from configuration"""
    # Types: wrap, grid
    # Generates formula for facet_grid

def _build_labels(labels_config: LabelsConfig):
    """Add plot labels"""
    # title, x, y, caption, subtitle

def _build_coord(coord_config: CoordConfig):
    """Set coordinate system"""
    # Types: cartesian, flip, fixed, trans

def save_plot(plot: ggplot, output_config: OutputConfig) -> dict:
    """
    Save plot to file

    Process:
    1. Create output directory
    2. Generate filename (or use provided)
    3. Call plot.save() with dimensions and DPI
    4. Return metadata
    """
```

**Geometry Mapping:**
All plotnine geoms are imported and mapped:
- Basic: point, line, bar, col, histogram
- Distribution: boxplot, violin, density
- Specialized: tile, text, errorbar, ribbon, path, polygon
- Reference: hline, vline, abline
- Smoothing: smooth, area, jitter

**Multi-Layer Support (v0.2.0):**
```python
# Backward compatible handling
if geom_config and not geom_configs:
    geom_configs = [geom_config]  # Convert single to list

# Layer multiple geoms
for geom_cfg in geom_configs:
    plot = plot + _build_geom(geom_cfg)
```

**Theme Customization:**
Supports nested customizations via `theme()` function:
- `figure_size`: tuple
- `legend_position`: string
- `panel_background`, `plot_background`: element_rect
- `text`, `axis_text`, `axis_title`: element_text

#### `schemas.py` (140 lines)

**Purpose:** Pydantic models for type validation

**Key Schemas:**

```python
class DataSource(BaseModel):
    """Data source configuration"""
    type: Literal["file", "url", "inline"]
    path: Optional[str] = None  # For file/url
    data: Optional[list[dict]] = None  # For inline
    format: Optional[Literal["csv", "json", "parquet", "excel"]] = "csv"

class Aesthetics(BaseModel):
    """Aesthetic mappings"""
    x: Optional[str] = None
    y: Optional[str] = None
    color: Optional[str] = None
    fill: Optional[str] = None
    size: Optional[str] = None
    alpha: Optional[str] = None
    shape: Optional[str] = None
    linetype: Optional[str] = None
    group: Optional[str] = None

class GeomConfig(BaseModel):
    """Geometry configuration"""
    type: str  # Geometry name
    params: dict[str, Any] = Field(default_factory=dict)

class ScaleConfig(BaseModel):
    """Scale configuration"""
    aesthetic: str  # x, y, color, fill, etc.
    type: str  # continuous, discrete, log10, etc.
    params: dict[str, Any] = Field(default_factory=dict)

class ThemeConfig(BaseModel):
    """Theme configuration"""
    base: str = "gray"  # Base theme name
    customizations: dict[str, Any] = Field(default_factory=dict)

class FacetConfig(BaseModel):
    """Faceting configuration"""
    type: Literal["wrap", "grid"] = "wrap"
    facets: Optional[str] = None  # Formula
    cols: Optional[str] = None  # For grid
    rows: Optional[str] = None  # For grid
    params: dict[str, Any] = Field(default_factory=dict)

class LabelsConfig(BaseModel):
    """Plot labels"""
    title: Optional[str] = None
    x: Optional[str] = None
    y: Optional[str] = None
    caption: Optional[str] = None
    subtitle: Optional[str] = None

class CoordConfig(BaseModel):
    """Coordinate system"""
    type: str = "cartesian"
    params: dict[str, Any] = Field(default_factory=dict)

class StatConfig(BaseModel):
    """Statistical transformation"""
    type: str  # smooth, bin, density, summary
    params: dict[str, Any] = Field(default_factory=dict)

class OutputConfig(BaseModel):
    """Output configuration"""
    format: Literal["png", "pdf", "svg"] = "png"
    filename: Optional[str] = None
    width: float = 8  # inches
    height: float = 6  # inches
    dpi: int = 300
    directory: str = "./output"
```

**Validation Benefits:**
- Type checking at runtime
- Clear error messages
- Auto-generated JSON schema for MCP
- IDE autocomplete support

#### `__init__.py` (5 lines)

Simple package initialization with version number.

---

## Data Flow

### Complete Request Flow

```
1. User Request (via AI Assistant)
   ↓
2. MCP Client → Server (stdio transport)
   ↓
3. server.call_tool() receives request
   ↓
4. create_plot_handler() processes arguments
   ↓
5. Pydantic Validation
   - DataSource → data_loader.py
   - Aesthetics, GeomConfig(s), etc. → plot_builder.py
   ↓
6. Data Loading
   load_data() → pandas DataFrame
   ↓
7. Plot Building
   build_plot() → ggplot object
   - Build aesthetics
   - Add geom layer(s)  ← Multi-layer support!
   - Apply scales
   - Add facets
   - Set labels
   - Apply theme
   - Set coordinates
   ↓
8. Plot Saving
   save_plot() → File on disk
   ↓
9. Response
   TextContent with metadata
   ↓
10. User sees result
```

### Error Handling Flow

```
Try:
    Load data
    ↓ DataLoadError
    → User-friendly message with suggestions

Try:
    Build plot
    ↓ PlotBuildError
    → Column/geom/config error with hints

Try:
    Save plot
    ↓ PlotBuildError / IOError
    → File system error message

Catch all:
    → Generic error with full traceback context
```

---

## Implemented Features

### ✅ Data Sources

**File-based:**
- [x] CSV files (`pd.read_csv`)
- [x] JSON files (`pd.read_json`)
- [x] Parquet files (`pd.read_parquet`) - optional dependency
- [x] Excel files (`pd.read_excel`) - optional dependency

**Network-based:**
- [x] HTTP/HTTPS URLs
- [x] Auto-detection from Content-Type header

**Inline:**
- [x] JSON arrays passed directly in MCP call

**Features:**
- [x] Format auto-detection
- [x] Path resolution (relative and absolute)
- [x] User home directory expansion (`~`)
- [x] Comprehensive error messages

### ✅ Geometries (20+ types)

**Basic:**
- [x] point - Scatter points
- [x] line - Connected lines
- [x] bar - Bar chart (count stat)
- [x] col - Column chart (identity stat)
- [x] path - Path in data order

**Distribution:**
- [x] histogram - Binned continuous data
- [x] density - Kernel density estimation
- [x] boxplot - Box and whisker
- [x] violin - Violin plots

**Smoothing:**
- [x] smooth - Conditional means (supports lm, loess)
- [x] area - Filled area under curve

**Specialized:**
- [x] tile - Heatmap tiles
- [x] text - Text annotations
- [x] jitter - Jittered points
- [x] errorbar - Error bars
- [x] ribbon - Confidence ribbons
- [x] polygon - Filled polygons

**Reference:**
- [x] hline - Horizontal line
- [x] vline - Vertical line
- [x] abline - Diagonal line

### ✅ Aesthetics

All ggplot2 aesthetics supported:
- [x] x, y - Position
- [x] color - Point/line color
- [x] fill - Fill color
- [x] size - Point/line size
- [x] alpha - Transparency
- [x] shape - Point shape
- [x] linetype - Line style
- [x] group - Grouping for lines/paths

### ✅ Scales

**Position scales:**
- [x] continuous
- [x] discrete
- [x] log10
- [x] sqrt
- [x] datetime

**Color scales:**
- [x] gradient (continuous)
- [x] discrete
- [x] brewer (ColorBrewer palettes)

**Implementation:**
- Dynamic scale name construction: `scale_{aesthetic}_{type}`
- Parameter passing to plotnine scale functions
- Full support for limits, breaks, labels

### ✅ Themes

**Base themes:**
- [x] gray (default)
- [x] bw (black and white)
- [x] minimal
- [x] classic
- [x] dark
- [x] light
- [x] void

**Customizations:**
- [x] figure_size
- [x] legend_position
- [x] legend_direction
- [x] panel_background (via element_rect)
- [x] plot_background (via element_rect)
- [x] text (via element_text)
- [x] axis_text (via element_text)
- [x] axis_title (via element_text)

### ✅ Faceting

**Types:**
- [x] facet_wrap - Single variable wrapping
- [x] facet_grid - Two-variable grid

**Features:**
- [x] Formula support (`~ variable`, `row ~ col`)
- [x] Custom parameters (ncol, scales, etc.)

### ✅ Coordinate Systems

- [x] cartesian (default)
- [x] flip (swap x and y)
- [x] fixed (fixed aspect ratio)
- [x] trans (coordinate transformation)

**Note:** `coord_polar` not available in plotnine 0.13+

### ✅ Labels

All label types supported:
- [x] title
- [x] x-axis label
- [x] y-axis label
- [x] caption
- [x] subtitle

### ✅ Statistical Transformations

- [x] smooth (various methods: lm, loess, etc.)
- [x] bin (for histograms)
- [x] density (kernel density)
- [x] summary (aggregations)

**Note:** Most stats are implicit in geoms

### ✅ Output Formats

- [x] PNG (default, 300 DPI)
- [x] PDF (vector)
- [x] SVG (vector)

**Configuration:**
- [x] Custom dimensions (width, height in inches)
- [x] Custom DPI (raster formats)
- [x] Custom filename
- [x] Custom output directory
- [x] Auto-generated filenames (UUID-based)

### ✅ Multi-Layer Plots (v0.2.0)

**Implementation:**
```python
# Accept both single geom and array of geoms
geom_config: Optional[GeomConfig] = None
geom_configs: Optional[list[GeomConfig]] = None

# Backward compatibility conversion
if geom_config and not geom_configs:
    geom_configs = [geom_config]

# Layer all geoms
for geom_cfg in geom_configs:
    plot = plot + _build_geom(geom_cfg)
```

**Use cases:**
- Scatter + smooth trend lines
- Boxplot + jittered points
- Line + points
- Histogram + density curve
- Area + line border
- Any combination!

**Backward compatibility:**
- Old code using `geom` still works
- New code can use `geoms` array
- No breaking changes

---

## Design Decisions

### Why Pydantic for Validation?

**Pros:**
- Type safety at runtime
- Clear error messages
- Auto-generates JSON schemas
- IDE support
- Nested validation

**Alternative considered:** Manual dict validation
**Decision:** Pydantic provides better UX and maintainability

### Why stdio Transport?

**Reason:** MCP specification standard
**Benefit:** Works with all MCP clients (Claude Desktop, Cursor, VSCode)
**Alternative:** HTTP (not standard for MCP)

### Why Separate Modules?

**Rationale:**
- **data_loader**: Independent data loading logic, reusable
- **plot_builder**: Pure plotnine logic, no MCP coupling
- **schemas**: Validation layer, clear contracts
- **server**: MCP-specific logic, thin orchestration layer

**Benefit:** Testable, maintainable, clear separation of concerns

### Why Default to ./output Directory?

**Reasoning:**
- Predictable location
- Keeps project organized
- Easy to .gitignore
- User can override

**Alternative:** System temp directory
**Decision:** Local output for user control

### Why Support Both geom and geoms?

**Reasoning:**
- Backward compatibility (v0.1.0 used `geom`)
- Intuitive for single-layer plots
- Explicit for multi-layer plots

**Implementation:**
```python
# Simple internal conversion
if geom_config and not geom_configs:
    geom_configs = [geom_config]
```

### Why Auto-generate Filenames?

**Reasoning:**
- Users don't always want to name files
- UUID prevents collisions
- Still allows custom names

**Format:** `plot_{8-char-uuid}.{format}`
**Example:** `plot_a3f2b9c1.png`

### Why Not Support coord_polar?

**Reason:** Removed in plotnine 0.13+
**Alternative:** Use `coord_trans` for transformations
**Note:** Documented in README to avoid confusion

---

## Testing Strategy

### Current Test Suite (`test_basic.py`)

**Test Coverage:**

1. **test_inline_data_scatter_plot()**
   - Tests: Inline data source, scatter plot, basic theming
   - Validates: Data loading, plot building, file saving

2. **test_file_data_line_plot()**
   - Tests: CSV file loading, line plot, custom theme
   - Validates: File reading, theme customization

3. **test_bar_plot()**
   - Tests: Bar chart with fill aesthetic
   - Validates: Column chart (geom_col)

4. **test_multi_layer_plot()**
   - Tests: Multi-layer (point + smooth)
   - Validates: geom_configs array, layering

5. **test_boxplot_with_jitter()**
   - Tests: Boxplot + jitter overlay
   - Validates: Multiple geom types, transparency

**Test Approach:**
- Integration tests (end-to-end)
- Direct module imports (not via MCP)
- File output verification
- Visual inspection supported

**Coverage Gaps:**
- Unit tests for individual functions
- Error case testing
- Scale/facet/coord testing
- URL data source testing
- All geometry types

### Running Tests

```bash
python test_basic.py
```

**Expected output:**
```
============================================================
Running Plotnine MCP Basic Tests
============================================================
Test 1: Simple scatter plot with inline data...
  ✓ Data loaded: 5 rows
  ✓ Plot built successfully
  ✓ Plot saved to: /path/to/output/test_scatter.png
...
All tests passed! ✓
```

### Test Data

**Sample file:** `examples/sample_data.csv`
```csv
x,y,category,size
1,2.3,A,10
2,4.1,A,15
...
```

### Future Testing Needs

- [ ] Unit tests for each module
- [ ] Mock MCP client tests
- [ ] Error handling tests
- [ ] Performance benchmarks
- [ ] Visual regression tests (compare images)
- [ ] CI/CD pipeline (GitHub Actions)

---

## Known Limitations

### 1. Single Plot per Call

**Limitation:** Cannot create multiple independent plots in one MCP call

**Workaround:** Make multiple MCP calls

**Future:** Batch processing feature planned

### 2. No Interactive Plots

**Limitation:** Static images only (PNG, PDF, SVG)

**Reason:** plotnine is not interactive

**Future:** Consider plotly backend option

### 3. Limited Data Transformations

**Limitation:** No built-in filtering, grouping, aggregation

**Workaround:** Pre-process data before plotting

**Future:** Data transformation module planned

### 4. Memory Constraints for Large Data

**Limitation:** Entire dataset loaded into memory

**Impact:** Large files (>1GB) may fail

**Future:** Streaming/chunking support planned

### 5. No Database Support

**Limitation:** Cannot query databases directly

**Workaround:** Export to CSV/JSON first

**Future:** SQLAlchemy integration planned

### 6. Theme Customization Limitations

**Limitation:** Not all plotnine theme elements exposed

**Reason:** Simplified API for AI interactions

**Workaround:** Limited set covers most use cases

### 7. No Plot Composition

**Limitation:** Cannot combine multiple plots into subplots

**Reason:** plotnine doesn't support subplots natively

**Future:** External composition tool or matplotlib backend

### 8. Error Messages Could Be Better

**Limitation:** Some plotnine errors are cryptic

**Status:** Partially mitigated with try-catch

**Future:** Smart error handler with suggestions

### 9. No Animation Support

**Limitation:** Static plots only

**Future:** Frame-by-frame generation planned

### 10. Limited Statistical Annotations

**Limitation:** No auto-generated correlations, p-values, etc.

**Workaround:** Manual text annotations

**Future:** Statistical annotation module planned

---

## Code Quality & Standards

### Type Hints

**Status:** Partial coverage
- Pydantic models: Full
- Public functions: Full
- Private functions: Partial

**Goal:** 100% coverage for public API

### Documentation

**Docstrings:**
- Modules: Yes
- Public functions: Yes
- Private functions: Partial

**Format:** Google style

### Code Style

**Formatter:** Black (line length 100)
**Linter:** Ruff
**Import sorting:** Not enforced yet

### Dependencies

**Philosophy:** Minimal, well-maintained
**Lock file:** No (pip-tools recommended)
**Virtual env:** Recommended

---

## Performance Characteristics

### Benchmarks (Informal)

**Test environment:**
- MacBook M1
- Python 3.12
- Dataset: 10 rows

**Results:**
- Simple scatter: ~1-2 seconds
- Multi-layer: ~2-3 seconds
- Faceted plot: ~2-4 seconds

**Bottlenecks:**
- plotnine rendering (most time)
- File I/O (negligible)
- Data loading (depends on source)

### Optimization Opportunities

1. **Caching:** Reuse loaded data for multiple plots
2. **Lazy evaluation:** Defer rendering until needed
3. **Parallel processing:** For batch operations
4. **Data sampling:** For large datasets

---

## Deployment & Distribution

### Package Structure

```
plotnine-mcp/
├── pyproject.toml          # Package metadata & dependencies
├── README.md               # User documentation
├── LICENSE                 # MIT License
├── IMPLEMENTATION_REFERENCE.md  # This document
├── FUTURE_ENHANCEMENTS.md  # Roadmap
├── src/
│   └── plotnine_mcp/
│       ├── __init__.py
│       ├── server.py
│       ├── data_loader.py
│       ├── plot_builder.py
│       └── schemas.py
├── examples/
│   ├── sample_data.csv
│   └── usage_examples.md
├── output/                 # Generated plots (gitignored)
│   └── .gitkeep
└── test_basic.py          # Test suite
```

### Installation Methods

**Development install:**
```bash
pip install -e .
```

**Regular install:**
```bash
pip install .
```

**With optional dependencies:**
```bash
pip install -e ".[full]"  # Adds pyarrow, openpyxl
```

### Entry Point

**Defined in pyproject.toml:**
```toml
[project.scripts]
plotnine-mcp = "plotnine_mcp.server:main"
```

**Can be run as:**
```bash
plotnine-mcp  # If installed
python -m plotnine_mcp.server  # Module execution
```

### MCP Configuration

**Claude Desktop** (`claude_desktop_config.json`):
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

**Cursor** (`.cursor/mcp.json`):
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

---

## Version History

### v0.2.0 (2025-11-06)

**Major Features:**
- ✨ Multi-layer plot support
- 📝 Enhanced documentation

**Changes:**
- Added `geoms` array parameter
- Backward compatible with `geom` parameter
- Two new test cases
- Updated README with multi-layer examples

**Files changed:**
- `server.py`: Added geoms schema and handler logic
- `plot_builder.py`: Modified build_plot() for multi-layer
- `test_basic.py`: Added multi-layer tests
- `README.md`: Added examples and feature highlight

### v0.1.0 (2025-11-06)

**Initial Release:**
- ✅ MCP server implementation
- ✅ 20+ geometry types
- ✅ Multiple data sources
- ✅ Full ggplot2 feature parity
- ✅ Documentation and examples
- ✅ Basic test suite

---

## Development Workflow

### Adding a New Feature

1. **Plan:** Document in FUTURE_ENHANCEMENTS.md
2. **Design:** Update schemas if needed
3. **Implement:** Add to appropriate module
4. **Test:** Add test case
5. **Document:** Update README and this file
6. **Commit:** Descriptive commit message
7. **Push:** To GitHub

### Testing Locally

```bash
# Install in dev mode
pip install -e .

# Run tests
python test_basic.py

# Test with MCP client
# (Configure in Claude Desktop/Cursor)
```

### Debugging

**MCP server logs:**
- stdout/stderr captured by MCP client
- Use `print()` for debugging (visible in client logs)
- Consider adding `--verbose` flag in future

**Common issues:**
- Import errors: Check installation
- Schema validation errors: Check Pydantic models
- plotnine errors: Check geom/scale names

---

## Contributing Guidelines

### Code Style

- Follow PEP 8
- Use Black formatter (line length 100)
- Add type hints
- Write docstrings (Google style)

### Pull Request Process

1. Fork repository
2. Create feature branch
3. Implement changes with tests
4. Update documentation
5. Submit PR with description

### Issue Reporting

Include:
- plotnine-mcp version
- Python version
- MCP client (Claude/Cursor/etc.)
- Minimal reproduction case
- Expected vs actual behavior

---

## Additional Resources

### Internal Documentation

- `README.md` - User guide
- `FUTURE_ENHANCEMENTS.md` - Roadmap
- `examples/usage_examples.md` - Example prompts

### External References

- [plotnine documentation](https://plotnine.readthedocs.io/)
- [ggplot2 reference](https://ggplot2.tidyverse.org/)
- [MCP specification](https://modelcontextprotocol.io/)
- [Pydantic docs](https://docs.pydantic.dev/)

---

## Changelog

### 2025-11-06
- ✨ Added multi-layer plot support (v0.2.0)
- 📝 Created IMPLEMENTATION_REFERENCE.md
- 📝 Created FUTURE_ENHANCEMENTS.md

### 2025-11-06
- 🎉 Initial release (v0.1.0)
- ✅ Core functionality complete
- 📚 Documentation complete

---

**Maintained by:** Fervoyush
**Repository:** https://github.com/Fervoyush/plotnine-mcp
**License:** MIT
