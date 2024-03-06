from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from typing import Union, List
from dotenv import load_dotenv
from pathlib import Path
import os
from contextlib import asynccontextmanager

from snowflake.snowpark.functions import col, lit
from api_db import SnowparkSession
from models.full_result_model import APIVoterDetails


CURRENT_YEAR = 2024

datasets = {}


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Load the larger tables
    datasets["HISTORICAL_DATA"] = SnowparkSession.table('p2024_union_grouped').cache_result()
    datasets["DAY_IN_EV"] = sorted(
        [
            row.asDict()['DAY_IN_EV'] for row in datasets['HISTORICAL_DATA']
            .filter(
                col(
                    "YEAR"
                ) == CURRENT_YEAR)
            .select(
                col(
                    "DAY_IN_EV"
                )
            )
            .distinct()
            .collect()
        ]
    )
    datasets["CURRENT_DATA_THROUGH_EV"] = datasets["HISTORICAL_DATA"].filter(
        (col("YEAR") == CURRENT_YEAR) & (col("DAY_IN_EV").isin(datasets["DAY_IN_EV"])))
    yield
    datasets.clear()



api_keys = [
    os.environ['FASTAPI_DASHBOARD_KEY'],
]

app = FastAPI(
    title="2024 Texas Primary Data API",
    description="API for the Primary 2024 Dashboard",
    version="0.1",
    docs_url="/docs",
    lifespan=app_lifespan,
)

api_key_header = APIKeyHeader(name="X-API-Key")


def get_api_key(api_key: str = Security(api_key_header)) -> Union[Security, HTTPException]:
    if api_key in api_keys:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


@app.get("/verify_key",
         response_class=JSONResponse,
         description="Verify your API Key",
         tags=["Security"])
async def verify_key(api_key: str = Security(get_api_key)):
    if not isinstance(api_key, HTTPException):
        return {"status": "API Key is valid"}
    return {"status": api_key}


@app.get("/",
         response_class=JSONResponse,
         description="Root API Endpoint",
         tags=["Home"])
async def home(api_key: str = Security(get_api_key)):
    if isinstance(api_key, HTTPException):
        raise api_key
    return {"Hello": "World"}


""" DASHBOARD DATA API ENDPOINTS AND SNOWFLAKE SNOWPARK QUERIES"""


@app.get("/historical/earlyvote",
         response_model=List[APIVoterDetails],
         description="Get all historical early vote data",
         tags=["Historical Data"])
async def get_all_earlyvote_data(api_key: str = Security(get_api_key)):
    if isinstance(api_key, HTTPException):
        raise api_key
    return [APIVoterDetails(**x.asDict()) for x in datasets['HISTORICAL_DATA'].collect()]


@app.get("/2024/primary/earlyvote",
         response_model=List[APIVoterDetails],
         description="Get early vote data through the current day in early voting",
         tags=["Early Vote Data", "2024 Texas Primary Early Vote Data"])
async def get_current_earlyvote_data(api_key: str = Security(get_api_key)):
    if isinstance(api_key, HTTPException):
        raise api_key
    return [APIVoterDetails(**x.asDict()) for x in datasets['CURRENT_DATA_THROUGH_EV'].collect()]


@app.get("/districts/counties",
         response_model=List[str],
         description="Get a list of all counties",
         tags=["District Lists"])
async def get_county_list(api_key: str = Security(get_api_key)):
    if isinstance(api_key, HTTPException):
        raise api_key
    result = datasets['HISTORICAL_DATA'].select(col("COUNTY")).distinct().collect()
    return sorted([x.asDict()["COUNTY"] for x in result])


@app.get("/2024/primary/earlyvote/districts/county/{county_name}",
         response_model=List[APIVoterDetails],
         description="Get early vote data for a specific county",
         tags=["Early Vote Data", "2024 Texas Primary Early Vote Data"])
async def get_early_vote_data_by_county(county_name: str, api_key: str = Security(get_api_key)):
    if isinstance(api_key, HTTPException):
        raise api_key
    result = datasets['CURRENT_DATA_THROUGH_EV'].filter(col("COUNTY") == lit(county_name.upper())).collect()
    return [APIVoterDetails(**x.asDict()) for x in result]


