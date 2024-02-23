from pydantic import BaseModel, model_validator, field_validator, Field, ConfigDict
from typing import Optional, Annotated
from datetime import date, datetime
from nameparser import HumanName

in_person_start_date = date(2024, 2, 20)
election_day = date(2024, 3, 5)


class VoterDetails(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        from_attributes=True,
        extra='ignore'
    )
    vuid: int = Field(alias='ID_VOTER')
    county: str = Field(alias='COUNTY')
    fullName: str = Field(alias='VOTER_NAME')
    firstName: Optional[str]
    lastName: Optional[str]
    dob: Annotated[Optional[date], Field(alias='DOB')] = None
    age: Optional[int] = None
    age_range: Optional[str] = None
    sd: Annotated[Optional[str], Field(alias='STATE_LEGISLATIVE_UPPER')] = None
    hd: Annotated[Optional[str], Field(alias='STATE_LEGISLATIVE_LOWER')] = None
    cd: Annotated[Optional[str], Field(alias='CONGRESSIONAL')] = None
    precinct: str = Field(alias='PRECINCT')
    poll_place_id: Annotated[Optional[str], Field(alias='POLL PLACE ID')] = None
    poll_place_name: Annotated[Optional[str], Field(alias='POLL PLACE NAME')] = None
    vote_method: str = Field(alias='VOTING_METHOD')
    vote_date: date = Field(alias='VOTE_DATE')
    day_in_ev: int = Field(alias='DAY_IN_EV')
    vep_registration: Annotated[Optional[bool], Field(alias='VEP_VUID')] = None
    gen18: Annotated[Optional[str], Field(alias='GEN18')] = None
    gen19: Annotated[Optional[str], Field(alias='GEN19')] = None
    gen20: Annotated[Optional[str], Field(alias='GEN20')] = None
    gen21: Annotated[Optional[str], Field(alias='GEN21')] = None
    gen22: Annotated[Optional[str], Field(alias='GEN22')] = None
    gen23: Annotated[Optional[str], Field(alias='GEN23')] = None
    pri18: Annotated[Optional[str], Field(alias='PRI18')] = None
    pri20: Annotated[Optional[str], Field(alias='PRI20')] = None
    pri22: Annotated[Optional[str], Field(alias='PRI22')] = None
    pri24: Optional[str] = None
    primary_count: int = 0
    general_count: int = 0
    primary_count_dem: int = 0
    primary_count_rep: int = 0
    primary_percent_dem: Optional[float] = 0.0
    primary_percent_rep: Optional[float] = 0.0
    general_percent_dem: Optional[float] = 0.0
    general_percent_rep: Optional[float] = 0.0

    @field_validator('vep_registration', mode='before')
    def set_vep_registration(cls, v):
        if v:
            return True

    @model_validator(mode='before')
    @classmethod
    def split_name(cls, v: dict):
        name = HumanName(v['VOTER_NAME'])
        v['firstName'] = name.first
        v['lastName'] = name.last
        return v

    @model_validator(mode='before')
    @classmethod
    def set_pri24_method(cls, v: dict):
        if v['VOTING_METHOD'] == 'IN-PERSON' and v['VOTE_DATE'].year == election_day.year:
            v['pri24'] = 'RE'

        else:
            v['pri24'] = 'R'

        if v['VOTING_METHOD'] == 'MAIL-IN':
            v['pri24'] = 'RA'
        return v

    @model_validator(mode='before')
    @classmethod
    def age(cls, v):
        if v['DOB']:
            _dob = datetime.strptime(v['DOB'], '%Y-%m-%d')
            today = date.today()
            v['age'] = today.year - _dob.year - ((today.month, today.day) < (_dob.month, _dob.day))
        return v

    @model_validator(mode='after')
    def set_primary_score(self):
        _primary_election_dates = [self.pri18, self.pri20, self.pri22, self.pri24]
        for election in _primary_election_dates:
            if election is not None:
                self.primary_count += 1
        return self

    @model_validator(mode='after')
    def set_general_score(self):
        _general_election_dates = [self.gen18, self.gen20, self.gen20]
        for election in _general_election_dates:
            if election is not None:
                self.general_count += 1
        return self

    @model_validator(mode='after')
    def calculate_party_primary_count(self):
        _primary_election_dates = [self.pri18, self.pri20, self.pri22, self.pri24]
        for election in _primary_election_dates:
            if election in ['D', 'DE', 'DA']:
                self.primary_count_dem += 1
            if election in ['R', 'RE', 'RA']:
                self.primary_count_rep += 1
        return self

    @model_validator(mode='after')
    def calculate_dem_percent(self):
        _general_election_dates = [self.gen18, self.gen20, self.gen20]
        _primary_election_dates = [self.pri18, self.pri20, self.pri22, self.pri24]
        if self.primary_count > 0:
            self.primary_percent_dem = round(self.primary_percent_dem / len(_primary_election_dates), 2)
        if self.general_count > 0:
            self.general_percent_dem = round(self.primary_count_dem / len(_general_election_dates), 2)
            if self.general_percent_dem == 1.33:
                self.general_percent_dem = 1.0
        return self

    @model_validator(mode='after')
    def calculate_rep_percent(self):
        _general_election_dates = [self.gen18, self.gen20, self.gen20]
        _primary_election_dates = [self.pri18, self.pri20, self.pri22, self.pri24]
        if self.primary_count > 0:
            self.primary_percent_rep = round(self.primary_count_rep / len(_primary_election_dates), 2)
        if self.general_count > 0:
            self.general_percent_rep = round(self.primary_count_rep / len(_general_election_dates), 2)
            if self.general_percent_rep == 1.33:
                self.general_percent_rep = 1.0
        return self

    @model_validator(mode='after')
    def age_range(self):
        if self.age < 25:
            self.age_range = '18-24'
        if 25 <= self.age < 35:
            self.age_range = '25-34'
        if 35 <= self.age < 45:
            self.age_range = '35-44'
        if 45 <= self.age < 55:
            self.age_range = '45-54'
        if 55 <= self.age < 65:
            self.age_range = '55-64'
        if 65 <= self.age < 75:
            self.age_range = '65-74'
        if 75 <= self.age < 85:
            self.age_range = '75-84'
        if 85 <= self.age:
            self.age_range = '85+'
        return self
