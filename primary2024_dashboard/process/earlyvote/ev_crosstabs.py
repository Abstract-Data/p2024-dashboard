from dataclasses import dataclass, field
from snowflake.snowpark.functions import col
from primary2024_dashboard.db_connect import SnowparkSession
import pandas as pd
from . import ev_definitions as define
from . import ev_datashape_funcs as funcs


@dataclass
class DailyTurnoutCrosstabs:
    party: str
    session: SnowparkSession
    legislative_chamber: str = None
    legislative_district: int = None
    _df: pd.DataFrame = field(init=False, default=None)
    _current: pd.DataFrame = field(init=False, default=None)

    @property
    def df(self):
        if self._df is None:
            self._df = self.create_df()
        return self._df

    @df.setter
    def df(self, value):
        self._df = value

    def create_df(self):
        if self._df is None:
            if self.legislative_chamber and self.legislative_district:
                if self.legislative_chamber.lower() == 'hd':
                    _chamber = define.HOUSE_DISTRICT_COL
                elif self.legislative_chamber.lower() == 'sd':
                    _chamber = define.SENATE_DISTRICT_COL
                else:
                    raise ValueError("Legislative Chamber must be 'hd' or 'sd'")
                _df = self.session.table(define.DB_FULL_UNION_TABLE).filter(
                    col(define.PRIMARY_VOTED_IN).isin(self.party.lower())
                ).filter(
                    col(_chamber) == self.legislative_district
                )
            else:
                _df = self.session.table(define.DB_FULL_UNION_TABLE).filter(
                    col(define.PRIMARY_VOTED_IN).isin(self.party.lower())
                )

            return _df

    @property
    def current(self):
        if self._df is None:
            self.df = self.create_df()
        self._current = self.df.select("*").filter(col(define.YEAR_COL) == 2024)
        return self._current

    def create_crosstabs(self, df=None, current=None):
        if not current:
            current = self.current.toPandas()
        if not df:
            df = self.df.toPandas()

        current = current.fillna(pd.NA)
        df = df.fillna(pd.NA)

        _day_of_early_vote = list(set(current[define.DAY_IN_EV_COL].tolist()))
        df = df[df[define.DAY_IN_EV_COL].isin(_day_of_early_vote)]
        df[define.DISTRICT_COLS] = df[define.DISTRICT_COLS].fillna(0)
        current[define.DISTRICT_COLS] = current[define.DISTRICT_COLS].fillna(0)

        crosstabs = {
            'byVoteMethod': funcs.create_crosstab(
                rows=[df[define.VOTE_METHOD_COL], df[define.YEAR_COL]],
                cols=df[define.DAY_IN_EV_COL]
            ),
            'byDay': funcs.create_crosstab(
                rows=df[define.DAY_IN_EV_COL],
                cols=df[define.YEAR_COL]
            ),
            'byDayAge': funcs.create_crosstab(
                rows=[df[define.AGE_RANGE_COL], df[define.YEAR_COL]],
                cols=df[define.DAY_IN_EV_COL]
            ),

            'byDayCounty': funcs.create_crosstab(
                rows=[df[define.COUNTY_COL], df[define.YEAR_COL]],
                cols=df[define.DAY_IN_EV_COL]
            ),

            'byDaySenate': funcs.create_crosstab(
                rows=[df[define.SD_COL].astype(int), df[define.YEAR_COL]],
                cols=df[define.DAY_IN_EV_COL],
            ),

            'byDayHouse': funcs.create_crosstab(
                rows=[df[define.HD_COL].astype(int), df[define.YEAR_COL]],
                cols=df[define.DAY_IN_EV_COL]
            ),

            'byDayCongressional': funcs.create_crosstab(
                rows=[df[define.CD_COL].astype(int), df[define.YEAR_COL]],
                cols=df[define.DAY_IN_EV_COL]
            ),

            'byDayVEP': funcs.create_crosstab(
                rows=df[define.YEAR_COL],
                cols=[df[define.DAY_IN_EV_COL], df[define.VEP_REGISTRATION_COL]]
            ),

            'byDayHouseCounty': funcs.create_crosstab(
                rows=[df[define.HD_COL].astype(int), df[define.COUNTY_COL]],
                cols=[df[define.YEAR_COL], df[define.DAY_IN_EV_COL]]
            ),

            'byDaySenateCounty': funcs.create_crosstab(
                rows=[df[define.SD_COL].astype(int), df[define.COUNTY_COL]],
                cols=[df[define.YEAR_COL], df[define.DAY_IN_EV_COL]]
            ),

            'byDayCongressionalCounty': funcs.create_crosstab(
                rows=[df[define.CD_COL].astype(int), df[define.COUNTY_COL]],
                cols=[df[define.YEAR_COL], df[define.DAY_IN_EV_COL]]
            ),

            'byAge': funcs.create_crosstab(
                rows=df[define.AGE_RANGE_COL],
                cols=df[define.YEAR_COL]
            ),

            'byDayCurrentPrimaryPreviousElections': funcs.create_percent_on_groupby(
                funcs.create_groupby_count(
                    df=current,
                    to_group=define.DAY_IN_EV_COL,
                    to_count=define.PARTY_TO_COUNT),
                compare=define.PARTY_TO_COMPARE,
                against=define.VOTERID_COL
            ),

            'byDayAllPrimaryPreviousElections': funcs.create_percent_on_groupby(
                funcs.create_groupby_count(
                    df=current,
                    to_group=[define.DAY_IN_EV_COL, define.YEAR_COL],
                    to_count=define.PARTY_TO_COUNT),
                compare=define.PARTY_TO_COMPARE,
                against=define.VOTERID_COL
            ),

            'byDayHouseAllPrimaryPreviousElections': funcs.create_percent_on_groupby(
                funcs.create_groupby_count(
                    df=df,
                    to_group=[define.HD_COL, define.YEAR_COL],
                    to_count=define.PARTY_TO_COUNT),
                compare=define.PARTY_TO_COMPARE,
                against=define.VOTERID_COL
            ),

            'byDaySenateAllPrimaryPreviousElections': funcs.create_percent_on_groupby(
                funcs.create_groupby_count(
                    df=df,
                    to_group=[define.SD_COL, define.YEAR_COL],
                    to_count=define.PARTY_TO_COUNT),
                compare=define.PARTY_TO_COMPARE,
                against=define.VOTERID_COL
            ),

            'byDayCongressionalAllPrimaryPreviousElections': funcs.create_percent_on_groupby(
                funcs.create_groupby_count(
                    df=df,
                    to_group=[define.CD_COL, define.YEAR_COL],
                    to_count=define.PARTY_TO_COUNT),
                compare=define.PARTY_TO_COMPARE,
                against=define.VOTERID_COL
            ),

            'byDayCountyAllPrimaryPreviousElections': funcs.create_percent_on_groupby(
                funcs.create_groupby_count(
                    df=df,
                    to_group=[define.COUNTY_COL, define.YEAR_COL],
                    to_count=define.PARTY_TO_COUNT),
                compare=define.PARTY_TO_COMPARE,
                against=define.VOTERID_COL
            ),
        }
        return crosstabs
