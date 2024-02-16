from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from db_connect import Base


class CandidateDetailsModel(Base):
    __tablename__ = 'candidate_details'

    id = Column(Integer, primary_key=True)
    candidateName = Column(String)
    candidateFirstName = Column(String)
    candidateLastName = Column(String)
    candidateParty = Column(String)
    candidateIncumbent = Column(Boolean)
    candidateEarlyVotes = Column(Integer)
    candidateElectionDayVotes = Column(Integer)
    candidateTotalVotes = Column(Integer)
    candidatePercentage = Column(Float)
    candidatePaletteColor = Column(String)
    race_county_id = Column(Integer, ForeignKey('county_election_details.countyName'))
    race_id = Column(Integer, ForeignKey('race_details.officeId'))
    update_time = Column(DateTime)


class RaceDetailsModel(Base):
    __tablename__ = 'race_details'

    id = Column(Integer, primary_key=True)
    officeId = Column(Integer, ForeignKey('race_summary_details.officeId'))
    officeName = Column(String)
    officeTotalVotes = Column(Integer)
    county_id = Column(Integer, ForeignKey('county_election_details.id'))
    race_summary_id = Column(Integer, ForeignKey('race_summary_details.officeId'))
    update_time = Column(DateTime)
    candidates = relationship('CandidateDetailsModel', backref='race')


class CountyElectionDetailsModel(Base):
    __tablename__ = 'county_election_details'

    id = Column(Integer, primary_key=True)
    countyName = Column(String)
    countyTotalVotes = Column(Integer)
    countyPaletteColor = Column(String)
    update_time = Column(DateTime)
    races = relationship('RaceDetailsModel', backref='county')


class CandidateSummaryDetailsModel(Base):
    __tablename__ = 'candidate_summary_details'

    id = Column(Integer, primary_key=True)
    candidateName = Column(String)
    candidateParty = Column(String)
    candidatePaletteColor = Column(String)
    candidateTotalVotes = Column(Integer)
    candidateBallotOrder = Column(Integer)
    race_summary_id = Column(Integer, ForeignKey('race_summary_details.officeId'))
    update_time = Column(DateTime)


class RaceSummaryDetailsModel(Base):
    __tablename__ = 'race_summary_details'
    id = Column(Integer, primary_key=True)
    officeId = Column(Integer)
    officeName = Column(String)
    race_details_id = Column(Integer, ForeignKey('race_details.officeId'))
    update_time = Column(DateTime)
    candidates_summary = relationship('CandidateSummaryDetailsModel', backref='race_summary')
