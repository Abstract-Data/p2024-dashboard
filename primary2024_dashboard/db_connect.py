from snowflake.snowpark import Session
from dotenv import load_dotenv
import os
from pathlib import Path
from typing import ClassVar, Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import sqlite3


""" LOCAL SQL LITE DATABASE CONNECTION """
conn = sqlite3.connect(f'{Path(__file__).parent / "p2024_results.db"}')

Base = declarative_base()

engine = create_engine(f'sqlite:///{Path(__file__).parent / "p2024_results.db"}')

SessionLocal = sessionmaker(bind=engine)


""" SNOWFLAKE SNOWPARK CONNECTION """
path = Path(__file__).parent / "process" / '.env'
load_dotenv(path)

SNOWFLAKE_SNOWPARK_PARAMS: Dict[str, str] = {
    "account": os.environ['SNOWFLAKE_VEP_ACCOUNT'],
    "user": os.environ['SNOWFLAKE_VEP_USR'],
    "password": os.environ['SNOWFLAKE_VEP_PWD'],
    "database": "VEP",
    "warehouse": os.environ['SNOWFLAKE_VEP_WAREHOUSE'],
    "role": os.environ['SNOWFLAKE_VEP_ROLE'],
    "schema": "VEP2024"
}

SnowparkSession = Session.builder.configs(SNOWFLAKE_SNOWPARK_PARAMS)
