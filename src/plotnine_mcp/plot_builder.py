"""
Plot building utilities for creating plotnine visualizations.
"""

from pathlib import Path
from typing import Any, Optional
import uuid

import pandas as pd
from plotnine import (
    ggplot,
    aes,
    # Geoms
    geom_point,
    geom_line,
    geom_bar,
    geom_col,
    geom_histogram,
    geom_boxplot,
    geom_violin,
    geom_area,
    geom_density,
    geom_smooth,
    geom_jitter,
    geom_tile,
    geom_text,
    geom_errorbar,
    geom_hline,
    geom_vline,
    geom_abline,
    geom_path,
    geom_polygon,
    geom_ribbon,
    # Scales
    scale_x_continuous,
    scale_y_continuous,
    scale_x_discrete,
    scale_y_discrete,
    scale_x_log10,
    scale_y_log10,
    scale_x_sqrt,
    scale_y_sqrt,
    scale_x_datetime,
    scale_y_datetime,
    scale_color_gradient,
    scale_color_discrete,
    scale_fill_gradient,
    scale_fill_discrete,
    scale_color_brewer,
    scale_fill_brewer,
    # Themes
    theme_gray,
    theme_bw,
    theme_minimal,
    theme_classic,
    theme_dark,
    theme_light,
    theme_void,
    theme,
    element_text,
    element_rect,
    element_line,
    element_blank,
    # Facets
    facet_wrap,
    facet_grid,
    # Coords
    coord_cartesian,
    coord_flip,
    coord_fixed,
    coord_trans,
    # Stats
    stat_smooth,
    stat_bin,
    stat_density,
    stat_summary,
    # Labels
    labs,
    xlab,
    ylab,
    ggtitle,
)

