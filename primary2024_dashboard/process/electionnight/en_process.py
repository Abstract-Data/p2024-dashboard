from __future__ import annotations
from primary2024_dashboard.process.electionnight.election_result_db import Base, SessionLocal, engine
from election_result_scraper import ElectionResultTicker
import election_result_models as models
from election_result_validators import ENDORSEMENTS
from pathlib import Path
import csv
import itertools
from sqlalchemy.orm.exc import StaleDataError
from primary2024_dashboard.logger import Logger
from time import sleep

logger = Logger(module_name="en_process.py")

P2024_ELECTION_RESULTS = ElectionResultTicker(
    _refresh_count=661,
    _url_file=Path(__file__).parents[2] / 'texas_results_urls.toml'
)


def generate_county_turnout_report_models(county_results):
    logger.info("Generating county turnout report models")
    for county in county_results.values():
        county_turnout_report = models.CountyTurnoutReportModel(
            **dict(county.county_turnout_report)
        )
        yield county_turnout_report


def generate_county_election_detail_models(county_results):
    logger.info("Generating county election detail models")
    for county in county_results.values():
        county_turnout_report = models.CountyTurnoutReportModel(
            **dict(county.county_turnout_report)
        )
        yield models.CountyElectionDetailsModel(
            county_id=county.county_id,
            county_name=county.county_name,
            county_total_votes=county.county_total_votes,
            county_palette_color=county.county_palette_color,
            turnout_report_id=county.turnout_report_id,
            update_time=county.update_time,
            county_turnout_report=county_turnout_report
        )


def generate_county_race_models(county_results):
    logger.info("Generating county race models")
    for county in county_results.values():
        for race in county.county_races.values():
            yield models.CountyRaceDetailsModel(
                office_id=race.office_id,
                office_name=race.office_name,
                office_type=race.office_type,
                office_district_number=race.office_district_number,
                office_total_votes=race.office_total_votes,
                county_id=county.county_id,
                county_name=county.county_name,
                update_time=race.update_time,
            )


def generate_county_candidate_models(county_results):
    logger.info("Generating county candidate models")
    for county in county_results.values():
        for race in county.county_races.values():
            for candidate in race.candidates.values():
                county_detail_model = models.CountyCandidateDetailsModel(
                    candidate_id=candidate.candidate_id,
                    candidate_name=candidate.candidate_name,
                    candidate_first_name=candidate.candidate_first_name,
                    candidate_last_name=candidate.candidate_last_name,
                    candidate_party=candidate.candidate_party,
                    candidate_incumbent=candidate.candidate_incumbent,
                    candidate_early_votes=candidate.candidate_early_votes,
                    candidate_election_day_votes=candidate.candidate_election_day_votes,
                    candidate_total_votes=candidate.candidate_total_votes,
                    candidate_vote_percent=candidate.candidate_vote_percent,
                    candidate_palette_color=candidate.candidate_palette_color,
                    update_time=candidate.update_time,
                    candidate_office_id=candidate.candidate_office_id,
                    race_county_name=county.county_name,
                    race_id=candidate.candidate_office_id
                )
                yield county_detail_model


def generate_county_level_endorsement_models(county_results):
    logger.info("Generating county level endorsement models")
    for county in county_results.values():
        for race in county.county_races.values():
            for candidate in race.candidates.values():
                if candidate.endorsements:
                    if candidate.endorsements.candidate_id is not None:
                        endorsement_model = models.CandidateEndorsementsModel(
                            **dict(candidate.endorsements),
                        )
                        yield endorsement_model


def generate_statewide_race_summaries(office_summary):
    logger.info("Generating statewide race summaries")
    for summary in office_summary.values():
        yield models.StatewideRaceSummaryModel(
            office_id=summary.office_id,
            office_name=summary.office_name,
            office_type=summary.office_type,
            office_district_number=summary.office_district_number,
            race_details_id=summary.race_details_id,
            county_candidates_id=summary.county_candidates_id,
            update_time=summary.update_time
        )


def generate_statewide_candidate_summaries(office_summary):
    logger.info("Generating statewide candidate summaries")
    for summary in office_summary.values():
        for _candidate in summary.statewide_summary:
            yield models.StatewideCandidateSummaryModel(
                candidate_name=_candidate.candidate_name,
                candidate_party=_candidate.candidate_party,
                candidate_palette_color=_candidate.candidate_palette_color,
                candidate_total_votes=_candidate.candidate_total_votes,
                candidate_ballot_order=_candidate.candidate_ballot_order,
                candidate_office_id=_candidate.candidate_office_id,
                race_summary_id=int(summary.office_id),
                update_time=_candidate.update_time
            )


def main():
    P2024_ELECTION_RESULTS.get_update_time()
    P2024_ELECTION_RESULTS.update_results()

    county_results = P2024_ELECTION_RESULTS.county_results
    office_summary = P2024_ELECTION_RESULTS.statewide_results

    all_models = itertools.chain(
        generate_county_turnout_report_models(county_results),
        generate_county_election_detail_models(county_results),
        generate_county_race_models(county_results),
        generate_county_candidate_models(county_results),
        generate_statewide_race_summaries(office_summary),
        generate_statewide_candidate_summaries(office_summary)
    )

    with SessionLocal() as session:
        Base.metadata.create_all(bind=engine)
        session.add_all(all_models)
        session.commit()

        endorsement_models = [x for x in generate_county_level_endorsement_models(county_results)]

        try:
            endorsements_to_update = [x.__dict__ for x in endorsement_models]
            session.bulk_update_mappings(models.CandidateEndorsementsModel, endorsements_to_update)
        except StaleDataError:
            session.rollback()
            session.add_all(endorsement_models)
        session.commit()

    return office_summary, county_results


for _ in range(30):
    statewide_races, county_races = main()
    sleep(30)
