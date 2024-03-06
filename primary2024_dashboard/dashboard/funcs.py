import pandas as pd

from primary2024_dashboard.process.earlyvote import LoadToSnowflake, DailyTurnoutCrosstabs, VoterDetails, define
from snowflake.snowpark.functions import col, udf
import re
from primary2024_dashboard.db_connect import SnowparkSession


replace_year = lambda col: re.search(r'\d{4}', col).group(0) if re.search(r'\d{4}', col) else col


# Define the Python function
@udf(session=SnowparkSession, name='format_number_with_commas', replace=True)
def format_number_with_commas(number: int) -> str:
    return '{:,}'.format(number)

def update_early_vote_data():
    snow = LoadToSnowflake()
    snow.load_current_election()


def with_thousands_separator(func):
    def wrapper(*args, **kwargs):
        df = func(*args, **kwargs)
        df = df.select(
            *[format_number_with_commas(col(c)) if c in df.columns[1:] else col(c) for c in df.columns])
        for c in df.columns[1:]:
            df = df.withColumnRenamed(c, replace_year(c))
        return df
    return wrapper


def rename_year_crosstab_columns(df):
    for c in df.columns[1:]:
        df = df.withColumnRenamed(c, replace_year(c))
    return df


@with_thousands_separator
def format_and_rename_crosstab_columns(df: pd.DataFrame):
    return rename_year_crosstab_columns(df)


def get_party_data(party: str):
    if party.lower() not in ["rep", "dem"]:
        raise ValueError("Party must be 'rep' or 'dem'")

    all_data = SnowparkSession.table(
        define.DB_FULL_UNION_TABLE
    ).filter(
        col(define.PRIMARY_VOTED_IN).isin(party)
    )

    day_of_ev_list = all_data.select(
        define.DAY_IN_EV_COL
    ).filter(
        col(define.YEAR_COL) == 2024
    ).distinct().collect()

    current_day_df = all_data.filter(col(define.DAY_IN_EV_COL).isin(day_of_ev_list))

    return all_data, current_day_df
