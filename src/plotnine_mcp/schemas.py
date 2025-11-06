"""
Pydantic schemas for validating plotnine MCP tool parameters.
"""

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class DataSource(BaseModel):
    """Data source configuration."""

    type: Literal["file", "url", "inline"] = Field(
        description="Type of data source: file path, URL, or inline JSON data"
    )
    path: Optional[str] = Field(
        None, description="File path or URL (required for file/url types)"
    )
    data: Optional[list[dict[str, Any]]] = Field(
        None, description="Inline data as list of dictionaries (required for inline type)"
    )
    format: Optional[Literal["csv", "json", "parquet", "excel"]] = Field(
        "csv", description="Data format (auto-detected if not specified)"
    )


class Aesthetics(BaseModel):
    """Aesthetic mappings for the plot."""

    x: Optional[str] = Field(None, description="Column name for x-axis")
    y: Optional[str] = Field(None, description="Column name for y-axis")
    color: Optional[str] = Field(None, description="Column name for color aesthetic")
    fill: Optional[str] = Field(None, description="Column name for fill aesthetic")
    size: Optional[str] = Field(None, description="Column name for size aesthetic")
    alpha: Optional[str] = Field(None, description="Column name for alpha aesthetic")
    shape: Optional[str] = Field(None, description="Column name for shape aesthetic")
    linetype: Optional[str] = Field(None, description="Column name for linetype aesthetic")
    group: Optional[str] = Field(None, description="Column name for grouping")


class GeomConfig(BaseModel):
    """Geometry configuration."""

    type: str = Field(
        description="Geometry type: point, line, bar, histogram, boxplot, violin, smooth, etc."
    )
    params: dict[str, Any] = Field(
        default_factory=dict, description="Additional parameters for the geom"
    )


class ScaleConfig(BaseModel):
    """Scale configuration."""

    aesthetic: str = Field(description="Which aesthetic this scale applies to (x, y, color, etc.)")
    type: str = Field(
        description="Scale type: continuous, discrete, log10, sqrt, date, datetime, etc."
    )
    params: dict[str, Any] = Field(
        default_factory=dict, description="Scale parameters (limits, breaks, labels, etc.)"
    )


class ThemeConfig(BaseModel):
    """Theme configuration."""

    base: str = Field(
        "gray",
        description="Base theme: gray, bw, minimal, classic, dark, light, void, etc."
    )
    customizations: dict[str, Any] = Field(
        default_factory=dict,
        description="Theme customizations (figure_size, legend_position, text sizes, etc.)"
    )


class FacetConfig(BaseModel):
    """Facet configuration."""

    type: Literal["wrap", "grid"] = Field("wrap", description="Facet type: wrap or grid")
    facets: Optional[str] = Field(None, description="Faceting formula (e.g., '~ variable' or 'var1 ~ var2')")
    cols: Optional[str] = Field(None, description="Column variable for facet_grid")
    rows: Optional[str] = Field(None, description="Row variable for facet_grid")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Additional facet parameters (ncol, scales, etc.)"
    )


class LabelsConfig(BaseModel):
    """Labels configuration."""

    title: Optional[str] = Field(None, description="Plot title")
    x: Optional[str] = Field(None, description="X-axis label")
    y: Optional[str] = Field(None, description="Y-axis label")
    caption: Optional[str] = Field(None, description="Plot caption")
    subtitle: Optional[str] = Field(None, description="Plot subtitle")


class CoordConfig(BaseModel):
    """Coordinate system configuration."""

    type: str = Field(
        "cartesian",
        description="Coordinate system: cartesian, flip, fixed, trans, etc."
    )
    params: dict[str, Any] = Field(
        default_factory=dict, description="Coordinate system parameters"
    )


class StatConfig(BaseModel):
    """Statistical transformation configuration."""

    type: str = Field(description="Stat type: smooth, bin, density, etc.")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Stat parameters"
    )


class OutputConfig(BaseModel):
    """Output configuration."""

    format: Literal["png", "pdf", "svg"] = Field("png", description="Output format")
    filename: Optional[str] = Field(None, description="Output filename (auto-generated if not provided)")
    width: float = Field(8, description="Figure width in inches")
    height: float = Field(6, description="Figure height in inches")
    dpi: int = Field(300, description="DPI for raster formats")
    directory: str = Field("./output", description="Output directory")
