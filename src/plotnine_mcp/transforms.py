"""
Data transformation utilities for pre-plot data manipulation.
"""

import pandas as pd
from typing import Any, Optional, Union


def apply_filter(data: pd.DataFrame, filter_expr: str) -> pd.DataFrame:
    """
    Filter data using a query expression.

    Args:
        data: Input DataFrame
        filter_expr: Pandas query expression (e.g., "age > 18 and city == 'NYC'")

    Returns:
        Filtered DataFrame

    Examples:
        >>> apply_filter(data, "age > 18")
        >>> apply_filter(data, "category == 'A' and value > 100")
    """
    try:
        return data.query(filter_expr)
    except Exception as e:
        raise ValueError(f"Filter error: {str(e)}\n\nCheck your filter expression syntax.")


def apply_group_summarize(
    data: pd.DataFrame,
    group_by: Union[str, list[str]],
    aggregations: dict[str, Union[str, list[str]]],
) -> pd.DataFrame:
    """
    Group data and apply aggregations.

    Args:
        data: Input DataFrame
        group_by: Column(s) to group by
        aggregations: Dictionary mapping column names to aggregation function(s)
                     Functions: 'sum', 'mean', 'median', 'min', 'max', 'count', 'std', 'var'

    Returns:
        Grouped and aggregated DataFrame

    Examples:
        >>> apply_group_summarize(data, 'category', {'value': 'mean'})
        >>> apply_group_summarize(data, ['category', 'region'], {'sales': ['sum', 'mean'], 'count': 'count'})
    """
    try:
        grouped = data.groupby(group_by)
        result = grouped.agg(aggregations).reset_index()

        # Flatten column names if multi-level
        if isinstance(result.columns, pd.MultiIndex):
            result.columns = ['_'.join(col).strip('_') if col[1] else col[0]
                            for col in result.columns.values]

        return result
    except Exception as e:
        raise ValueError(f"Grouping error: {str(e)}\n\nCheck your group_by and aggregations.")


def apply_sort(
    data: pd.DataFrame,
    sort_by: Union[str, list[str]],
    ascending: Union[bool, list[bool]] = True,
) -> pd.DataFrame:
    """
    Sort data by column(s).

    Args:
        data: Input DataFrame
        sort_by: Column(s) to sort by
        ascending: Sort order (True for ascending, False for descending)

    Returns:
        Sorted DataFrame
    """
    try:
        return data.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)
    except Exception as e:
        raise ValueError(f"Sort error: {str(e)}\n\nCheck your sort_by column names.")


