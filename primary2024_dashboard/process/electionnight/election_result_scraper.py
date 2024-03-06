from __future__ import annotations
from typing import Dict, List, ClassVar
import cfscrape
import json
import election_result_validators as validators
from pathlib import Path
from primary2024_dashboard.logger import Logger
from primary2024_dashboard.utils import TomlReader
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import time
from primary2024_dashboard.logger import Logger

EXAMPLES = (47009, 242), (47010, 278), (49681, 665), (49666, 661)


def generate_office_election_result(office_id: int, office_name: str, data: dict, refresh_time: datetime):
    # First, standardize the county results and race summaries
    county_results = standardize_county_results(data, refresh_time)
    race_summaries = standardize_race_summaries(data, refresh_time)

    # Filter the county results and race summaries for the specified office
    office_county_results = [result for result in county_results.values() if any(race.office_id == office_id for race in result.county_races.values())]
    office_race_summaries = [summary for summary in race_summaries.values() if summary.office_id == office_id]

    # Extract the list of candidates from the race summaries
    candidates = [candidate for summary in office_county_results for candidate in summary.statewide_summary]

    # Create the OfficeElectionResult instance
    office_election_result = validators.OfficeElectionResult(
        office_id=office_id,
        office_name=office_name,
        candidates=candidates,
        counties=office_county_results,
        update_time=refresh_time
    )

    # Add the turnout reports to the OfficeElectionResult instance
    office_election_result.turnout_reports = [county.county_turnout_report for county in office_county_results]

    return office_election_result

def standardize_county_results(data: dict, refresh_time):
    logger = Logger("func:standardize_county_results")

    logger.info(f"Standardizing county results")
    county_data = {}
    for county_num, county_details in data.items():
        county_races = {}
        for _id, _office in county_details['Races'].items():
            candidate_dict = {}
            endorsement_dict = {}
            for _race_id, _candidate_values in _office['C'].items():
                _candidate_info = validators.CountyCandidateDetails(
                    **dict(_candidate_values),
                    candidate_office_id=_race_id,
                    race_id=_race_id,
                    race_county_name=county_details["N"],
                    update_time=refresh_time
                )
                if _candidate_info.endorsements:
                    _candidate_info.endorsements.candidate_office_id = _candidate_info.candidate_office_id
                    # _candidate_info.endorsements.vote_percent = _candidate_info.candidate_vote_percent
                    endorsement_dict.update({_candidate_info.candidate_id: _candidate_info.endorsements})
                    _candidate_info.endorsement_id = _race_id
                candidate_dict.update({_candidate_info.candidate_name: _candidate_info})
            race_info = validators.CountyRaceDetails(
                **_office,
                candidates=candidate_dict,
                county_id=county_num,
                county_name=county_details['N'],
                update_time=refresh_time,
            )
            county_races.update({race_info.office_name: race_info})

        turnout_report = validators.CountyTurnoutReport(
            **county_details['Summary'],
            county_id=county_num,
            county_name=county_details['N'],
            update_time=refresh_time
        )

        county_data.update(
            {
                county_details['N']: validators.CountyElectionDetails(
                    **county_details,
                    county_id=county_num,
                    county_name=county_details['N'],
                    county_races=county_races,
                    turnout_report_id=county_num,
                    county_turnout_report=turnout_report,
                    update_time=refresh_time
                ),
            },
        )
    logger.info(f"Finished standardizing county results")
    return county_data