@app.get("/districts/federal",
         response_model=List[int],
         description="Get a list of all congressional districts",
         tags=["District Lists"])
async def get_congressional_districts(api_key: str = Security(get_api_key)):
    if isinstance(api_key, HTTPException):
        raise api_key
    result = datasets['HISTORICAL_DATA'].select(col("CD")).distinct().collect()
    result_list = [x.asDict()['cd'] for x in result]
    return sorted([int(x) for x in result_list])


@app.get("/2024/primary/earlyvote/districts/federal/{cd}",
         response_model=List[APIVoterDetails],
         description="Get early vote data for a specific congressional district",
         tags=["Early Vote Data", "2024 Texas Primary Early Vote Data"])
async def get_current_early_vote_by_congressional_district(cd: int, api_key: str = Security(get_api_key)):
    if isinstance(api_key, HTTPException):
        raise api_key
    result = datasets['CURRENT_DATA_THROUGH_EV'].filter(col("CD") == lit(cd)).collect()
    return [APIVoterDetails(**x.asDict()) for x in result]


@app.get("/districts/state/house",
         response_model=List[int],
         description="Get a list of all state house districts",
         tags=["District Lists"])
async def get_state_house_district_list(api_key: str = Security(get_api_key)):
    if isinstance(api_key, HTTPException):
        raise api_key
    result = datasets['HISTORICAL_DATA'].select(col("HD")).distinct().collect()
    result_list = [x.asDict()['hd'] for x in result]
    return sorted([int(x) for x in result_list])

@app.get("/2024/primary/earlyvote/districts/state/house/{hd}",
         response_model=List[APIVoterDetails],
         description="Get early vote data for a specific state house district",
         tags=["Early Vote Data", "2024 Texas Primary Early Vote Data"])
async def get_current_earlyvote_data_by_state_house_district(hd: int, api_key: str = Security(get_api_key)):
    if isinstance(api_key, HTTPException):
        raise api_key
    result = datasets['CURRENT_DATA_THROUGH_EV'].filter(col("HD") == lit(hd)).collect()
    return [APIVoterDetails(**x.asDict()) for x in result]


@app.get("/districts/state/senate",
         response_model=List[int],
         description="Get a list of all state senate districts",
         tags=["District Lists"])
async def get_state_house_district_list(api_key: str = Security(get_api_key)):
    if isinstance(api_key, HTTPException):
        raise api_key
    result = datasets['HISTORICAL_DATA'].filter(col("HD")).distinct().collect()
    result_list = [x.asDict()['sd'] for x in result]
    return sorted([int(x) for x in result_list])


@app.get("/2024/primary/earlyvote/districts/senate/{sd}",
         response_model=List[APIVoterDetails],
         description="Get early vote data for a specific state senate district",
         tags=["Early Vote Data", "2024 Texas Primary Early Vote Data"])
async def get_current_earlyvote_data_by_state_senate_district(sd: int, api_key: str = Security(get_api_key)):
    if isinstance(api_key, HTTPException):
        raise api_key
    result = datasets['CURRENT_DATA_THROUGH_EV'].filter(col("SD") == lit(sd)).collect()
    return [APIVoterDetails(**x.asDict()) for x in result]


@app.get("/2024/primary/earlyvote/party/{party}",
         response_model=List[APIVoterDetails],
         description="Get early vote data for a specific party",
         tags=["Early Vote Data", "2024 Texas Primary Early Vote Data", "Political Party Data"],
         responses={404: {"description": "Invalid party: Must be 'dem' or 'rep'"}})
async def get_current_earlyvote_data_by_state_senate_district(party: str, api_key: str = Security(get_api_key)):
    if isinstance(api_key, HTTPException):
        raise api_key

    if party.lower() in ['republican', 'gop', 'rnc', 'rep']:
        party = 'rep'
    elif party.lower() in ['democrat', 'dnc', 'dem']:
        party = 'dem'
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid party",
        )
    result = datasets['CURRENT_DATA_THROUGH_EV'].filter(col("PRIMARY_VOTED_IN") == lit(party)).collect()
    return [APIVoterDetails(**x.asDict()) for x in result]