def apply_select(data: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Select specific columns from data.

    Args:
        data: Input DataFrame
        columns: List of column names to keep

    Returns:
        DataFrame with selected columns
    """
    try:
        return data[columns].copy()
    except Exception as e:
        raise ValueError(
            f"Select error: {str(e)}\n\nCheck that all columns exist in data."
        )


def apply_rename(data: pd.DataFrame, rename_map: dict[str, str]) -> pd.DataFrame:
    """
    Rename columns.

    Args:
        data: Input DataFrame
        rename_map: Dictionary mapping old names to new names

    Returns:
        DataFrame with renamed columns
    """
    try:
        return data.rename(columns=rename_map)
    except Exception as e:
        raise ValueError(f"Rename error: {str(e)}")


def apply_mutate(data: pd.DataFrame, mutations: dict[str, str]) -> pd.DataFrame:
    """
    Create new columns or modify existing ones using expressions.

    Args:
        data: Input DataFrame
        mutations: Dictionary mapping new column names to expressions

    Returns:
        DataFrame with new/modified columns

    Examples:
        >>> apply_mutate(data, {'total': 'price * quantity'})
        >>> apply_mutate(data, {'age_group': 'age // 10 * 10'})
    """
    result = data.copy()
    try:
        for col_name, expr in mutations.items():
            result[col_name] = result.eval(expr)
        return result
    except Exception as e:
        raise ValueError(
            f"Mutate error: {str(e)}\n\nCheck your expression syntax for column '{col_name}'."
        )


def apply_drop_na(
    data: pd.DataFrame, columns: Optional[list[str]] = None, how: str = "any"
) -> pd.DataFrame:
    """
    Drop rows with missing values.

    Args:
        data: Input DataFrame
        columns: Specific columns to check (None for all columns)
        how: 'any' to drop if any NA, 'all' to drop only if all NA

    Returns:
        DataFrame with NA rows removed
    """
    try:
        return data.dropna(subset=columns, how=how).reset_index(drop=True)
    except Exception as e:
        raise ValueError(f"Drop NA error: {str(e)}")


def apply_fill_na(
    data: pd.DataFrame,
    fill_values: Union[Any, dict[str, Any]],
    method: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fill missing values.

    Args:
        data: Input DataFrame
        fill_values: Value(s) to fill NA with (scalar or dict mapping columns to values)
        method: Optional fill method ('ffill', 'bfill')

    Returns:
        DataFrame with NA values filled
    """
    result = data.copy()
    try:
        if method:
            return result.fillna(method=method)
        else:
            return result.fillna(fill_values)
    except Exception as e:
        raise ValueError(f"Fill NA error: {str(e)}")


def apply_sample(
    data: pd.DataFrame, n: Optional[int] = None, frac: Optional[float] = None, random_state: int = 42
) -> pd.DataFrame:
    """
    Sample rows from data.

    Args:
        data: Input DataFrame
        n: Number of rows to sample
        frac: Fraction of rows to sample (0.0 to 1.0)
        random_state: Random seed for reproducibility

    Returns:
        Sampled DataFrame
    """
    try:
        if n is not None:
            return data.sample(n=min(n, len(data)), random_state=random_state).reset_index(drop=True)
        elif frac is not None:
            return data.sample(frac=frac, random_state=random_state).reset_index(drop=True)
        else:
            raise ValueError("Must specify either 'n' or 'frac'")
    except Exception as e:
        raise ValueError(f"Sample error: {str(e)}")


def apply_unique(data: pd.DataFrame, columns: Optional[list[str]] = None) -> pd.DataFrame:
    """
    Get unique rows.

    Args:
        data: Input DataFrame
        columns: Specific columns to check for uniqueness (None for all columns)

    Returns:
        DataFrame with duplicate rows removed
    """
    try:
        return data.drop_duplicates(subset=columns).reset_index(drop=True)
    except Exception as e:
        raise ValueError(f"Unique error: {str(e)}")


def apply_rolling(
    data: pd.DataFrame,
    column: str,
    window: int,
    function: str = "mean",
    new_column: Optional[str] = None,
) -> pd.DataFrame:
    """
    Apply rolling window calculation.

    Args:
        data: Input DataFrame
        column: Column to apply rolling calculation on
        window: Window size
        function: Aggregation function ('mean', 'sum', 'min', 'max', 'std')
        new_column: Name for new column (defaults to '{column}_rolling_{function}')

    Returns:
        DataFrame with rolling calculation column added
    """
    result = data.copy()
    try:
        if new_column is None:
            new_column = f"{column}_rolling_{function}"

        rolling = result[column].rolling(window=window)

        if function == "mean":
            result[new_column] = rolling.mean()
        elif function == "sum":
            result[new_column] = rolling.sum()
        elif function == "min":
            result[new_column] = rolling.min()
        elif function == "max":
            result[new_column] = rolling.max()
        elif function == "std":
            result[new_column] = rolling.std()
        else:
            raise ValueError(f"Unknown rolling function: {function}")

        return result
    except Exception as e:
        raise ValueError(f"Rolling error: {str(e)}")


def apply_pivot(
    data: pd.DataFrame,
    index: str,
    columns: str,
    values: str,
    aggfunc: str = "mean",
) -> pd.DataFrame:
    """
    Pivot data from long to wide format.

    Args:
        data: Input DataFrame
        index: Column to use as index
        columns: Column to use for new column names
        values: Column with values to aggregate
        aggfunc: Aggregation function ('mean', 'sum', 'count', 'min', 'max')

    Returns:
        Pivoted DataFrame
    """
    try:
        result = data.pivot_table(
            index=index, columns=columns, values=values, aggfunc=aggfunc
        )
        return result.reset_index()
    except Exception as e:
        raise ValueError(f"Pivot error: {str(e)}")


def apply_transforms(data: pd.DataFrame, transforms: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Apply a series of transformations in order.

    Args:
        data: Input DataFrame
        transforms: List of transformation dictionaries, each with 'type' and parameters

    Returns:
        Transformed DataFrame

    Example:
        transforms = [
            {"type": "filter", "filter_expr": "age > 18"},
            {"type": "group_summarize", "group_by": "category", "aggregations": {"value": "mean"}},
            {"type": "sort", "sort_by": "value", "ascending": False}
        ]
    """
    result = data.copy()

    for i, transform in enumerate(transforms):
        try:
            transform_type = transform.get("type")

            if transform_type == "filter":
                result = apply_filter(result, transform["filter_expr"])

            elif transform_type == "group_summarize":
                result = apply_group_summarize(
                    result, transform["group_by"], transform["aggregations"]
                )

            elif transform_type == "sort":
                result = apply_sort(
                    result,
                    transform["sort_by"],
                    transform.get("ascending", True),
                )

            elif transform_type == "select":
                result = apply_select(result, transform["columns"])

            elif transform_type == "rename":
                result = apply_rename(result, transform["rename_map"])

            elif transform_type == "mutate":
                result = apply_mutate(result, transform["mutations"])

            elif transform_type == "drop_na":
                result = apply_drop_na(
                    result,
                    transform.get("columns"),
                    transform.get("how", "any"),
                )

            elif transform_type == "fill_na":
                result = apply_fill_na(
                    result,
                    transform["fill_values"],
                    transform.get("method"),
                )

            elif transform_type == "sample":
                result = apply_sample(
                    result,
                    transform.get("n"),
                    transform.get("frac"),
                    transform.get("random_state", 42),
                )

            elif transform_type == "unique":
                result = apply_unique(result, transform.get("columns"))

            elif transform_type == "rolling":
                result = apply_rolling(
                    result,
                    transform["column"],
                    transform["window"],
                    transform.get("function", "mean"),
                    transform.get("new_column"),
                )

            elif transform_type == "pivot":
                result = apply_pivot(
                    result,
                    transform["index"],
                    transform["columns"],
                    transform["values"],
                    transform.get("aggfunc", "mean"),
                )

            else:
                raise ValueError(f"Unknown transform type: {transform_type}")

        except Exception as e:
            raise ValueError(f"Transform {i+1} ({transform_type}) failed: {str(e)}")

    return result
