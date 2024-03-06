from snowflake.snowpark import Session
from snowflake.connector import connect
from snowflake.sqlalchemy import URL
from dotenv import load_dotenv
import os
from pathlib import Path
from typing import Dict

path = Path(__file__).parent / "process" / '.env'
load_dotenv(path)

""" SNOWFLAKE SNOWPARK CONNECTION """

SNOWFLAKE_SNOWPARK_PARAMS: Dict[str, str] = {
    "account": os.environ['SNOWFLAKE_VEP_ACCOUNT'],
    "user": os.environ['SNOWFLAKE_VEP_USR'],
    "password": os.environ['SNOWFLAKE_VEP_PWD'],
    "database": "VEP",
    "warehouse": os.environ['SNOWFLAKE_VEP_WAREHOUSE'],
    "role": os.environ['SNOWFLAKE_VEP_ROLE'],
    "schema": "ELECTIONHISTORY_TX"
}

SnowparkSession = Session.builder.configs(SNOWFLAKE_SNOWPARK_PARAMS).create()