def standardize_race_summaries(data: dict, refresh_time):
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
                    update_time=refresh_time,
                    candidate_office_id=race['OID']
                )
                candidate_list.update({_candidate_details.candidate_name: _candidate_details})
            _race_summary = validators.StatewideRaceSummary(
                **race,
                statewide_summary=sorted(
                    [
                        v for v in candidate_list.values()], key=lambda x: x.candidate_ballot_order
                ),
                update_time=refresh_time,
                race_details_id=race['OID'],
                county_candidates_id=race['OID'],
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
            return standardize_race_summaries(_data, args[0].refresh_time)
        else:
            return standardize_county_results(_data, args[0].refresh_time)
    return wrapper


@dataclass
class ElectionResultTicker:
    result_id: ClassVar[int] = 49666
    logger: ClassVar[Logger] = Logger(module_name="class:ElectionResultTicker")
    _refresh_count: int
    _statewide_results: Dict[str, int] = field(default=None)
    _county_results: Dict[str, int] = field(default=None)
    _refresh_time: datetime = field(default=None)
    _next_refresh_time: datetime = field(default=None)
    _url_file: Path = field(default_factory=Path)
    _county_url: str = field(init=False)
    _office_url: str = field(init=False)
    _update_time_url: str = field(init=False)


    @property
    def url_file(self):
        return TomlReader(self._url_file)()

    @property
    def county_url(self):
        self._county_url = self.url_file['county_url']
        return self._county_url.format(num1=self.result_id, num2=self._refresh_count)

    @property
    def office_url(self):
        self._office_url = self.url_file['office_url']
        return self._office_url.format(num1=self.result_id, num2=self._refresh_count)

    @property
    def update_time_url(self):
        self._update_time_url = self.url_file['update_time_url']
        return self._update_time_url.format(num1=self.result_id, num2=self._refresh_count)

    @update_time_url.setter
    def update_time_url(self, value):
        self._update_time_url = self._update_time_url

    @property
    def refresh_count(self) -> int:
        return self._refresh_count

    @refresh_count.setter
    def refresh_count(self, value):
        self._refresh_count = value

    @property
    def refresh_time(self):
        _time = self.get_update_time(self.result_id, self.refresh_count)
        self._refresh_time = datetime.strptime(_time['LastUpdatedTime'], "%b %d, %Y %H:%M:%S")
        return self._refresh_time

    @refresh_time.setter
    def refresh_time(self, value):
        self._refresh_time = value

    @property
    def next_refresh_time(self):
        self._next_refresh_time = self.refresh_time + timedelta(minutes=5)
        return self._next_refresh_time

    @property
    def statewide_results(self):
        return self._statewide_results

    @statewide_results.setter
    def statewide_results(self, value):
        self._statewide_results = value

    @property
    def county_results(self):
        return self._county_results

    @county_results.setter
    def county_results(self, value):
        self._county_results = value

    @format_data_wrapper
    def scrape_county_results(self):
        logger = Logger("func:scrape_county_results")
        scraper = cfscrape.create_scraper()
        logger.info("Created cloudflare scraper for county results data")
        response = scraper.get(self.county_url)
        logger.info(f"Scraped county results data successfully")
        return json.loads(response.content)

    @format_data_wrapper
    def scrape_office_summary(self):
        self.logger.info("func:scrape_office_summary")
        scraper = cfscrape.create_scraper()
        self.logger.info("Created cloudflare scraper for office summary data")
        response = scraper.get(self.office_url)
        self.logger.info(f"Scraped office summary data successfully")
        return json.loads(response.content)

    def get_update_time(self, *num: int):
        scraper = cfscrape.create_scraper()
        self.logger.info("Created cloudflare scraper for SOS update time data")
        response = scraper.get(self.update_time_url)
        self.logger.info(f"Scraped SOS update time data successfully")
        return json.loads(response.content)

    def get_county_results(self):
        self.logger.info("func:get_county_results")
        try:
            self.county_results = self.scrape_county_results()
        except json.decoder.JSONDecodeError:
            self.county_results = self.scrape_county_results()
        return self.county_results

    def get_statewide_results(self):
        self.logger.info("func:get_statewide_results")
        try:
            self.statewide_results = self.scrape_office_summary()
        except json.decoder.JSONDecodeError:
            self.statewide_results = self.scrape_office_summary()
        return self.statewide_results

    def update_results(self):
        self.logger.info("func:update_results")
        try:
            self.county_results = self.get_county_results()
            self.statewide_results = self.get_statewide_results()
        except json.decoder.JSONDecodeError:
            self.refresh_count -= 1
            self.county_results = self.get_county_results()
            self.statewide_results = self.get_statewide_results()
        self.refresh_count += 1
        return self.statewide_results, self.county_results

    def auto_refresh(self):
        self.logger.warning("func:auto_refresh ENABLED")
        while True:
            current_time = datetime.now()
            if current_time >= self.next_refresh_time:
                self.update_results()
                self.logger.info(f"Results updated at {current_time.strftime('%H:%M:%S')}")
            if current_time.hour >= 3:
                self.logger.warning("Current time is after 3 am. Stopping auto refresh.")
                break
            time.sleep(60)  # wait for 60 seconds before checking again

    # TODO: Fix this to work with the new data structure
    """
    def generate_office_election_results(self):
        # First, standardize the county results and race summaries
        county_results = standardize_county_results(self._county_results, self._refresh_time)
        race_summaries = standardize_race_summaries(self._statewide_results, self._refresh_time)

        office_election_results = []
        for office in county_results.values():
            # Filter the county results and race summaries for the specified office
            office_county_results = [
                result for result in county_results.values() if
                any(race.office_id == office.office_id for race in result.county_races.values())]
            office_race_summaries = [
                summary for summary in race_summaries.values() if summary.office_id == office.office_id]

            # Extract the list of candidates from the race summaries
            candidates = [candidate for summary in office_county_results for candidate in summary.statewide_summary]

            # Create the OfficeElectionResult instance
            office_election_result = validators.OfficeElectionResult(
                office_id=office.office_id,
                office_name=office.office_name,
                candidates=candidates,
                counties=office_county_results,
                update_time=self._refresh_time
            )

            # Add the turnout reports to the OfficeElectionResult instance
            office_election_result.turnout_reports = [county.county_turnout_report for county in office_county_results]

            office_election_results.append(office_election_result)

        return office_election_results
    """