from pydantic import BaseModel, Field, model_validator, field_validator
from nameparser import HumanName
from datetime import datetime



class CandidateDetails(BaseModel):
    candidateName: str = Field(alias='N')
    candidateFirstName: str = None
    candidateLastName: str = None
    candidateParty: str = Field(alias='P')
    candidateIncumbent: bool = None
    candidateEarlyVotes: int = Field(alias='EV')
    candidateElectionDayVotes: int = 0
    candidateTotalVotes: int = Field(alias='V')
    candidatePercentage: float = Field(alias='PE')
    candidatePaletteColor: str = Field(alias='C')
    update_time: datetime = datetime.now()

    @model_validator(mode='before')
    def set_incumbent(cls, values):
        if "(I)" in values['N']:
            values['candidateIncumbent'] = True
        else:
            values['candidateIncumbent'] = False
        return values

    @model_validator(mode='before')
    def parse_candidate_name(cls, values):
        name = HumanName(values['N'])
        values['candidateFirstName'] = name.first
        values['candidateLastName'] = name.last
        return values

    @model_validator(mode='after')
    def parse_election_day_votes(self):
        if self.candidateTotalVotes > self.candidateEarlyVotes:
            self.candidateElectionDayVotes = self.candidateTotalVotes - self.candidateEarlyVotes
        return self

    @field_validator('candidateParty')
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


class RaceDetails(BaseModel):
    officeId: int = Field(alias='OID')
    officeName: str = Field(alias='ON')
    officeTotalVotes: int = Field(alias='T')
    update_time: datetime = datetime.now()
    officeCandidates: list[CandidateDetails]


class CountyElectionDetails(BaseModel):
    id: int = None
    countyName: str = Field(alias='N')
    countyTotalVotes: int = Field(alias='TV')
    countyPaletteColor: str = Field(alias='C')
    update_time: datetime = datetime.now()
    countyRaces: list[RaceDetails]


class RaceSummaryDetails(BaseModel):
    officeId: int = Field(alias='OID')
    officeName: str = Field(alias='ON')
    update_time: datetime = datetime.now()
    officeCandidates: list['CandidateSummaryDetails']


class CandidateSummaryDetails(BaseModel):
    candidateName: str = Field(alias='N')
    candidateParty: str = Field(alias='P')
    candidatePaletteColor: str = Field(alias='C')
    candidateTotalVotes: int = Field(alias='T')
    candidateBallotOrder: int = Field(alias='O')
    update_time: datetime = datetime.now()
