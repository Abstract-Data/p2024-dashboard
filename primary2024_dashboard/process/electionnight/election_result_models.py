from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from primary2024_dashboard.process.electionnight.election_result_db import Base


class CandidateEndorsementsModel(Base):
    __tablename__ = 'candidate_endorsements'
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer)
    candidate_office_id = Column(Integer)
    district = Column(String, nullable=False)
    district_number = Column(Integer, nullable=False)
    candidate_first_name = Column(String, nullable=False)
    candidate_last_name = Column(String, nullable=False)
    paxton = Column(Boolean)
    abbott = Column(Boolean)
    perry = Column(Boolean)
    miller = Column(Boolean)
    patrick = Column(Boolean)
    # vote_percent = Column(Float)
    # win_or_made_runoff = Column(Boolean)


class CountyTurnoutReportModel(Base):
    __tablename__ = 'county_turnout_reports'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    county_id = Column(Integer)
    county_name = Column(String)
    total_precincts = Column(Integer)
    precincts_reporting = Column(Integer)
    registered_voters = Column(Integer)
    votes_counted = Column(Integer)
    turnout_percent = Column(Float)
    polling_locations_total = Column(Integer)
    polling_locations_reporting = Column(Integer)
    polling_locations_percent = Column(Float)
    update_time = Column(DateTime)


class CountyCandidateDetailsModel(Base):
    __tablename__ = 'county_candidate_details'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer)
    candidate_name = Column(String)
    candidate_first_name = Column(String)
    candidate_last_name = Column(String)
    candidate_party = Column(String)
    candidate_incumbent = Column(Boolean)
    candidate_early_votes = Column(Integer)
    candidate_election_day_votes = Column(Integer)
    candidate_total_votes = Column(Integer)
    candidate_vote_percent = Column(Float)
    candidate_palette_color = Column(String)
    candidate_office_id = Column(Integer)
    race_county_name = Column(String, ForeignKey('county_election_details.county_name'))
    race_id = Column(Integer, ForeignKey('county_race_details.office_id'))
    endorsement_id = Column(Integer, ForeignKey('candidate_endorsements.candidate_id'))
    endorsement = relationship('CandidateEndorsementsModel', backref='candidate', lazy='joined')
    update_time = Column(DateTime)


class CountyRaceDetailsModel(Base):
    __tablename__ = 'county_race_details'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    office_id = Column(Integer, ForeignKey('statewide_race_summary.office_id'))
    office_name = Column(String)
    office_type = Column(String)
    office_district_number = Column(Integer)
    office_total_votes = Column(Integer)
    county_id = Column(Integer, ForeignKey('county_election_details.county_id'))
    county_name = Column(String)
    update_time = Column(DateTime)
    candidates = relationship('CountyCandidateDetailsModel', backref='race', lazy='joined')


class CountyElectionDetailsModel(Base):
    __tablename__ = 'county_election_details'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    county_id = Column(Integer)
    county_name = Column(String)
    county_total_votes = Column(Integer)
    county_palette_color = Column(String)
    update_time = Column(DateTime)
    turnout_report_id = Column(Integer, ForeignKey('county_turnout_reports.county_id'))
    county_turnout_report = relationship('CountyTurnoutReportModel', backref='turnout_reports', lazy='joined')
    county_races = relationship('CountyRaceDetailsModel', backref='county', lazy='joined')


class StatewideCandidateSummaryModel(Base):
    __tablename__ = 'statewide_candidate_summary'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    candidate_name = Column(String)
    candidate_party = Column(String)
    candidate_palette_color = Column(String)
    candidate_total_votes = Column(Integer)
    candidate_ballot_order = Column(Integer)
    candidate_office_id = Column(Integer)
    race_summary_id = Column(Integer, ForeignKey('statewide_race_summary.office_id'))
    update_time = Column(DateTime)


class StatewideRaceSummaryModel(Base):
    __tablename__ = 'statewide_race_summary'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    office_id = Column(Integer)
    office_name = Column(String)
    office_type = Column(String)
    office_district_number = Column(Integer)
    race_details_id = Column(Integer, ForeignKey('county_race_details.office_id'))
    county_candidates_id = Column(Integer, ForeignKey('county_candidate_details.candidate_office_id'))
    update_time = Column(DateTime)
    statewide_summary = relationship('StatewideCandidateSummaryModel', backref='race_summary', lazy='joined')
    county_candidates = relationship('CountyCandidateDetailsModel', backref='county', lazy='joined')
