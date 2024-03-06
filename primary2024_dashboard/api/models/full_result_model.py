from pydantic import BaseModel, Field, AliasChoices, PastDate, ConfigDict
from typing import Optional, Annotated


class APIVoterDetails(BaseModel):
    __config__ = ConfigDict(
        str_strip_whitespace=True,
        from_attributes=True,
        extra='ignore')

    county: str = Field(alias='COUNTY')
    age_range: str = Field(alias='AGE_RANGE')
    sd: Annotated[Optional[str], Field(alias='SD')] = None
    hd: Annotated[Optional[str], Field(alias='HD')] = None
    cd: Annotated[Optional[str], Field(alias='CD')] = None
    precinct: Annotated[Optional[str], Field(alias='PRECINCT')] = None
    poll_place_id: Annotated[Optional[str], Field(alias='POLL_PLACE_ID')] = None
    poll_place_name: Annotated[Optional[str], Field(alias='POLL_PLACE_NAME')] = None
    vote_method: Annotated[str, Field(validation_alias=AliasChoices('VOTING_METHOD', 'VOTE_METHOD'))]
    vote_date: Annotated[PastDate, Field(alias='VOTE_DATE')]
    year: Annotated[int, Field(alias='YEAR')]
    primary_voted_in: Annotated[str, Field(alias='PRIMARY_VOTED_IN')]
    day_in_ev: Annotated[int, Field(alias='DAY_IN_EV')]
    vep_registration: Annotated[Optional[int], Field(alias='VEP_REGISTRATION')] = None
    new_voter: Annotated[Optional[bool], Field(alias='NEW_VOTER')] = None
    primary_count: Annotated[int, Field(alias='PRIMARY_COUNT')] = 0
    general_count: Annotated[int, Field(alias='GENERAL_COUNT')] = 0
    primary_count_dem: Annotated[int, Field(alias='PRIMARY_COUNT_DEM')] = 0
    primary_count_rep: Annotated[int, Field(alias='PRIMARY_COUNT_REP')] = 0
    count: Annotated[int, Field(alias='VUID_COUNT')] = 0
