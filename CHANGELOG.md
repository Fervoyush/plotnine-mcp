# Changelog

All notable changes to the plotnine MCP server will be documented in this file.

## [Unreleased] - Development Phase

All features below are in active development and will be released as v1.0.0.

### Added - Phase 1, 2 & 3 Features (2025-01-07)

#### New MCP Tools (4 tools added)
- **preview_data**: Inspect data before plotting
  - Shows dataset shape, column types, first N rows
  - Displays statistics for numeric columns
  - Reports missing values
  - Configurable number of preview rows

- **list_themes**: List all available themes
  - Shows all base themes with descriptions
  - Lists customization options
  - Includes example usage

- **export_plot_config**: Save plot configurations to JSON
  - Export any plot config for reuse
  - Configurable output directory
  - Auto-adds .json extension

- **import_plot_config**: Load and use saved configurations
  - Import previously saved configs
  - Support for parameter overrides
  - Maintains backward compatibility

#### Enhanced Error Messages
- **Fuzzy Matching**: Smart suggestions for typos
  - Column name suggestions (e.g., "hieght" → "height")
  - Geometry type suggestions (e.g., "scater" → "jitter")
  - Theme name suggestions

- **Better Validation**: Column existence check before plotting
  - Validates all aesthetic column references
  - Validates facet column references
  - Early error detection with helpful messages

- **New Module**: `error_utils.py`
  - `suggest_column_name()`: Fuzzy match column names
  - `format_column_error()`: Format helpful column errors
  - `suggest_geom_type()`: Fuzzy match geom types
  - `format_geom_error()`: Format helpful geom errors
  - `suggest_theme_name()`: Fuzzy match themes
  - `format_theme_error()`: Format helpful theme errors

#### Code Improvements
- Extracted `THEME_MAP` as module-level constant in `plot_builder.py`
- Added comprehensive column validation in `build_plot()`
- Improved error messages throughout the codebase

#### Testing
- New test suite: `test_new_features.py`
  - 7 test cases covering all new features
  - Tests for data preview, theme listing
  - Tests for fuzzy matching and error messages
  - Tests for config export/import
  - All tests passing ✓

#### Documentation
- Updated README.md with new tools documentation
- Added examples for using new tools
- Updated feature highlights
- Added usage examples in chat format

#### Phase 2: High Impact Features
- **list_plot_templates**: Browse 9 preset plot templates
  - time_series, scatter_with_trend, distribution_comparison
  - category_breakdown, correlation_heatmap, boxplot_comparison
  - multi_line, histogram_with_density, before_after

- **create_plot_from_template**: Use templates easily
  - Just provide data and aesthetics
  - Template handles geometry, theme, and scales
  - Optional overrides for customization

- **suggest_plot_templates**: AI-powered template recommendations
  - Analyzes data characteristics (numeric/categorical/time columns)
  - Optionally considers user goals
  - Returns top 5 recommendations with reasoning

- **list_color_palettes**: Browse 21 color palettes
  - 6 categories: colorblind_safe, scientific, categorical, corporate, sequential, diverging
  - Category filtering
  - Preview colors in response

- **Templates module** (`templates.py`):
  - 9 pre-configured plot templates
  - Template application with validation
  - Smart suggestion algorithm

- **Palettes module** (`palettes.py`):
  - 21 carefully curated color palettes
  - Scale configuration helpers
  - Accessibility-focused options

#### Phase 3: Advanced Features
- **batch_create_plots**: Create multiple plots in one operation
  - Process array of plot configurations
  - Detailed summary of successes/failures
  - Perfect for exploratory analysis

- **Data Transformations** (integrated into `create_plot`):
  - 12 transformation types via `transforms` parameter
  - filter: Query-based filtering
  - group_summarize: Group by and aggregate
  - sort: Sort by columns
  - select: Choose specific columns
  - rename: Rename columns
  - mutate: Create/modify columns with expressions
  - drop_na: Remove missing values
  - fill_na: Fill missing values
  - sample: Random sampling
  - unique: Remove duplicates
  - rolling: Rolling window calculations
  - pivot: Reshape data
  - Chained transformations support

- **Transforms module** (`transforms.py`):
  - All transformation logic
  - Pandas-based implementation
  - Comprehensive error handling

### Total Tools Available
Now **11 tools** (was 2, added 9):
1. create_plot (enhanced with transforms support)
2. list_geom_types
3. preview_data
4. list_themes
5. export_plot_config
6. import_plot_config
7. list_plot_templates (NEW - Phase 2)
8. create_plot_from_template (NEW - Phase 2)
9. suggest_plot_templates (NEW - Phase 2)
10. list_color_palettes (NEW - Phase 2)
11. batch_create_plots (NEW - Phase 3)

### Statistics
- Lines of code added: ~3500+
- New files: 6 (error_utils.py, templates.py, palettes.py, transforms.py, test_new_features.py, test_phase2_phase3.py)
- Tests added: 24 new test cases (7 Phase 1 + 17 Phase 2&3)
- All existing tests still passing (backward compatible)
- Total test coverage: 29 tests across 3 test suites

### Added - Multi-layer Plot Support (2025-11-06)
- **Multi-layer plot support**: Combine multiple geometries in single plot
- `geoms` parameter (array) for multi-layer plots
- Backward compatibility with `geom` parameter
- Documentation for multi-layer usage
- Test cases for multi-layer plots
- Enhanced plot_builder.py to handle multiple geoms
- Updated README with multi-layer examples

---

## [0.1.0] - Current Development Version

### Core Features
- MCP server implementation
- 20+ geometry types
- Multiple data sources (file, URL, inline)
- Full ggplot2 feature parity
- Comprehensive theming system
- Documentation and examples
- Basic test suite