from .schemas import (
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


class PlotBuildError(Exception):
    """Custom exception for plot building errors."""

    pass


# Geom mapping dictionary
GEOM_MAP = {
    "point": geom_point,
    "line": geom_line,
    "bar": geom_bar,
    "col": geom_col,
    "histogram": geom_histogram,
    "boxplot": geom_boxplot,
    "violin": geom_violin,
    "area": geom_area,
    "density": geom_density,
    "smooth": geom_smooth,
    "jitter": geom_jitter,
    "tile": geom_tile,
    "text": geom_text,
    "errorbar": geom_errorbar,
    "hline": geom_hline,
    "vline": geom_vline,
    "abline": geom_abline,
    "path": geom_path,
    "polygon": geom_polygon,
    "ribbon": geom_ribbon,
}


def build_plot(
    data: pd.DataFrame,
    aes_config: Aesthetics,
    geom_config: Optional[GeomConfig] = None,
    geom_configs: Optional[list[GeomConfig]] = None,
    scales: Optional[list[ScaleConfig]] = None,
    theme_config: Optional[ThemeConfig] = None,
    facet_config: Optional[FacetConfig] = None,
    labels_config: Optional[LabelsConfig] = None,
    coord_config: Optional[CoordConfig] = None,
    stats: Optional[list[StatConfig]] = None,
) -> ggplot:
    """
    Build a plotnine plot from configuration.

    Args:
        data: DataFrame to plot
        aes_config: Aesthetic mappings
        geom_config: Single geometry configuration (deprecated, use geom_configs)
        geom_configs: List of geometry configurations for multi-layer plots
        scales: Scale configurations
        theme_config: Theme configuration
        facet_config: Facet configuration
        labels_config: Labels configuration
        coord_config: Coordinate system configuration
        stats: Statistical transformation configurations

    Returns:
        ggplot object

    Raises:
        PlotBuildError: If plot cannot be built
    """
    try:
        # Handle backward compatibility: convert single geom to list
        if geom_config and not geom_configs:
            geom_configs = [geom_config]
        elif not geom_configs:
            raise PlotBuildError("Either geom_config or geom_configs must be provided")

        # Build aesthetics
        aes_obj = _build_aesthetics(aes_config)

        # Start with base plot
        plot = ggplot(data, aes_obj)

        # Add geometries (multiple layers)
        for geom_cfg in geom_configs:
            plot = plot + _build_geom(geom_cfg)

        # Add statistical transformations if any
        if stats:
            for stat_config in stats:
                plot = plot + _build_stat(stat_config)

        # Add scales
        if scales:
            for scale_config in scales:
                plot = plot + _build_scale(scale_config)

        # Add facets
        if facet_config:
            plot = plot + _build_facet(facet_config)

        # Add labels
        if labels_config:
            plot = plot + _build_labels(labels_config)

        # Add coordinate system
        if coord_config:
            plot = plot + _build_coord(coord_config)

        # Apply theme
        if theme_config:
            plot = plot + _build_theme(theme_config)

        return plot

    except Exception as e:
        raise PlotBuildError(f"Failed to build plot: {str(e)}") from e


def _build_aesthetics(aes_config: Aesthetics) -> aes:
    """Build aesthetics object from configuration."""
    aes_dict = {}

    if aes_config.x:
        aes_dict["x"] = aes_config.x
    if aes_config.y:
        aes_dict["y"] = aes_config.y
    if aes_config.color:
        aes_dict["color"] = aes_config.color
    if aes_config.fill:
        aes_dict["fill"] = aes_config.fill
    if aes_config.size:
        aes_dict["size"] = aes_config.size
    if aes_config.alpha:
        aes_dict["alpha"] = aes_config.alpha
    if aes_config.shape:
        aes_dict["shape"] = aes_config.shape
    if aes_config.linetype:
        aes_dict["linetype"] = aes_config.linetype
    if aes_config.group:
        aes_dict["group"] = aes_config.group

    return aes(**aes_dict)


def _build_geom(geom_config: GeomConfig):
    """Build geometry from configuration."""
    geom_type = geom_config.type.lower()

    if geom_type not in GEOM_MAP:
        raise PlotBuildError(
            f"Unknown geom type: {geom_type}. Available: {', '.join(GEOM_MAP.keys())}"
        )

    geom_class = GEOM_MAP[geom_type]
    return geom_class(**geom_config.params)


def _build_scale(scale_config: ScaleConfig):
    """Build scale from configuration."""
    aesthetic = scale_config.aesthetic.lower()
    scale_type = scale_config.type.lower()

    # Build scale name
    scale_name = f"scale_{aesthetic}_{scale_type}"

    # Map to plotnine scale functions
    scale_map = {
        "scale_x_continuous": scale_x_continuous,
        "scale_y_continuous": scale_y_continuous,
        "scale_x_discrete": scale_x_discrete,
        "scale_y_discrete": scale_y_discrete,
        "scale_x_log10": scale_x_log10,
        "scale_y_log10": scale_y_log10,
        "scale_x_sqrt": scale_x_sqrt,
        "scale_y_sqrt": scale_y_sqrt,
        "scale_x_datetime": scale_x_datetime,
        "scale_y_datetime": scale_y_datetime,
        "scale_color_gradient": scale_color_gradient,
        "scale_color_discrete": scale_color_discrete,
        "scale_fill_gradient": scale_fill_gradient,
        "scale_fill_discrete": scale_fill_discrete,
        "scale_color_brewer": scale_color_brewer,
        "scale_fill_brewer": scale_fill_brewer,
    }

    if scale_name not in scale_map:
        raise PlotBuildError(f"Unknown scale: {scale_name}")

    scale_func = scale_map[scale_name]
    return scale_func(**scale_config.params)


def _build_theme(theme_config: ThemeConfig):
    """Build theme from configuration."""
    base_theme_name = theme_config.base.lower()

    # Map theme names to functions
    theme_map = {
        "gray": theme_gray,
        "grey": theme_gray,
        "bw": theme_bw,
        "minimal": theme_minimal,
        "classic": theme_classic,
        "dark": theme_dark,
        "light": theme_light,
        "void": theme_void,
    }

    if base_theme_name not in theme_map:
        raise PlotBuildError(
            f"Unknown theme: {base_theme_name}. Available: {', '.join(theme_map.keys())}"
        )

    base_theme = theme_map[base_theme_name]()

    # Apply customizations if any
    if theme_config.customizations:
        custom_theme = _build_theme_customizations(theme_config.customizations)
        return base_theme + custom_theme

    return base_theme


def _build_theme_customizations(customizations: dict[str, Any]):
    """Build theme customizations."""
    theme_params = {}

    # Handle common customizations
    if "figure_size" in customizations:
        theme_params["figure_size"] = tuple(customizations["figure_size"])

    if "legend_position" in customizations:
        theme_params["legend_position"] = customizations["legend_position"]

    if "legend_direction" in customizations:
        theme_params["legend_direction"] = customizations["legend_direction"]

    if "panel_background" in customizations:
        theme_params["panel_background"] = element_rect(**customizations["panel_background"])

    if "plot_background" in customizations:
        theme_params["plot_background"] = element_rect(**customizations["plot_background"])

    if "text" in customizations:
        theme_params["text"] = element_text(**customizations["text"])

    if "axis_text" in customizations:
        theme_params["axis_text"] = element_text(**customizations["axis_text"])

    if "axis_title" in customizations:
        theme_params["axis_title"] = element_text(**customizations["axis_title"])

    return theme(**theme_params)


def _build_facet(facet_config: FacetConfig):
    """Build facet from configuration."""
    if facet_config.type == "wrap":
        if not facet_config.facets:
            raise PlotBuildError("facet_wrap requires 'facets' parameter")
        return facet_wrap(facet_config.facets, **facet_config.params)
    elif facet_config.type == "grid":
        # Build formula for facet_grid
        if facet_config.rows and facet_config.cols:
            formula = f"{facet_config.rows} ~ {facet_config.cols}"
        elif facet_config.rows:
            formula = f"{facet_config.rows} ~ ."
        elif facet_config.cols:
            formula = f". ~ {facet_config.cols}"
        else:
            raise PlotBuildError("facet_grid requires 'rows' or 'cols' parameter")

        return facet_grid(formula, **facet_config.params)
    else:
        raise PlotBuildError(f"Unknown facet type: {facet_config.type}")


def _build_labels(labels_config: LabelsConfig):
    """Build labels from configuration."""
    label_params = {}

    if labels_config.title:
        label_params["title"] = labels_config.title
    if labels_config.x:
        label_params["x"] = labels_config.x
    if labels_config.y:
        label_params["y"] = labels_config.y
    if labels_config.caption:
        label_params["caption"] = labels_config.caption
    if labels_config.subtitle:
        label_params["subtitle"] = labels_config.subtitle

    return labs(**label_params)


def _build_coord(coord_config: CoordConfig):
    """Build coordinate system from configuration."""
    coord_type = coord_config.type.lower()

    coord_map = {
        "cartesian": coord_cartesian,
        "flip": coord_flip,
        "fixed": coord_fixed,
        "trans": coord_trans,
    }

    if coord_type not in coord_map:
        raise PlotBuildError(
            f"Unknown coord type: {coord_type}. Available: {', '.join(coord_map.keys())}"
        )

    coord_func = coord_map[coord_type]
    return coord_func(**coord_config.params)


def _build_stat(stat_config: StatConfig):
    """Build statistical transformation from configuration."""
    stat_type = stat_config.type.lower()

    stat_map = {
        "smooth": stat_smooth,
        "bin": stat_bin,
        "density": stat_density,
        "summary": stat_summary,
    }

    if stat_type not in stat_map:
        raise PlotBuildError(
            f"Unknown stat type: {stat_type}. Available: {', '.join(stat_map.keys())}"
        )

    stat_func = stat_map[stat_type]
    return stat_func(**stat_config.params)


def save_plot(
    plot: ggplot, output_config: OutputConfig
) -> dict[str, str]:
    """
    Save plot to file.

    Args:
        plot: ggplot object
        output_config: Output configuration

    Returns:
        Dict with 'path' key containing the saved file path

    Raises:
        PlotBuildError: If plot cannot be saved
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = Path(output_config.directory).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename if not provided
        if output_config.filename:
            filename = output_config.filename
        else:
            filename = f"plot_{uuid.uuid4().hex[:8]}.{output_config.format}"

        # Full output path
        output_path = output_dir / filename

        # Save plot
        plot.save(
            filename=str(output_path),
            width=output_config.width,
            height=output_config.height,
            dpi=output_config.dpi,
            verbose=False,
        )

        return {
            "path": str(output_path),
            "format": output_config.format,
            "width": output_config.width,
            "height": output_config.height,
            "dpi": output_config.dpi,
        }

    except Exception as e:
        raise PlotBuildError(f"Failed to save plot: {str(e)}") from e
