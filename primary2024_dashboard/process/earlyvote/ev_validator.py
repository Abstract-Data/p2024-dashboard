from pydantic import BaseModel, model_validator, Field, ConfigDict, AliasChoices, PastDate
from typing import Optional, Annotated, List, ClassVar
from datetime import date, datetime
from nameparser import HumanName

in_person_start_date = datetime.strptime('2024-02-20', '%Y-%m-%d')
election_day = datetime.strptime('2024-03-05', '%Y-%m-%d')
midterm_2022 = datetime.strptime('2022-11-08', '%Y-%m-%d')


class VoterDetails(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        from_attributes=True,
        extra='ignore',

    )
    vuid: int = Field(alias='VUID')
    county: str = Field(alias='COUNTY')
    fullName: Optional[str] = Field(alias='FULLNAME')
    firstName: Annotated[Optional[str], Field(alias='FIRSTNAME')] = None
    lastName: Annotated[Optional[str], Field(alias='LASTNAME')] = None
    dob: Annotated[Optional[PastDate], Field(alias='DOB')] = None
    edr: Annotated[Optional[date], Field(alias='EDR')] = None
    age: Optional[int] = None
    age_range: Optional[str] = None
    sd: Annotated[Optional[str], Field(alias='STATE_LEGISLATIVE_UPPER')] = None
    hd: Annotated[Optional[str], Field(alias='STATE_LEGISLATIVE_LOWER')] = None
    cd: Annotated[Optional[str], Field(alias='CONGRESSIONAL')] = None
    precinct: Annotated[Optional[str], Field(alias='PRECINCT')] = None
    poll_place_id: Annotated[Optional[str], Field(alias='POLL PLACE ID')] = None
    poll_place_name: Annotated[Optional[str], Field(alias='POLL PLACE NAME')] = None
    vote_method: str = Field(validation_alias=AliasChoices('VOTING_METHOD', 'VOTE_METHOD'))
    vote_date: PastDate = Field(alias='VOTE_DATE')
    year: int = Field(alias='YEAR')
    primary_voted_in: str = Field(alias='PRIMARY_VOTED_IN')
    day_in_ev: int = Field(alias='DAY_IN_EV')
    vep_registration: Annotated[Optional[int], Field(alias='VEP_VUID')] = None
    new_voter: Optional[bool] = None
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

    # @model_validator(mode='before')
    # @classmethod
    # def adjust_in_person_before_ev_date(cls, values: dict):
    #     if values['VOTING_METHOD'] == 'IN-PERSON' and values['DAY_IN_EV'] is None:
    #         values['day_in_ev'] = 1
    #     return values

    # @field_validator('vep_registration', mode='before')
    # @classmethod
    # def set_vep_registration(cls, v: dict):
    #     # If there is a value change to integer
    #     if v:
    #         v['VEP_VUID'] = int(v['VEP_VUID'])

    @model_validator(mode='before')
    @classmethod
    def set_new_voter(cls, v: dict):
        if v['EDR']:
            v['EDR'] = datetime.strptime(v['EDR'], '%Y-%m-%d')
            if v['EDR'] > midterm_2022:
                v['new_voter'] = True
        return v

    # @model_validator(mode='before')
    # @classmethod
    # def split_name(cls, v: dict):
    #     name = HumanName(v['VOTER_NAME'])
    #     v['firstName'] = name.first
    #     v['lastName'] = name.last
    #     return v

    @model_validator(mode='before')
    @classmethod
    def set_pri24_method(cls, v: dict):
        if v['VOTE_DATE'].year == election_day.year:
            if v['VOTE_METHOD'] == 'MAIL-IN':
                v['pri24'] = 'RA'
            elif v['VOTE_METHOD'] == 'IN-PERSON' and v['VOTE_DATE'] < election_day.date():
                v['pri24'] = 'RE'
            else:
                v['pri24'] = 'R'
        return v

    @model_validator(mode='before')
    @classmethod
    def set_age(cls, v: dict):
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
            self.primary_percent_dem = round(self.primary_count_dem / len(_primary_election_dates), 2)
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
    def set_age_range(self):
        if self.age:
            _age = self.age
            if _age < 25:
                self.age_range = '18-24'
            if 25 <= _age < 35:
                self.age_range = '25-34'
            if 35 <= _age < 45:
                self.age_range = '35-44'
            if 45 <= _age < 55:
                self.age_range = '45-54'
            if 55 <= _age < 65:
                self.age_range = '55-64'
            if 65 <= _age < 75:
                self.age_range = '65-74'
            if 75 <= _age < 85:
                self.age_range = '75-84'
            if 85 <= _age:
                self.age_range = '85+'
        else:
            self.age_range = 'Unknown'
        return self
