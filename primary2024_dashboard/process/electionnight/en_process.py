from __future__ import annotations
from primary2024_dashboard.process.electionnight.election_result_db import Base, SessionLocal, engine
from election_result_scraper import scrape_county_results, scrape_office_summary, EXAMPLES, get_update_time
import election_result_models as models


def main():
    office_summary = scrape_office_summary(EXAMPLES[-1])
    county_results = scrape_county_results(EXAMPLES[-1])

    county_models = []
    race_models = []
    candidate_models = []
    turnout_models = []
    for county_number, county in enumerate(county_results.values()):

        county_models.append(
            models.CountyElectionDetailsModel(
                    county_id=county.county_id,
                    county_name=county.county_name,
                    county_total_votes=county.county_total_votes,
                    county_palette_color=county.county_palette_color,
                    turnout_report_id=county.turnout_report_id,
                    update_time=county.update_time,
                    county_turnout_report=models.CountyTurnoutReportModel(
                        **dict(county.county_turnout_report)
                    ),
                ),
        )

        for race in county.county_races:
            race_models.append(models.CountyRaceDetailsModel(
                    office_id=race.office_id,
                    office_name=race.office_name,
                    office_total_votes=race.office_total_votes,
                    county_id=county.county_id,
                    county_name=county.county_name,
                    update_time=race.update_time,
                ),
            )

            for candidate in race.candidates:
                candidate_models.append(
                    models.CountyCandidateDetailsModel(
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
                        race_county_id=county.county_id,
                        race_id=int(race.office_id)
                    )
                )

    race_summaries = []
    candidate_summaries = []
    for summary in office_summary.values():
        race_summaries.append(
            models.StatewideRaceSummaryModel(
                office_id=summary.office_id,
                office_name=summary.office_name,
                race_details_id=summary.race_details_id,
                update_time=summary.update_time
            )
        )

        for candidate in summary.candidate_summary:
            candidate_summaries.append(
                models.StatewideCandidateSummaryModel(
                    candidate_name=candidate.candidate_name,
                    candidate_party=candidate.candidate_party,
                    candidate_palette_color=candidate.candidate_palette_color,
                    candidate_total_votes=candidate.candidate_total_votes,
                    candidate_ballot_order=candidate.candidate_ballot_order,
                    race_summary_id=int(summary.office_id),
                    update_time=candidate.update_time
                )
            )

    with SessionLocal() as session:
        session.add_all(turnout_models)
        session.commit()

        session.add_all(county_models)
        session.commit()

        session.add_all(race_models)
        session.commit()

        session.add_all(candidate_models)
        session.commit()

        session.add_all(race_summaries)
        session.commit()

        session.add_all(candidate_summaries)
        session.commit()
    return office_summary, county_results


office_summary, county_summary = main()

