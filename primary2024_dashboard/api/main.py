import httpx
import pandas as pd
import json
from api_db import SnowparkSession
from snowflake.snowpark.functions import col
from models.full_result_model import APIVoterDetails
import asyncio


BASE_API_URL = 'http://127.0.0.1:8000'
P2024_API_URL = BASE_API_URL + "/2024/primary/earlyvote"
PARTY_API_URL = P2024_API_URL + "/party/{party}"

COUNTY_LIST_API_URL = BASE_API_URL + "/districts/counties"
FEDERAL_LIST_API_URL = BASE_API_URL + "/districts/federal/"
STATE_SENATE_LIST_API_URL = BASE_API_URL + "/districts/state/senate"
STATE_HOUSE_LIST_API_URL = BASE_API_URL + "/districts/state/house"

COUNTY_API_URL = P2024_API_URL + "districts/county/{county}"
FEDERAL_API_URL = P2024_API_URL + "districts/federal/{cd}"
STATE_SENATE_API_URL = P2024_API_URL + "districts/state/senate/{sd}"
STATE_HOUSE_API_URL = P2024_API_URL + "districts/state/house/{hd}"

api_key = {'X-API-Key': 'fSSjyHUiklxdOr-EHDZ7bYk2nvWnp-wflCOu8yzx210'}


async def get_party_data(party: str):
    print(f"Getting data for {party}...")
    async with httpx.AsyncClient(timeout=None) as client:
        results = await client.get(PARTY_API_URL.format(party=party), headers=api_key)
        print(f"Got data for {party}!")
    return results


async def get_district_list(district_type: str):
    print(f"{district_type.upper()} list...")
    async with httpx.AsyncClient(timeout=None) as client:
        if district_type.lower() == "county":
            results = await client.get(COUNTY_API_URL, headers=api_key)
        elif district_type.lower() in ["federal", "congress", "cd"]:
            results = await client.get(FEDERAL_LIST_API_URL, headers=api_key)
        elif district_type.lower() in ["sd", "state_senate"]:
            results = await client.get(STATE_SENATE_LIST_API_URL, headers=api_key)
        elif district_type.lower() in ["hd", "state_house"]:
            results = await client.get(STATE_HOUSE_LIST_API_URL, headers=api_key)
        else:
            raise ValueError(f"Invalid district type {district_type}")
        print("Got {} list!".format(district_type))
    return results


async def get_county_data(county_name: str):
    print(f"Getting {county_name.title()} data...")
    async with httpx.AsyncClient(timeout=None) as client:
        results = await client.get(COUNTY_API_URL.format(county=county_name), headers=api_key)
        print(f"Got {county_name.title()} data!")
    return results


async def get_district_data(district_type: str, district: int):
    print(f"Getting {district_type} {district} data...")
    async with httpx.AsyncClient(timeout=None) as client:
        if district_type.lower() in ["federal", "congress", "cd"]:
            results = await client.get(FEDERAL_API_URL.format(cd=district), headers=api_key)
        elif district_type.lower() in ["sd", "state_senate"]:
            results = await client.get(STATE_SENATE_API_URL.format(sd=district), headers=api_key)
        elif district_type.lower() in ["hd", "state_house"]:
            results = await client.get(STATE_HOUSE_API_URL.format(hd=district), headers=api_key)
        else:
            raise ValueError(f"Invalid district type {district_type}")
        print(f"Got {district_type.upper()} {district} data!")
    return results


async def main():
    rep = asyncio.create_task(get_party_data('rep'))
    dem = asyncio.create_task(get_party_data('dem'))
    county_list = asyncio.create_task(get_district_list('county'))
    congress_list = asyncio.create_task(get_district_list('federal'))
    state_senate_list = asyncio.create_task(get_district_list('state_senate'))
    state_house_list = asyncio.create_task(get_district_list('state_house'))

    county_specific = asyncio.create_task(get_county_data('Travis'))
    federal_specific = asyncio.create_task(get_district_data('federal', 25))
    state_senate_specific = asyncio.create_task(get_district_data('state_senate', 14))
    state_house_specific = asyncio.create_task(get_district_data('state_house', 48))
    results = await asyncio.gather(
        *[
            rep,
            dem,
            county_list,
            congress_list,
            state_senate_list,
            state_house_list,
            county_specific,
            federal_specific,
            state_senate_specific,
            state_house_specific
        ])
    return results


result_list = asyncio.run(main())

result1 = result_list[0]
result2 = result_list[1]
result3 = result_list[2]
result4 = result_list[3]
result5 = result_list[4]
result6 = result_list[5]
result7 = result_list[6]
result8 = result_list[7]
result9 = result_list[8]
result10 = result_list[9]

# dataframe = pd.read_json(json.dumps(results.json()))

