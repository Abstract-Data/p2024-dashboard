import pandas as pd
from primary2024_dashboard.process.earlyvote import ElectionYearData, LoadToSnowflake
from typing import Generator, Dict, Annotated, Optional, List
from pathlib import Path
from datetime import date, datetime
import csv
import itertools
from pydantic import BaseModel, Field, AliasChoices, field_validator, model_validator, EmailStr, ConfigDict, ValidationInfo
from pydantic_extra_types.phone_numbers import PhoneNumber
from tqdm import tqdm
import hashlib
import phonenumbers


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

EXPORT_FOLDER = Path(__file__).parent / "data" / "exports"

p2024r = ElectionYearData("2024", party="r")
p2024d = ElectionYearData("2024", party="d")

# df = p2024.to_df()

# in_person = df[df['vote_method'] == 'IN-PERSON']
# vote_method = pd.crosstab([in_person['county'], in_person['vote_method']], in_person['vote_date'], margins=True)
#
# in_person = df[(df['vote_method'] == 'IN-PERSON') & (df['vote_date'] < date(2024, 2, 20))]
#
#
# # Get data for all vuids that are duplicates
# duplicates = df.duplicated(
#     subset=[
#         'vuid',
#         'first_name'],
#     keep=False
# )
#
# df_duplicates = df[duplicates]
#
# df_duplicate_count = df_duplicates.drop_duplicates(keep='first')
#
# crosstabs = pd.crosstab(
#     [
#         df_duplicates['county'],
#         df_duplicates['precinct'],
#         df_duplicates['poll_place_id'],
#         df_duplicates['poll_place_name'],
#         df_duplicates['vuid'],
#         df_duplicates['first_name'],
#         df_duplicates['last_name'],
#         df_duplicates['full_name'],
#         df_duplicates['vote_date'],
#     ],
#     columns=df_duplicates['vote_method'],
#     margins=True
# )
#
# by_county_duplicates = pd.crosstab(
#     [df_duplicates['county'], df_duplicates['vote_method']],
# df['vote_date'],
# margins=True)
#
# by_county_vote_totals = df.groupby('county')['vuid'].count()
#
# dupes = by_county_duplicates.reset_index()
# totals = by_county_vote_totals.reset_index()
#
# by_county_combined = pd.merge(dupes, totals, on='county')
#
# by_county_combined['percent_duplicates'] = by_county_combined['All'] / by_county_combined['vuid']
#
# crosstabs.to_csv(EXPORT_FOLDER / "20240229_gop_duplicates.csv"
# )
#
# by_county_combined.to_csv(EXPORT_FOLDER / "20240229_gop_dupes_bycounty.csv")
#
# print(crosstabs)
