#!/usr/bin/env python3
"""
Basic test script for plotnine MCP server functionality.
"""

import sys
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from plotnine_mcp.data_loader import load_data, DataSource
from plotnine_mcp.plot_builder import build_plot, save_plot
from plotnine_mcp.schemas import (
    Aesthetics,
    GeomConfig,
    ThemeConfig,
    LabelsConfig,
    OutputConfig,
)


def test_inline_data_scatter_plot():
    """Test creating a simple scatter plot with inline data."""
    print("Test 1: Simple scatter plot with inline data...")

    # Create data source
    data_source = DataSource(
        type="inline",
        data=[
            {"x": 1, "y": 2, "category": "A"},
            {"x": 2, "y": 4, "category": "A"},
            {"x": 3, "y": 3, "category": "B"},
            {"x": 4, "y": 5, "category": "B"},
            {"x": 5, "y": 6, "category": "C"},
        ],
    )

    # Load data
    data = load_data(data_source)
    print(f"  ✓ Data loaded: {len(data)} rows")

    # Create plot configuration
    aes_config = Aesthetics(x="x", y="y", color="category")
    geom_config = GeomConfig(type="point", params={"size": 3})
    theme_config = ThemeConfig(base="minimal")
    labels_config = LabelsConfig(
        title="Test Scatter Plot", x="X Values", y="Y Values"
    )
    output_config = OutputConfig(
        format="png", filename="test_scatter.png", directory="./output"
    )

    # Build plot
    plot = build_plot(
        data=data,
        aes_config=aes_config,
        geom_config=geom_config,
        theme_config=theme_config,
        labels_config=labels_config,
    )
    print("  ✓ Plot built successfully")

    # Save plot
    result = save_plot(plot, output_config)
    print(f"  ✓ Plot saved to: {result['path']}")

    return result


def test_file_data_line_plot():
    """Test creating a line plot from CSV file."""
    print("\nTest 2: Line plot from CSV file...")

    # Create data source
    data_source = DataSource(
        type="file", path="./examples/sample_data.csv", format="csv"
    )

    # Load data
    data = load_data(data_source)
    print(f"  ✓ Data loaded: {len(data)} rows, columns: {list(data.columns)}")

    # Create plot configuration
    aes_config = Aesthetics(x="x", y="y", color="category")
    geom_config = GeomConfig(type="line", params={"size": 1.5})
    theme_config = ThemeConfig(
        base="bw",
        customizations={"figure_size": [10, 6], "legend_position": "bottom"},
    )
    labels_config = LabelsConfig(
        title="Sample Data Line Plot", x="X Axis", y="Y Axis"
    )
    output_config = OutputConfig(
        format="png", filename="test_line.png", directory="./output"
    )

    # Build plot
    plot = build_plot(
        data=data,
        aes_config=aes_config,
        geom_config=geom_config,
        theme_config=theme_config,
        labels_config=labels_config,
    )
    print("  ✓ Plot built successfully")

    # Save plot
    result = save_plot(plot, output_config)
    print(f"  ✓ Plot saved to: {result['path']}")

    return result


def test_bar_plot():
    """Test creating a bar plot."""
    print("\nTest 3: Bar plot...")

    # Create data
    data_source = DataSource(
        type="inline",
        data=[
            {"category": "A", "value": 10},
            {"category": "B", "value": 15},
            {"category": "C", "value": 12},
            {"category": "D", "value": 18},
        ],
    )

    data = load_data(data_source)
    print(f"  ✓ Data loaded: {len(data)} rows")

    # Create plot
    aes_config = Aesthetics(x="category", y="value", fill="category")
    geom_config = GeomConfig(type="col")
    theme_config = ThemeConfig(base="classic")
    labels_config = LabelsConfig(title="Bar Chart Example", x="Category", y="Value")
    output_config = OutputConfig(
        format="png", filename="test_bar.png", directory="./output"
    )

    plot = build_plot(
        data=data,
        aes_config=aes_config,
        geom_config=geom_config,
        theme_config=theme_config,
        labels_config=labels_config,
    )
    print("  ✓ Plot built successfully")

    result = save_plot(plot, output_config)
    print(f"  ✓ Plot saved to: {result['path']}")

    return result


def test_multi_layer_plot():
    """Test creating a multi-layer plot (scatter + smooth)."""
    print("\nTest 4: Multi-layer plot (scatter + smooth)...")

    # Create data source
    data_source = DataSource(
        type="file", path="./examples/sample_data.csv", format="csv"
    )

    data = load_data(data_source)
    print(f"  ✓ Data loaded: {len(data)} rows")

    # Create plot with multiple geoms
    aes_config = Aesthetics(x="x", y="y", color="category")
    geom_configs = [
        GeomConfig(type="point", params={"size": 3, "alpha": 0.7}),
        GeomConfig(type="smooth", params={"method": "lm", "se": False}),
    ]
    theme_config = ThemeConfig(
        base="minimal", customizations={"figure_size": [10, 6]}
    )
    labels_config = LabelsConfig(
        title="Multi-Layer Plot: Points + Smooth Trend",
        x="X Values",
        y="Y Values",
    )
    output_config = OutputConfig(
        format="png", filename="test_multi_layer.png", directory="./output"
    )

    plot = build_plot(
        data=data,
        aes_config=aes_config,
        geom_configs=geom_configs,
        theme_config=theme_config,
        labels_config=labels_config,
    )
    print("  ✓ Multi-layer plot built successfully")

    result = save_plot(plot, output_config)
    print(f"  ✓ Plot saved to: {result['path']}")

    return result


def test_boxplot_with_jitter():
    """Test boxplot with jittered points overlay."""
    print("\nTest 5: Boxplot with jittered points...")

    # Create data
    data_source = DataSource(
        type="file", path="./examples/sample_data.csv", format="csv"
    )

    data = load_data(data_source)
    print(f"  ✓ Data loaded: {len(data)} rows")

    # Create layered plot
    aes_config = Aesthetics(x="category", y="y", fill="category")
    geom_configs = [
        GeomConfig(type="boxplot", params={"alpha": 0.7}),
        GeomConfig(type="jitter", params={"width": 0.2, "alpha": 0.5}),
    ]
    theme_config = ThemeConfig(base="bw")
    labels_config = LabelsConfig(
        title="Boxplot with Individual Points",
        x="Category",
        y="Values",
    )
    output_config = OutputConfig(
        format="png", filename="test_boxplot_jitter.png", directory="./output"
    )

    plot = build_plot(
        data=data,
        aes_config=aes_config,
        geom_configs=geom_configs,
        theme_config=theme_config,
        labels_config=labels_config,
    )
    print("  ✓ Boxplot with jitter built successfully")

    result = save_plot(plot, output_config)
    print(f"  ✓ Plot saved to: {result['path']}")

    return result


def main():
    """Run all tests."""
    print("=" * 60)
    print("Running Plotnine MCP Basic Tests")
    print("=" * 60)

    try:
        # Test 1: Scatter plot with inline data
        test_inline_data_scatter_plot()

        # Test 2: Line plot from file
        test_file_data_line_plot()

        # Test 3: Bar plot
        test_bar_plot()

        # Test 4: Multi-layer plot
        test_multi_layer_plot()

        # Test 5: Boxplot with jitter
        test_boxplot_with_jitter()

        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        print("\nCheck the ./output directory for generated plots.")

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
