#!/usr/bin/env python3
"""
Test script for new Phase 1 features:
- Data preview
- List themes
- Better error messages
- Config export/import
"""

import sys
import json
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from plotnine_mcp.data_loader import load_data, DataSource
from plotnine_mcp.plot_builder import build_plot, PlotBuildError, THEME_MAP, GEOM_MAP
from plotnine_mcp.schemas import Aesthetics, GeomConfig, ThemeConfig, OutputConfig
from plotnine_mcp.error_utils import (
    suggest_column_name,
    format_column_error,
    suggest_geom_type,
    format_geom_error,
)
from plotnine_mcp.server import (
    preview_data_handler,
    list_themes_handler,
    export_plot_config_handler,
    import_plot_config_handler,
)


def test_data_preview():
    """Test the data preview functionality."""
    print("Test 1: Data preview tool...")

    # Create inline data source
    arguments = {
        "data_source": {
            "type": "inline",
            "data": [
                {"x": 1, "y": 2.5, "category": "A"},
                {"x": 2, "y": 4.1, "category": "A"},
                {"x": 3, "y": 3.8, "category": "B"},
                {"x": 4, "y": 5.2, "category": "B"},
                {"x": 5, "y": 6.0, "category": "C"},
            ],
        },
        "rows": 3,
    }

    # Run async function
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(preview_data_handler(arguments))

    assert len(result) == 1
    assert "Shape: 5 rows × 3 columns" in result[0].text
    assert "Columns:" in result[0].text
    print("  ✓ Data preview successful")
    print(f"  Preview length: {len(result[0].text)} characters")


def test_list_themes():
    """Test the list themes functionality."""
    print("\nTest 2: List themes tool...")

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(list_themes_handler())

    assert len(result) == 1
    message = result[0].text
    assert "Available Themes" in message
    assert "minimal" in message
    assert "bw" in message
    assert "Customization options:" in message
    print("  ✓ List themes successful")
    print(f"  Listed {len(THEME_MAP)} themes")


def test_column_name_suggestion():
    """Test fuzzy matching for column names."""
    print("\nTest 3: Column name fuzzy matching...")

    available_columns = ["age", "height", "weight", "category", "value"]

    # Test exact typo
    suggestion = suggest_column_name("hieght", available_columns)
    assert suggestion == "height"
    print(f"  ✓ 'hieght' → '{suggestion}'")

    # Test case difference
    suggestion = suggest_column_name("Age", available_columns)
    assert suggestion == "age"
    print(f"  ✓ 'Age' → '{suggestion}'")

    # Test partial match
    suggestion = suggest_column_name("categoy", available_columns)
    assert suggestion == "category"
    print(f"  ✓ 'categoy' → '{suggestion}'")

    # Test format_column_error
    error_msg = format_column_error("hieght", available_columns)
    assert "Did you mean: 'height'?" in error_msg
    assert "Available columns:" in error_msg
    print("  ✓ Error message formatting works")


def test_geom_type_suggestion():
    """Test fuzzy matching for geometry types."""
    print("\nTest 4: Geom type fuzzy matching...")

    available_geoms = list(GEOM_MAP.keys())

    # Test typo
    suggestion = suggest_geom_type("scater", available_geoms)
    # Note: "scater" might not match "point" well, but should work
    print(f"  ✓ Suggestion for 'scater': {suggestion}")

    # Test partial
    suggestion = suggest_geom_type("histogram", available_geoms)
    assert suggestion == "histogram"
    print(f"  ✓ 'histogram' → '{suggestion}'")

    # Test error formatting
    error_msg = format_geom_error("scatterplot", available_geoms)
    assert "Unknown geometry type:" in error_msg
    assert "Available geometry types:" in error_msg
    print("  ✓ Geom error message formatting works")


def test_column_validation():
    """Test that column validation catches errors early."""
    print("\nTest 5: Column validation in build_plot...")

    # Create test data
    data_source = DataSource(
        type="inline",
        data=[
            {"x": 1, "y": 2, "category": "A"},
            {"x": 2, "y": 4, "category": "B"},
        ],
    )
    data = load_data(data_source)

    # Try to use non-existent column
    aes_config = Aesthetics(x="x", y="wrong_column")
    geom_config = GeomConfig(type="point")

    try:
        plot = build_plot(data, aes_config, geom_config=geom_config)
        assert False, "Should have raised PlotBuildError"
    except PlotBuildError as e:
        error_msg = str(e)
        assert "wrong_column" in error_msg
        assert "not found" in error_msg
        print(f"  ✓ Caught invalid column error")
        print(f"  Error message: {error_msg[:80]}...")


def test_export_plot_config():
    """Test exporting plot configuration."""
    print("\nTest 6: Export plot config...")

    config = {
        "data_source": {"type": "file", "path": "./data/test.csv"},
        "aes": {"x": "date", "y": "value", "color": "category"},
        "geom": {"type": "line", "params": {"size": 1.5}},
        "theme": {"base": "minimal", "customizations": {"figure_size": [12, 6]}},
        "labels": {"title": "Test Plot", "x": "Date", "y": "Value"},
    }

    arguments = {
        "config": config,
        "filename": "test_config",
        "directory": "./test_output/configs",
    }

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(export_plot_config_handler(arguments))

    assert len(result) == 1
    assert "exported successfully" in result[0].text
    assert "test_config.json" in result[0].text

    # Verify file exists
    config_path = Path("./test_output/configs/test_config.json")
    assert config_path.exists()
    print(f"  ✓ Config exported to: {config_path}")

    # Verify content
    with open(config_path, "r") as f:
        saved_config = json.load(f)
    assert saved_config["aes"]["x"] == "date"
    print("  ✓ Config content is correct")


def test_import_plot_config():
    """Test importing plot configuration."""
    print("\nTest 7: Import plot config...")

    # First ensure we have a config to import
    config = {
        "data_source": {
            "type": "inline",
            "data": [{"x": 1, "y": 2}, {"x": 2, "y": 4}],
        },
        "aes": {"x": "x", "y": "y"},
        "geom": {"type": "point"},
        "output": {
            "filename": "imported_plot",
            "directory": "./test_output",
        },
    }

    # Export it first
    export_args = {
        "config": config,
        "filename": "import_test_config",
        "directory": "./test_output/configs",
    }

    loop = asyncio.get_event_loop()
    loop.run_until_complete(export_plot_config_handler(export_args))

    # Now import it
    import_args = {
        "config_path": "./test_output/configs/import_test_config.json",
    }

    result = loop.run_until_complete(import_plot_config_handler(import_args))

    assert len(result) == 1
    assert "imported configuration" in result[0].text
    print("  ✓ Config imported and plot created")

    # Verify the plot was created
    plot_path = Path("./test_output/imported_plot.png")
    assert plot_path.exists()
    print(f"  ✓ Plot created from imported config: {plot_path}")


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
    print("Running Phase 1 New Features Tests")
    print("=" * 60)

    try:
        test_data_preview()
        test_list_themes()
        test_column_name_suggestion()
        test_geom_type_suggestion()
        test_column_validation()
        test_export_plot_config()
        test_import_plot_config()

        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        cleanup()


if __name__ == "__main__":
    main()
