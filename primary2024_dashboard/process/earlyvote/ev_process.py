from pathlib import Path
from primary2024_dashboard.utils.csv_reader import read_files_in_directory
from primary2024_dashboard.process.earlyvote.earlyvoter_validation import VoterDetails
from primary2024_dashboard.process.earlyvote.earlyvoter_model import VoterDetailModel
from primary2024_dashboard.db_connect import (
    SnowparkSession,
    Base,
    SessionLocal,
    engine,
    conn
)
from snowflake.snowpark.functions import col
from typing import Generator, List
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
import pandas as pd
from primary2024_dashboard.logger import Logger
from dataclasses import dataclass
import matplotlib.pyplot as plt

make_null_list = [
    'general_count',
    'primary_count',
    'primary_count_dem',
    'primary_count_rep',
    'primary_percent_dem',
    'general_percent_dem',
    'primary_percent_rep',
    'general_percent_rep',
    'age'
]

column_list = ['county', 'sd', 'hd', 'cd', 'vote_method', 'age_range',
               'vep_registration', 'day_in_ev', 'primary_count_dem', 'primary_count_rep', 'year']


class ElectionYearData:
    def __init__(self, year: str, path: Path = Path(__file__).parents[2] / "data" / "earlyvote_days"):
        self.year = year

        if year == "2024":
            self.path = path / year / "march_primary"
        else:
            self.path = path / year
        self.data = read_files_in_directory(self.path)

    def __iter__(self):
        return self.data

    def __next__(self):
        return next(self.data)

    def __len__(self):
        return len(list(self.data))

    def to_df(self) -> pd.DataFrame:
        df = pd.DataFrame([dict(x) for x in self.data])
        df = df.fillna(pd.NA)
        return df


class EarlyVoteData:
    snowpark = SnowparkSession.create()
    eh2020 = ElectionYearData("2020")
    eh2022 = ElectionYearData("2022")
    eh2024 = ElectionYearData("2024")
    logger = Logger(module_name="EarlyVoteData")

    # def __init__(
    #         self,
    #         eh2020=ElectionYearData("2020"),
    #         eh2022=ElectionYearData("2022"),
    #         eh2024=ElectionYearData("2024")
    # ):
    #     self.eh2020 = eh2020
    #     self.eh2022 = eh2022
    #     self.eh2024 = eh2024
    @classmethod
    def compile(cls, records: ElectionYearData = None) -> Generator[VoterDetails, None, None]:
        cls.logger.debug(f".compile() called")
        if records is None:
            records = cls.eh2024

        data = [dict(x) for x in records.data]
        if records == cls.eh2024:
            cls.logger.debug(f"Compiling 2024 records")
            vep_registrations = EarlyVoteData.snowpark.table(
                'ALL_VEP_VUIDS'
            ).select(
                'VUID'
            )
            cls.logger.debug(f"Pulling VEP Registrations")

            vep_registrations = vep_registrations.rename(
                {
                    'VUID': 'VEP_VUID'
                }
            )
            current_early_voters = EarlyVoteData.snowpark.create_dataframe(data, schema=list(
                data[0].keys()))  # Load data into Snowpark
            cls.logger.debug(f"Pulling early voters")

            previous_voting_history = EarlyVoteData.snowpark.table(
                'ELECTIONHISTORY'
            ).filter(
                col(
                    'VUID'
                ).isin(
                    current_early_voters.select(
                        'ID_VOTER'
                    )
                )
            )
            previous_voting_history = previous_voting_history.rename({'VUID': 'EH_VUID'})
            cls.logger.debug(f"Pulled voting history")

            state_voterfile = EarlyVoteData.snowpark.table(
                'VOTERFILE'
            ).select(
                'VUID',
                'DOB',
                'STATE_LEGISLATIVE_UPPER',
                'STATE_LEGISLATIVE_LOWER',
                'CONGRESSIONAL'
            ).filter(
                col(
                    'VUID'
                ).isin(
                    current_early_voters.select(
                        'ID_VOTER'
                    )
                )
            )
            cls.logger.debug(f"Pulled voterfile")

            add_dob = current_early_voters.join(state_voterfile, col('ID_VOTER') == col('VUID'), 'inner')
            cls.logger.debug(f"Joined dobs with early voters")
            add_vep_registrations = add_dob.join(vep_registrations, col('ID_VOTER') == col('VEP_VUID'), 'left')
            cls.logger.debug(f"Joined VEP registrations with early voters")
            voter_ev_history = add_vep_registrations.join(previous_voting_history, col('ID_VOTER') == col('EH_VUID'),
                                                          'left')
            cls.logger.debug(f"Joined voting history with early voters")

        else:
            cls.logger.debug(f"Compiling previous year records")
            previous_election_history = EarlyVoteData.snowpark.create_dataframe(data, schema=list(data[0].keys()))
            cls.logger.debug(f"Pulling voters")
            state_voterfile = EarlyVoteData.snowpark.table(
                'VOTERFILE'
            ).select(
                'VUID',
                'DOB',
                'STATE_LEGISLATIVE_UPPER',
                'STATE_LEGISLATIVE_LOWER',
                'CONGRESSIONAL'
            ).filter(
                col(
                    'VUID'
                ).isin(
                    previous_election_history.select(
                        'ID_VOTER'
                    )
                )
            )
            voter_ev_history = previous_election_history.join(state_voterfile, col('ID_VOTER') == col('VUID'), 'inner')
            cls.logger.debug(f"Joined voters with voterfile")

        voter_ev_history = (voter_ev_history.to_pandas().to_dict(orient='records'))
        cls.logger.debug(f"Returning records")
        return (VoterDetails(**dict(x)) for x in voter_ev_history)

    @classmethod
    def update(cls) -> None:
        cls.logger.info("Updating 2024 voter records in database")
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as session:
            for record in cls.compile():
                stmt = sqlite_insert(VoterDetailModel).values(**dict(record))
                on_conflict_stmt = stmt.on_conflict_do_update(
                    index_elements=['vuid'],
                    set_=dict(stmt.excluded)
                )
                session.execute(on_conflict_stmt)
            session.commit()
            cls.logger.info("2024 voter records updated in database")

    @staticmethod
    def fetch() -> Generator[VoterDetails, None, None]:
        EarlyVoteData.logger.info("Fetching 2024 records from database")
        with SessionLocal() as session:
            for record in session.query(VoterDetailModel).all():
                yield VoterDetails.model_construct(**record.__dict__)

    @classmethod
    def to_df(cls, records: ElectionYearData = None) -> pd.DataFrame:
        cls.logger.debug("Converting records to dataframe")
        if records is None:
            records = cls.fetch()
        else:
            records = cls.compile(records)
        df = pd.DataFrame([dict(x) for x in records])
        df = df.fillna(pd.NA)
        df[make_null_list] = df[make_null_list].replace(0, pd.NA)
        cls.logger.debug("Returning dataframe")
        return df


