from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from dotenv import load_dotenv
import os
from pathlib import Path
from typing import ClassVar, Dict

load_dotenv(Path(__file__).parent / 'api.env')

# SNOWFLAKE_ORM_URL = URL(
#     account=os.environ['SNOWFLAKE_VEP_ACCOUNT'],
#     user=os.environ['SNOWFLAKE_VEP_USR'],
#     password=os.environ['SNOWFLAKE_VEP_PWD'],
#     database='VEP',
#     schema='ELECTIONHISTORY_TX',
#     warehouse=os.environ['SNOWFLAKE_VEP_WAREHOUSE'],
#     role=os.environ['SNOWFLAKE_VEP_ROLE'],
# )
#
# orm_engine = create_engine(SNOWFLAKE_ORM_URL, echo=True)
#
# orm_session = sessionmaker(autocommit=False,
#                            autoflush=False,
#                            bind=orm_engine)
#
#
# Base = declarative_base()
#
SNOWFLAKE_SNOWPARK_PARAMS: Dict[str, str] = {
    "account": os.environ['SNOWFLAKE_VEP_ACCOUNT'],
    "user": os.environ['SNOWFLAKE_VEP_USR'],
    "password": os.environ['SNOWFLAKE_VEP_PWD'],
    "database": "VEP",
    "warehouse": os.environ['SNOWFLAKE_VEP_WAREHOUSE'],
    "role": os.environ['SNOWFLAKE_VEP_ROLE'],
    "schema": "ELECTIONHISTORY_TX"
}

from snowflake.snowpark import Session


SnowparkSession = Session.builder.configs(SNOWFLAKE_SNOWPARK_PARAMS).create()
