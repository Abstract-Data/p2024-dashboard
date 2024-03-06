from pathlib import Path
from primary2024_dashboard.utils.csv_reader import read_files_in_directory
from .ev_validator import VoterDetails
from .sos_intake_validator import SOSVoterIntake
from . import ev_definitions as define
from primary2024_dashboard.db_connect import SnowparkSession
from snowflake.snowpark.functions import col
from typing import Generator, List, Dict, ClassVar
import pandas as pd
from primary2024_dashboard.logger import Logger
from dataclasses import dataclass

FLDR_PATH = Path(__file__).parents[2] / "data" / "earlyvote_days"

""" DAILY TURNOUT CROSSTAB CONSTANTS """


def convert_nulls(val: pd.DataFrame) -> pd.DataFrame:
    # def wrapper(*args, **kwargs) -> DataFrame:
    #     val: DataFrame = func(*args, **kwargs)
    val: pd.DataFrame = val.astype(object).where(pd.notnull(val), None)
    return val


def reduce_columns(df: pd.DataFrame, columns: List = None) -> pd.DataFrame:
    """Reduce columns in dataframe to a specified list"""
    if not columns:
        columns = define.CONDENSED_COLS
    return df[columns]


class ElectionYearData:

    def __init__(self, year: str, party: str = None, path: Path = FLDR_PATH):
        self.year = year
        self.logger = Logger(module_name="ElectionYearData")
        if party:
            if party.lower() in ["democrat", "democratic", "dem", "d"]:
                self.party = "dem"
            elif party.lower() in ["republican", "rep", "gop", "r"]:
                self.party = "rep"
            else:
                raise ValueError("Party must be 'dem' or 'rep'")

        if self.party:
            self.path = path / year / "primary" / self.party
        else:
            self.path = path / year
        self.logger.debug(f"Started reading {self.party.title()} primary data for {self.year}")
        self.data = iter(
            SOSVoterIntake(
                **dict(x)
            ) for x in read_files_in_directory(
                self.path,
                primary_party=self.party if party else None
            )
        )
        self.logger.debug(f"Finished reading {self.party.title()} primary data for {self.year}")

    def __repr__(self):
        return f"ElectionYearData(year={self.year}, party={self.party})"

    # def __iter__(self):
    #     return self.data
    #
    # def __next__(self):
    #     return next(self.data)
    #
    # def __len__(self):
    #     return len(list(self.data))

    def to_df(self) -> pd.DataFrame:
        _data = self.data
        df = pd.DataFrame([dict(x) for x in _data])
        df = df.fillna(pd.NA)  # Change None values to pd.NA
        return df


@dataclass
class LoadToSnowflake:
    logger: ClassVar[Logger] = Logger(module_name="LoadToSnowflake")
    session: SnowparkSession = SnowparkSession

    @classmethod
    def update_with_snowflake(cls, records: Generator[SOSVoterIntake, None, None]) -> List[Dict]:
        session = cls.session
        cls.logger.info("Extracting records to load into Snowflake")

        extracted_records = [dict(x) for x in records]
        # Create dataframe from local data
        load_records = session.create_dataframe(extracted_records, schema=list(extracted_records[0].keys()))
        cls.logger.info(f"Created dataframe from local data")

        # Create voterfile dataframe
        voterfile = session.table(define.DB_VOTERFILE_TABLE).select(
            define.VOTERID_COL, 'DOB', define.REGISTRATION_DATE_COL, define.SENATE_DISTRICT_COL,
            define.HOUSE_DISTRICT_COL, 'CONGRESSIONAL')

        # Create election history dataframe
        election_history = session.table(define.DB_ELECTIONHISTORY_TABLE)

        # Rename join columns in dataframes
        voterfile = voterfile.rename({define.VOTERID_COL: 'VF_VUID'})
        election_history = election_history.rename({define.VOTERID_COL: 'EH_VUID'})
        cls.logger.debug(f"Created voterfile and election history dataframes, renamed join columns")

        # Join dataframes
        merge_records_and_voterfile = load_records.join(voterfile, col(define.VOTERID_COL) == col('VF_VUID'), 'left')
        cls.logger.debug(f"Joined records with voterfile")
        merge_election_history = merge_records_and_voterfile.join(election_history,
                                                                  col(define.VOTERID_COL) == col('EH_VUID'),
                                                                  'left')
        cls.logger.debug(f"Joined records with election history")

        # Convert to local pandas dataframe, then to dictionary records
        to_record_dicts = (merge_election_history.toPandas().to_dict(orient='records'))
        cls.logger.info(f"Converted joined records to local pandas dataframe, then to dictionary records")

        # Create a list of VoterDetails objects (Pydantic models)
        return to_record_dicts

    @classmethod
    def validate(cls, records: Generator[SOSVoterIntake, None, None]) -> Generator[VoterDetails, None, None]:
        cls.logger.info("Validating records started...")
        return (VoterDetails(**dict(x)) for x in cls.update_with_snowflake(records))

    @classmethod
    def write_to_snowflake(cls, records: Generator[VoterDetails, None, None], table_name: str, append: bool = False) -> None:
        session = cls.session
        records = [dict(x) for x in records]
        df = session.create_dataframe(records, schema=list(records[0].keys()))
        cls.logger.info(f"Created dataframe from records, overwriting Snowflake table {table_name}")
        df.write.mode("overwrite" if not append else "append").saveAsTable(f"ELECTIONHISTORY_TX.{table_name.upper()}")
        cls.logger.info(f"Records {'overwritten' if not append else 'appended'} to Snowflake table {table_name}")
        return df

    @classmethod
    def load_prior_elections(cls):
        e2020_rep = ElectionYearData(year="2020", party="r")
        e2022_rep = ElectionYearData(year="2022", party="r")
        e2022_dem = ElectionYearData(year="2022", party="d")

        _previous_years = iter([e2020_rep, e2022_rep, e2022_dem])
        for year in list(range(3)):
            _year = next(_previous_years)
            cls.logger.info(f"Loading {_year.year} {_year.party} data")
            _data = cls.validate(_year.data)
            if year == 2:
                cls.write_to_snowflake(_data, f"p{_year.year}", append=True)
            else:
                cls.write_to_snowflake(_data, f"p{_year.year}")
            cls.logger.info(f"Finished loading {_year.year} {_year.party} data")

        return None

    @classmethod
    def load_current_election(cls):
        e2024_rep = ElectionYearData(year="2024", party="r")
        e2024_dem = ElectionYearData(year="2024", party="d")
        _current_year = iter([e2024_rep, e2024_dem])
        for year in list(range(1, 3)):
            _year = next(_current_year)
            cls.logger.info(f"Loading {_year.year} {_year.party} data {year}/2")
            _data = cls.validate(_year.data)
            if year == 2:
                cls.write_to_snowflake(_data, f"p{_year.year}", append=True)
            else:
                cls.write_to_snowflake(_data, f"p{_year.year}")
            cls.logger.info(f"Finished loading {_year.year} {_year.party} data")
        return None
