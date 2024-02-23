from db_connect import Base, Session, engine
from process.electionnight import models, county_results, office_summary

county_models = []
race_models = []
candidate_models = []
for county_number, county in enumerate(county_results):
    county_models.append(models.CountyElectionDetailsModel(
        countyName=county.countyName,
        countyTotalVotes=county.countyTotalVotes,
        countyPaletteColor=county.countyPaletteColor,
        update_time=county.update_time
    ))
    for race in county.countyRaces:
        race_models.append(models.RaceDetailsModel(
            officeId=race.officeId,
            officeName=race.officeName,
            officeTotalVotes=race.officeTotalVotes,
            race_summary_id=int(race.officeId),
            county_id=county.countyName))
        for candidate in race.officeCandidates:
            candidate_models.append(models.CandidateDetailsModel(
                candidateName=candidate.candidateName,
                candidateParty=candidate.candidateParty,
                candidateFirstName=candidate.candidateFirstName,
                candidateLastName=candidate.candidateLastName,
                candidateIncumbent=candidate.candidateIncumbent,
                candidateEarlyVotes=candidate.candidateEarlyVotes,
                candidateElectionDayVotes=candidate.candidateElectionDayVotes,
                candidateTotalVotes=candidate.candidateTotalVotes,
                candidatePercentage=candidate.candidatePercentage,
                candidatePaletteColor=candidate.candidatePaletteColor,
                race_county_id=county.countyName,
                race_id=int(race.officeId)
            ))

race_summaries = []
candidate_summaries = []
for summary in office_summary:
    race_summaries.append(models.RaceSummaryDetailsModel(
        officeId=summary.officeId,
        officeName=summary.officeName,
        race_details_id=int(summary.officeId),
        update_time=summary.update_time
    ))
    for candidate in summary.officeCandidates:
        candidate_summaries.append(models.CandidateSummaryDetailsModel(
            candidateName=candidate.candidateName,
            candidateParty=candidate.candidateParty,
            candidatePaletteColor=candidate.candidatePaletteColor,
            candidateTotalVotes=candidate.candidateTotalVotes,
            candidateBallotOrder=candidate.candidateBallotOrder,
            race_summary_id=int(summary.officeId)
        ))

Base.metadata.create_all(engine)

with Session() as session:
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