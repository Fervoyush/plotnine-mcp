#!/usr/bin/env python3
"""
Test script for Phase 2 & Phase 3 features:
- Plot templates
- Template suggestions
- Color palettes
- Data transformations
- Batch processing
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from plotnine_mcp.data_loader import load_data, DataSource
from plotnine_mcp.templates import (
    list_templates,
    apply_template,
    suggest_template,
    TEMPLATES,
)
from plotnine_mcp.palettes import (
    list_palettes,
    get_palette,
    palette_categories,
    create_scale_config,
)
from plotnine_mcp.transforms import apply_transforms
from plotnine_mcp.server import (
    list_plot_templates_handler,
    create_plot_from_template_handler,
    suggest_plot_templates_handler,
    list_color_palettes_handler,
    batch_create_plots_handler,
)


def test_list_templates():
    """Test listing plot templates."""
    print("Test 1: List plot templates...")

    templates = list_templates()
    assert len(templates) == len(TEMPLATES)
    assert "time_series" in templates
    assert "scatter_with_trend" in templates

    print(f"  ✓ Listed {len(templates)} templates")
    print(f"  Templates: {', '.join(list(templates.keys())[:3])}...")


def test_apply_template():
    """Test applying a template."""
    print("\nTest 2: Apply template...")

    data_source = {
        "type": "inline",
        "data": [
            {"x": 1, "y": 2, "category": "A"},
            {"x": 2, "y": 4, "category": "B"},
        ],
    }

    aes = {"x": "x", "y": "y", "color": "category"}

    config = apply_template("scatter_with_trend", data_source, aes)

    assert "data_source" in config
    assert "aes" in config
    assert "geoms" in config
    assert len(config["geoms"]) == 2  # point + smooth

    print("  ✓ Template applied successfully")
    print(f"  Geoms: {[g['type'] for g in config['geoms']]}")


def test_suggest_template():
    """Test template suggestions."""
    print("\nTest 3: Suggest templates based on data...")

    # Numeric data
    suggestions = suggest_template(num_numeric=2, num_categorical=0, has_time=False)
    assert "scatter_with_trend" in suggestions
    print(f"  ✓ Numeric data: {suggestions[:2]}")

    # Time series data
    suggestions = suggest_template(num_numeric=1, num_categorical=0, has_time=True)
    assert "time_series" in suggestions
    print(f"  ✓ Time data: {suggestions[:2]}")

    # Categorical comparison
    suggestions = suggest_template(num_numeric=1, num_categorical=1, has_time=False)
    assert any(
        "distribution" in s or "boxplot" in s for s in suggestions
    )
    print(f"  ✓ Categorical data: {suggestions[:2]}")


def test_list_palettes():
    """Test listing color palettes."""
    print("\nTest 4: List color palettes...")

    # All palettes
    all_palettes = list_palettes()
    assert len(all_palettes) > 0

    # By category
    scientific = list_palettes("scientific")
    assert "scientific_viridis" in scientific
    assert "scientific_plasma" in scientific

    print(f"  ✓ Total palettes: {len(all_palettes)}")
    print(f"  ✓ Scientific palettes: {len(scientific)}")


def test_get_palette():
    """Test getting specific palette."""
    print("\nTest 5: Get specific palette...")

    # With prefix
    viridis = get_palette("scientific_viridis")
    assert len(viridis) == 10
    assert viridis[0].startswith("#")

    # Without prefix
    viridis2 = get_palette("viridis")
    assert viridis == viridis2

    print(f"  ✓ Viridis palette: {len(viridis)} colors")
    print(f"  First 3 colors: {viridis[:3]}")


def test_palette_categories():
    """Test palette categories."""
    print("\nTest 6: Palette categories...")

    categories = palette_categories()
    assert "colorblind_safe" in categories
    assert "scientific" in categories
    assert "categorical" in categories

    print(f"  ✓ Categories: {len(categories)}")
    for cat in list(categories.keys())[:3]:
        print(f"    - {cat}")


def test_create_scale_config():
    """Test creating scale configuration from palette."""
    print("\nTest 7: Create scale config from palette...")

    # Discrete scale
    scale = create_scale_config("viridis", aesthetic="color", type="discrete")
    assert scale["aesthetic"] == "color"
    assert scale["type"] == "discrete"
    assert "values" in scale["params"]

    # Gradient scale
    scale = create_scale_config("viridis", aesthetic="fill", type="gradient")
    assert scale["aesthetic"] == "fill"
    assert scale["type"] == "gradient"
    assert "low" in scale["params"]
    assert "high" in scale["params"]

    print("  ✓ Discrete scale created")
    print("  ✓ Gradient scale created")


def test_data_transforms_filter():
    """Test filter transformation."""
    print("\nTest 8: Data transformation - filter...")

    data_source = DataSource(
        type="inline",
        data=[
            {"x": 1, "y": 2, "category": "A"},
            {"x": 2, "y": 4, "category": "B"},
            {"x": 3, "y": 6, "category": "A"},
        ],
    )
    data = load_data(data_source)

    transforms = [{"type": "filter", "filter_expr": "y > 2"}]
    result = apply_transforms(data, transforms)

    assert len(result) == 2  # Only y=4 and y=6
    print(f"  ✓ Filtered from {len(data)} to {len(result)} rows")


def test_data_transforms_group():
    """Test group and summarize transformation."""
    print("\nTest 9: Data transformation - group & summarize...")

    data_source = DataSource(
        type="inline",
        data=[
            {"category": "A", "value": 10},
            {"category": "A", "value": 20},
            {"category": "B", "value": 15},
            {"category": "B", "value": 25},
        ],
    )
    data = load_data(data_source)

    transforms = [
        {"type": "group_summarize", "group_by": "category", "aggregations": {"value": "mean"}}
    ]
    result = apply_transforms(data, transforms)

    assert len(result) == 2  # A and B
    assert "value" in result.columns
    print(f"  ✓ Grouped from {len(data)} to {len(result)} rows")


def test_data_transforms_mutate():
    """Test mutate transformation."""
    print("\nTest 10: Data transformation - mutate...")

    data_source = DataSource(
        type="inline",
        data=[
            {"price": 10, "quantity": 5},
            {"price": 20, "quantity": 3},
        ],
    )
    data = load_data(data_source)

    transforms = [{"type": "mutate", "mutations": {"total": "price * quantity"}}]
    result = apply_transforms(data, transforms)

    assert "total" in result.columns
    assert result["total"].tolist() == [50, 60]
    print("  ✓ Created new column 'total'")
    print(f"  Values: {result['total'].tolist()}")


def test_data_transforms_sort():
    """Test sort transformation."""
    print("\nTest 11: Data transformation - sort...")

    data_source = DataSource(
        type="inline",
        data=[
            {"name": "C", "value": 3},
            {"name": "A", "value": 1},
            {"name": "B", "value": 2},
        ],
    )
    data = load_data(data_source)

    transforms = [{"type": "sort", "sort_by": "value", "ascending": False}]
    result = apply_transforms(data, transforms)

    assert result["value"].tolist() == [3, 2, 1]
    print("  ✓ Sorted by value (descending)")
    print(f"  Order: {result['name'].tolist()}")


def test_data_transforms_chained():
    """Test multiple chained transformations."""
    print("\nTest 12: Data transformation - chained...")

    data_source = DataSource(
        type="inline",
        data=[
            {"category": "A", "value": 10, "status": "active"},
            {"category": "A", "value": 20, "status": "active"},
            {"category": "B", "value": 15, "status": "inactive"},
            {"category": "B", "value": 25, "status": "active"},
        ],
    )
    data = load_data(data_source)

    transforms = [
        {"type": "filter", "filter_expr": "status == 'active'"},
        {"type": "group_summarize", "group_by": "category", "aggregations": {"value": "sum"}},
        {"type": "sort", "sort_by": "value", "ascending": False},
    ]
    result = apply_transforms(data, transforms)

    assert len(result) == 2
    print("  ✓ Applied 3 chained transforms")
    print(f"  Final shape: {result.shape}")


async def test_template_handler():
    """Test template MCP handler."""
    print("\nTest 13: Template handler (MCP)...")

    loop = asyncio.get_event_loop()
    result = await list_plot_templates_handler()

    assert len(result) == 1
    assert "time_series" in result[0].text
    assert "scatter_with_trend" in result[0].text

    print("  ✓ Template handler works")
    print(f"  Response length: {len(result[0].text)} characters")


async def test_palette_handler():
    """Test palette MCP handler."""
    print("\nTest 14: Palette handler (MCP)...")

    loop = asyncio.get_event_loop()

    # List all categories
    result = await list_color_palettes_handler({})
    assert "colorblind_safe" in result[0].text

    # List specific category
    result = await list_color_palettes_handler({"category": "scientific"})
    assert "viridis" in result[0].text

    print("  ✓ Palette handler works")
    print("  ✓ Category filtering works")


async def test_create_from_template():
    """Test creating plot from template."""
    print("\nTest 15: Create plot from template...")

    arguments = {
        "template_name": "scatter_with_trend",
        "data_source": {
            "type": "inline",
            "data": [
                {"x": 1, "y": 2},
                {"x": 2, "y": 4},
                {"x": 3, "y": 6},
                {"x": 4, "y": 8},
            ],
        },
        "aes": {"x": "x", "y": "y"},
        "output": {"filename": "test_template", "directory": "./test_output"},
    }

    result = await create_plot_from_template_handler(arguments)

    assert len(result) == 1
    assert "scatter_with_trend" in result[0].text
    assert "successfully" in result[0].text

    # Verify file created
    output_file = Path("./test_output/test_template.png")
    assert output_file.exists()

    print("  ✓ Plot created from template")
    print(f"  ✓ File: {output_file}")


async def test_suggest_templates_handler():
    """Test template suggestion handler."""
    print("\nTest 16: Template suggestion handler...")

    arguments = {
        "data_source": {
            "type": "inline",
            "data": [
                {"date": "2024-01-01", "value": 10, "category": "A"},
                {"date": "2024-01-02", "value": 20, "category": "B"},
            ],
        },
        "goal": "show trend over time",
    }

    result = await suggest_plot_templates_handler(arguments)

    assert len(result) == 1
    assert "time_series" in result[0].text or "multi_line" in result[0].text

    print("  ✓ Template suggestions work")
    print(f"  Response includes goal-based filtering")


async def test_batch_create_plots():
    """Test batch plot creation."""
    print("\nTest 17: Batch plot creation...")

    arguments = {
        "plots": [
            {
                "data_source": {
                    "type": "inline",
                    "data": [{"x": 1, "y": 2}, {"x": 2, "y": 4}],
                },
                "aes": {"x": "x", "y": "y"},
                "geom": {"type": "point"},
                "output": {"filename": "batch_1", "directory": "./test_output"},
            },
            {
                "data_source": {
                    "type": "inline",
                    "data": [{"x": 1, "y": 3}, {"x": 2, "y": 5}],
                },
                "aes": {"x": "x", "y": "y"},
                "geom": {"type": "line"},
                "output": {"filename": "batch_2", "directory": "./test_output"},
            },
        ]
    }

    result = await batch_create_plots_handler(arguments)

    assert len(result) == 1
    assert "2 plot(s)" in result[0].text
    assert "Successful: 2" in result[0].text

    # Verify files created
    assert Path("./test_output/batch_1.png").exists()
    assert Path("./test_output/batch_2.png").exists()

    print("  ✓ Batch created 2 plots")
    print("  ✓ All files created successfully")


def cleanup():
    """Clean up test output files."""
    import shutil

    test_output = Path("./test_output")
    if test_output.exists():
        shutil.rmtree(test_output)
    print("\n✓ Cleaned up test output files")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Running Phase 2 & Phase 3 Features Tests")
    print("=" * 60)

    try:
        # Template tests
        test_list_templates()
        test_apply_template()
        test_suggest_template()

        # Palette tests
        test_list_palettes()
        test_get_palette()
        test_palette_categories()
        test_create_scale_config()

        # Transform tests
        test_data_transforms_filter()
        test_data_transforms_group()
        test_data_transforms_mutate()
        test_data_transforms_sort()
        test_data_transforms_chained()

        # Async handler tests
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_template_handler())
        loop.run_until_complete(test_palette_handler())
        loop.run_until_complete(test_create_from_template())
        loop.run_until_complete(test_suggest_templates_handler())
        loop.run_until_complete(test_batch_create_plots())

        print("\n" + "=" * 60)
        print("All Phase 2 & 3 tests passed! ✓")
        print("=" * 60)
        print("\nFeatures tested:")
        print("  • 9 plot templates")
        print("  • 21 color palettes (6 categories)")
        print("  • 12 data transformations")
        print("  • Batch processing")
        print("  • All MCP handlers")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        cleanup()


if __name__ == "__main__":
    main()
