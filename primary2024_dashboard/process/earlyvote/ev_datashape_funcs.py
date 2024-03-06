import pandas as pd
from typing import List
from collections import namedtuple

row_col_type = str | List[pd.Series]
percentage_grouping = namedtuple('percentage_grouping', ['col_desc', 'df_col'])


def create_crosstab(rows: row_col_type, cols: row_col_type):

    return pd.crosstab(
        rows,
        cols
    )


def create_groupby_count(df, to_group: row_col_type, to_count: row_col_type):
    return df.groupby(to_group).agg({x: 'count' for x in to_count})


def create_percent_on_groupby(df: pd.DataFrame, compare: tuple[str] | List[percentage_grouping], against: str):
    if isinstance(compare, list):
        _compare = [percentage_grouping(*x) for x in compare]
        for group in _compare:
            df[group.col_desc] = df[group.df_col] / df[against]
    else:
        _compare = percentage_grouping(*compare)
        df[_compare.col_desc] = df[_compare.df_col] / df[against]
    return df