ev_data = EarlyVoteData()

ev_data.update()

ev2020 = ev_data.to_df(ev_data.eh2020)
ev2022 = ev_data.to_df(ev_data.eh2022)
ev2024 = ev_data.to_df()

ev2020['year'] = 2020
ev2022['year'] = 2022
ev2024['year'] = 2024


def reduce_columns(df: pd.DataFrame, columns: List = None) -> pd.DataFrame:
    if not columns:
        columns = column_list
    return df[columns]


def replace_full_history():
    return pd.concat(
        [
            reduce_columns(x) for x in [ev2020, ev2022, ev2024]
        ],
        ignore_index=True
    ).sort_values(
        by='day_in_ev'
    ).to_sql(
        'full_turnout_roster',
        con=conn,
        if_exists='replace',
        index=False
)


@dataclass
class DailyTurnoutCrosstabs:
    all_elections: pd.DataFrame = pd.read_sql("SELECT * FROM full_turnout_roster", con=conn)

    def __post_init__(self):
        df = self.all_elections
        self.potus = df[df['year'].isin(['2020', '2024'])]
        self.current = df[df['year'] == '2024']
        self.byDay = pd.crosstab(
            df['day_in_ev'],
            df['year']
        )
        self.byDayAge = pd.crosstab(
            [df['age_range'], df['year']],
            df['day_in_ev']
        )

        self.byDayCounty = pd.crosstab(
            [df['county'], df['year']],
            df['day_in_ev']
        )

        self.byDaySenate = pd.crosstab(
            [df['sd'].astype(int), df['year']],
            df['day_in_ev'],
        )

        self.byDayHouse = pd.crosstab(
            [df['hd'].astype(int), df['year']],
            df['day_in_ev']
        )

        self.byDayCongressional = pd.crosstab(
            [df['cd'].astype(int), df['year']],
            df['day_in_ev']
        )

        self.byDayVEP = pd.crosstab(
            df['year'],
            [df['day_in_ev'], df['vep_registration']]
        )

        self.byDayHouseCounty = pd.crosstab(
            [df['hd'].astype(int), df['county']],
            [df['year'], df['day_in_ev']]
        )

        self.byDaySenateCounty = pd.crosstab(
            [df['sd'].astype(int), df['county']],
            [df['year'], df['day_in_ev']]
        )

        self.byDayCongressionalCounty = pd.crosstab(
            [df['cd'].astype(int), df['county']],
            [df['year'], df['day_in_ev']]
        )
        self.byAge = pd.crosstab(
            df['age_range'],
            df['year']
        )

# TODO: Republican Primary Score Turnout, Break Out By District
# TODO: Democrat Primary Score Turnout, Break Out By District

ct = DailyTurnoutCrosstabs()