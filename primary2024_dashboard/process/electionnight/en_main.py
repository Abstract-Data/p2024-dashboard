from primary2024_dashboard.process.electionnight.en_process import office_summary, county_summary
import primary2024_dashboard.process.electionnight.election_result_validators as validators
from primary2024_dashboard.process.electionnight.election_result_db import SessionLocal, Base, engine
from datetime import datetime

Base.metadata.create_all(bind=engine)

county_race_details = Base.metadata.tables['county_race_details']
county_candidate_details = Base.metadata.tables['county_candidate_details']
county_election_details = Base.metadata.tables['county_election_details']
county_turnout_reports = Base.metadata.tables['county_turnout_reports']

with SessionLocal() as session:
    county_race_models = [validators.CountyRaceDetails.construct(**x) for x in session.query(county_race_details).all()]
    county_candidate_models = [validators.CountyCandidateDetails.construct(**x) for x in session.query(county_candidate_details).all()]
    county_election_models = [validators.CountyElectionDetails.construct(**x) for x in session.query(county_election_details).all()]
    county_turnout_models = [validators.CountyTurnoutReport.construct(**x) for x in session.query(county_turnout_reports).all()]

