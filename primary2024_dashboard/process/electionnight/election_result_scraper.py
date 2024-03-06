from __future__ import annotations
import cfscrape
import json
import election_result_validators as validators
from pathlib import Path
from primary2024_dashboard.logger import Logger
from primary2024_dashboard.utils import TomlReader
from datetime import datetime, timedelta

EXAMPLES = (47009, 242), (47010, 278), (49681, 665), (49666, 654)

urls = TomlReader(Path(__file__).parents[2] / 'texas_results_urls.toml')

COUNTY_RESULTS_URL = lambda num, num2: urls.county_url.format(num1=num, num2=num2)  # noinspection PyUnresolvedReferences
OFFICE_RESULTS_URL = lambda num, num2: urls.office_url.format(num1=num, num2=num2)  # noinspection PyUnresolvedReferences
SOS_UPDATE_TIME_URL = lambda num, num2: urls.update_time_url.format(num1=num, num2=num2)  # noinspection PyUnresolvedReferences


def get_update_time(num: tuple):
    logger = Logger("func:get_update_time")
    url = SOS_UPDATE_TIME_URL(num[0], num[1])
    scraper = cfscrape.create_scraper()
    logger.info("Created cloudflare scraper for SOS update time data")
    response = scraper.get(url)
    logger.info(f"Scraped SOS update time data successfully")
    return json.loads(response.content)


SOS_UPDATE_DETAILS = get_update_time(EXAMPLES[2])

SOS_UPDATE_TIME = datetime.strptime(SOS_UPDATE_DETAILS['LastUpdatedTime'], "%b %d, %Y %H:%M:%S")
NEXT_REFRESH_TIME = SOS_UPDATE_TIME + timedelta(minutes=5)

def standardize_county_results(data: dict):
    logger = Logger("func:standardize_county_results")

    logger.info(f"Standardizing county results")
    county_data = {}
    for county_num, county_details in data.items():
        county_races = {}
        for _id, _office in county_details['Races'].items():
            candidate_list = {}
            for _race_id, _candidate_values in _office['C'].items():
                _candidate_info = validators.CountyCandidateDetails(
                    **dict(_candidate_values),
                    race_id=_race_id,
                    race_county_id=county_num,
                    update_time=SOS_UPDATE_TIME
                )
                candidate_list.update({_candidate_info.candidate_name: _candidate_info})
            race_info = validators.CountyRaceDetails(
                **_office,
                candidates=[x for x in candidate_list.values()],
                county_id=county_num,
                county_name=county_details['N'],
                update_time=SOS_UPDATE_TIME
            )
            county_races.update({race_info.office_name: race_info})

        turnout_report = validators.CountyTurnoutReport(
            **county_details['Summary'],
            county_id=county_num,
            county_name=county_details['N'],
            update_time=SOS_UPDATE_TIME
        )

        county_data.update(
            {
                county_details['N']: validators.CountyElectionDetails(
                    **county_details,
                    county_id=county_num,
                    county_name=county_details['N'],
                    county_races=[x for x in county_races.values()],
                    turnout_report_id=county_num,
                    county_turnout_report=turnout_report,
                    update_time=SOS_UPDATE_TIME
                ),
            },
        )
    logger.info(f"Finished standardizing county results")
    return county_data


def standardize_race_summaries(data: dict):
    logger = Logger("func:standardize_race_summaries")

    logger.info(f"Standardizing race summaries")
    race_summaries = {}
    for item in data:
        d = data[item]
        for race in d:
            candidate_list = {}
            for candidate in race['C']:
                _candidate_details = validators.StatewideCandidateSummary(
                    **candidate,
                    update_time=SOS_UPDATE_TIME
                )
                candidate_list.update({_candidate_details.candidate_name: _candidate_details})
            _race_summary = validators.StatewideRaceSummary(
                    **race,
                    candidate_summary=sorted(
                        [
                            v for v in candidate_list.values()], key=lambda x: x.candidate_ballot_order
                    ),
                    update_time=SOS_UPDATE_TIME
                )
            race_summaries.update({_race_summary.office_name: _race_summary})
    logger.info(f"Finished standardizing race summaries")
    return race_summaries


def format_data_wrapper(func):
    logger = Logger("func:format_data_wrapper")

    logger.info(f"Wrapping data formatting function called {func.__name__}")

    def wrapper(*args, **kwargs):
        _data = func(*args, **kwargs)
        if 'OS' in _data.keys():
            return standardize_race_summaries(_data)
        else:
            return standardize_county_results(_data)
    return wrapper


@format_data_wrapper
def scrape_county_results(num: tuple):
    logger = Logger("func:scrape_county_results")
    url = COUNTY_RESULTS_URL(num[0], num[1])
    scraper = cfscrape.create_scraper()
    logger.info("Created cloudflare scraper for county results data")
    response = scraper.get(url)
    logger.info(f"Scraped county results data successfully")
    return json.loads(response.content)


@format_data_wrapper
def scrape_office_summary(num: tuple):
    logger = Logger("func:scrape_office_summary")
    url = OFFICE_RESULTS_URL(num[0], num[1])
    scraper = cfscrape.create_scraper()
    logger.info("Created cloudflare scraper for office summary data")
    response = scraper.get(url)
    logger.info(f"Scraped office summary data successfully")
    return json.loads(response.content)

