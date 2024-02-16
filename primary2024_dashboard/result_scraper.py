import cfscrape
import json
import result_validators as validators
from pathlib import Path
from logger import Logger
from utils import read_toml_file

EXAMPLES = (47009, 242), (47010, 278), (49681, 665)

urls = read_toml_file(Path(__file__).parent / 'texas_results_urls.toml')

COUNTY_RESULTS_URL = lambda num, num2: urls['county_url'].format(num=num, num2=num2)
OFFICE_RESULTS_URL = lambda num, num2: urls['office_url'].format(num=num, num2=num2)


def standardize_county_results(data: dict):
    logger = Logger("func:standardize_county_results")

    logger.info(f"Standardizing county results")
    county_data = []
    for k, v in data.items():
        county_details = v
        county_races = []
        for _id, _office in v['Races'].items():
            candidate_list = []
            for _candidate_values in _office['C'].values():
                _candidate_info = validators.CandidateDetails(**_candidate_values)
                candidate_list.append(_candidate_info)
            race_info = validators.RaceDetails(**_office,
                                    officeCandidates=candidate_list)
            county_races.append(race_info)

        county_data.append(validators.CountyElectionDetails(**v,
                                                 countyRaces=county_races))
    logger.info(f"Finished standardizing county results")
    return county_data


def standardize_race_summaries(data: dict):
    logger = Logger("func:standardize_race_summaries")

    logger.info(f"Standardizing race summaries")
    race_summaries = []
    for item in data:
        d = data[item]
        for race in d:
            candidate_list = []
            for candidate in race['C']:
                candidate_list.append(validators.CandidateSummaryDetails(**candidate))
            race_summaries.append(
                validators.RaceSummaryDetails(
                    **race,
                    officeCandidates=sorted(candidate_list, key=lambda x: x.candidateBallotOrder)
                )
            )
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


office_summary = scrape_office_summary(EXAMPLES[0])
county_results = scrape_county_results(EXAMPLES[0])
