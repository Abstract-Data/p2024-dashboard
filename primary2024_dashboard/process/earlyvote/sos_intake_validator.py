from pydantic import BaseModel, model_validator, field_validator, Field, ConfigDict
from typing import Optional, Annotated
from datetime import date, datetime
from nameparser import HumanName
from primary2024_dashboard.utils.validation_funcs import clear_blank_strings

in_person_start_date = datetime.strptime('2024-02-20', '%Y-%m-%d')
election_day = datetime.strptime('2024-03-05', '%Y-%m-%d')
midterm_2022 = datetime.strptime('2022-11-08', '%Y-%m-%d')


class SOSVoterIntake(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        from_attributes=True,
        extra='ignore'
    )
    vuid: Annotated[str, Field(alias='ID_VOTER')]
    county: Annotated[str, Field(alias='COUNTY')]
    fullName: Annotated[str, Field(alias='VOTER_NAME')]
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    precinct: Annotated[Optional[str], Field(alias='PRECINCT')] = None
    poll_place_id: Annotated[Optional[str], Field(alias='POLL PLACE ID')] = None
    poll_place_name: Annotated[Optional[str], Field(alias='POLL PLACE NAME')] = None
    vote_method: Annotated[str, Field(alias='VOTING_METHOD', pattern=r'IN-PERSON|MAIL-IN')]
    vote_date: date = Field(alias='VOTE_DATE')
    year: int = Field(alias='YEAR')
    day_in_ev: int = Field(alias='DAY_IN_EV')
    primary_voted_in: str = Field(alias='PRIMARY_VOTED_IN')
    file_date_modified: datetime = Field(alias='DATE_MODIFIED')
    file_date_added: datetime = Field(alias='DATE_ADDED')

    _strip_blank_strings = model_validator(mode='before')(clear_blank_strings)


    @model_validator(mode='before')
    @classmethod
    def split_name(cls, v: dict):
        name = HumanName(v['VOTER_NAME'])
        v['firstName'] = name.first
        v['lastName'] = name.last
        return v

    @model_validator(mode='after')
    def check_year_same_as_vote_date(self):
        if not datetime.strptime(str(self.year), '%Y').year != self.vote_date.year:
            return self
        else:
            raise ValueError('Year does not match vote date')
