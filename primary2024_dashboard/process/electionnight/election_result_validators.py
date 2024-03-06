from __future__ import annotations
from pydantic import BaseModel, Field, model_validator, field_validator, computed_field, ConfigDict
from nameparser import HumanName
from datetime import datetime
from typing import Optional, List


class CountyCandidateDetails(BaseModel):
    __config__ = ConfigDict(
        from_attributes=True)

    candidate_id: int = Field(alias='id')
    candidate_name: str = Field(alias='N')
    candidate_first_name: str = None
    candidate_last_name: str = None
    candidate_party: str = Field(alias='P')
    candidate_incumbent: bool = None
    candidate_early_votes: int = Field(alias='EV')
    candidate_election_day_votes: int = Field(alias='V')
    candidate_total_votes: int = Field(alias='V')
    candidate_vote_percent: float = Field(alias='PE')
    candidate_palette_color: str = Field(alias='C')
    race_county_id: Optional[int] = None
    race_id: int
    update_time: datetime

    @model_validator(mode='before')
    def set_incumbent(cls, values):
        if "(I)" in values['N']:
            values['candidate_incumbent'] = True
        else:
            values['candidate_incumbent'] = False
        return values

    @model_validator(mode='before')
    def parse_candidate_name(cls, values):
        name = HumanName(values['N'])
        values['candidate_first_name'] = name.first
        values['candidate_last_name'] = name.last
        return values

    @model_validator(mode='after')
    def parse_election_day_votes(self):
        self.candidate_total_votes = self.candidate_early_votes + self.candidate_election_day_votes
        return self

    @field_validator('candidate_party')
    def validate_party(cls, value):
        if value == 'REP':
            return 'Republican'
        elif value == 'DEM':
            return 'Democrat'
        elif value == 'LIB':
            return 'Libertarian'
        elif value == 'GRE':
            return 'Green'
        elif value == 'IND':
            return 'Independent'
        elif value == 'W':
            return 'Write-In'
        else:
            return value


class CountyRaceDetails(BaseModel):
    __config__ = ConfigDict(
        from_attributes=True)
    office_id: int = Field(alias='OID')
    office_name: str = Field(alias='ON')
    office_type: str
    office_total_votes: int = Field(alias='T')
    county_id: Optional[int]
    county_name: str
    update_time: datetime
    candidates: List[CountyCandidateDetails]

    @model_validator(mode='before')
    def set_office_type(cls, values):
        if "PRESIDENT" in values['ON']:
            values['office_type'] = "POTUS"
        elif "GOVERNOR" in values['ON']:
            values['office_type'] = "Governor"
        elif "STATE SENATE" in values['ON']:
            values['office_type'] = "SD"
        elif "STATE REPRESENTATIVE" in values['ON']:
            values['office_type'] = "HD"
        else:
            values['office_type'] = "Other"
        return values


class CountyTurnoutReport(BaseModel):
    __config__ = ConfigDict(
        from_attributes=True)
    county_id: int
    county_name: str
    total_precincts: int = Field(alias='PRP')
    precincts_reporting: int = Field(alias='PRR')
    registered_voters: int = Field(alias='RV')
    votes_counted: int = Field(alias='VC')
    turnout_percent: float = Field(alias='VT')
    polling_locations_total: int = Field(alias='NPL')
    polling_locations_reporting: int = Field(alias='PLR')
    polling_locations_percent: float = Field(alias='PLP')
    update_time: datetime


class CountyElectionDetails(BaseModel):
    __config__ = ConfigDict(
        from_attributes=True)
    id: int = None
    county_id: int
    county_name: str
    county_total_votes: int = Field(alias='TV')
    county_palette_color: str = Field(alias='C')
    update_time: datetime
    turnout_report_id: int
    county_turnout_report: CountyTurnoutReport
    county_races: List[CountyRaceDetails]


class StatewideRaceSummary(BaseModel):
    __config__ = ConfigDict(
        from_attributes=True)
    office_id: int = Field(alias='OID')
    office_name: str = Field(alias='ON')
    race_details_id: int = Field(alias='OID')
    update_time: datetime
    candidate_summary: List[StatewideCandidateSummary]


class StatewideCandidateSummary(BaseModel):
    __config__ = ConfigDict(
        from_attributes=True)
    candidate_name: str = Field(alias='N')
    candidate_party: str = Field(alias='P')
    candidate_palette_color: str = Field(alias='C')
    candidate_total_votes: int = Field(alias='T')
    candidate_ballot_order: int = Field(alias='O')
    race_summary_id: Optional[int] = None
    update_time: datetime
