from __future__ import annotations
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    field_validator,
    computed_field,
    ConfigDict,
    ValidationError,
)
from nameparser import HumanName
from datetime import datetime
from typing import Optional, List, Optional, Annotated, Dict
from pathlib import Path
import csv

ENDORSEMENT_FILE = Path(__file__).parents[2] / 'data/endorsement_lists/P2024-TX-Endorsements.csv'


def read_endorsements(file_path: Path = ENDORSEMENT_FILE) -> list:
    # Read first row is header keys, each row after is values
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        return [dict(zip(headers, row)) for row in reader]


ENDORSEMENT_DICT = read_endorsements()


def set_office_type(cls, values):
    if "PRESIDENT" in values['ON']:
        values['office_type'] = "POTUS"
    elif "U. S. SENATOR" in values['ON']:
        values['office_type'] = "US Senate"
    elif "GOVERNOR" in values['ON']:
        values['office_type'] = "Governor"
    elif "STATE SENATOR" in values['ON']:
        values['office_type'] = "SD"
    elif "STATE REPRESENTATIVE" in values['ON']:
        values['office_type'] = "HD"
    elif "U. S. REPRESENTATIVE" in values['ON']:
        values['office_type'] = "CD"
    elif "STATE BOARD OF EDUCATION" in values['ON']:
        values['office_type'] = "SBOE"
    elif "COURT OF CRIMINAL APPEALS" in values['ON']:
        _values = values['ON'].split(",")
        _office = None
        if "PLACE" in values['ON']:
            _office = "CCA " + " ".join(_values[1].split(" ")[-2:])
            if "CHIEF" in values['ON']:
                _office = "CJ" + _values[1].split(" ")[0] + " CCA" + _values[-2:]
        if "PRESIDING" in values['ON']:
            _office = "PJCCA"
        values['office_type'] = _office

    elif "COURT OF APPEALS" in values['ON']:
        _values = values['ON'].split(",")
        _office = None
        if "PLACE" in values['ON']:
            if "DISTRICT" in values['ON']:
                _office = _values[1].split(" ")[1] + " COA" + _values[2]
            if "CHIEF" in values['ON']:
                _office = "CJ " + _values[1].split(" ")[0] + " COA" + _values[2]
        elif "CHIEF" in values['ON']:
            if "DISTRICT" in values['ON']:
                _office = "CJ " + _values[1].split(" ")[1] + " COA"
            else:
                _office = "CJ " + _values[1].split(" ")[0] + " COA"
        elif "PRESIDING" in values['ON']:
            _office = "PJCOA"
        else:
            _office = _values[1].split(" ")[0] + "COA"
        values['office_type'] = _office
    elif "JUDICIAL DISTRICT" in values['ON']:
        _values = values['ON'].split(",")
        _split = [x.strip() for x in _values[1].split(" ")]
        if "DISTRICT ATTORNEY" in values['ON']:
            # TODO: Fix to handle 'DISTRICT ATTORNEY FOR KLEBERG AND KENEDY COUNTIES'
            # TODO: Fix to handle 'CRIMINAL DISTRICT ATTORNEY WALLER COUNTY - UNEXPIRED TERM'
            values['office_type'] = f"DA, {_values[1].split(' ')[1]} JD"  # OUTPUT Ex: DA, 123TH JD
        else:
            values['office_type'] = _split[0] if len(_split) == 3 else " ".join(_split[:3]) + " JD"
    elif "COUNTY DISTRICT ATTORNEY" in values['ON']:
        _values = values['ON'].split(" ")
        values['office_type'] = ' '.join(_values[:1]) + " DA"
    # elif "DISTRICT ATTORNEY" in values['ON']:
    #     if "JUDICIAL DISTRICT" in values['ON']:
    #         _values = values['ON'].split(",")
    #         values['office_type'] = f"DA, {_values[0].split(' ')[0]} JD"
    elif "CRIMINAL DISTRICT ATTORNEY" in values['ON']:
        if "- UNEXPIRED TERM" in values['ON']:
            _values = values['ON'].split(" ")
            values['office_type'] = ' '.join(_values[1:-3]) + " CDA"
        else:
            _values = values['ON'].split(" ")
            values['office_type'] = f"CDA {' '.join(_values[-2:])}"
    elif "MULTICOUNTY COURT AT LAW" in values['ON']:
        _values = values['ON'].split(" ")
        values['office_type'] = _values[0] + " MCL"
    elif "RAILROAD COMMISSIONER" in values['ON']:
        values['office_type'] = "RRC"
    elif "SUPREME COURT" in values['ON']:
        _values = values['ON'].split(",")
        values['office_type'] = "SCOTX" + _values[2]
    else:
        values['office_type'] = "Other"
    return values


def set_district_number(cls, values):
    if "DISTRICT" in values['ON']:
        _office_num = values['ON'].split(" ")[-1]
        if _office_num.isdigit():
            values['office_district_number'] = int(_office_num)
    return values


class ElectionResultValidator(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        str_to_upper=True
    )


class CandidateEndorsements(ElectionResultValidator):
    id: Optional[int] = None
    candidate_id: Optional[int] = None
    candidate_office_id: Optional[int] = None
    district: Annotated[
        str,
        Field(
            alias='District Type',
            description="Type of district"
        )
    ]
    district_number: Annotated[
        int,
        Field(
            alias='District Number',
            description="District number"
        )
    ]
    paxton: Annotated[
        Optional[bool],
        Field(
            alias='Paxton Endorsed',
            description="Endorsed by Texas Attorney General Ken Paxton"
        )
    ] = None
    candidate_first_name: Annotated[
        str,
        Field(
            alias='Candidate First Name',
            description="First name of candidate"
        )
    ]
    candidate_last_name: Annotated[
        str,
        Field(
            alias='Candidate Last Name',
            description="Last name of candidate"
        )
    ]
    abbott: Annotated[
        Optional[bool],
        Field(
            alias='Abbott Endorsed',
            description="Endorsed by Texas Governor Greg Abbott"
        )
    ] = None
    perry: Annotated[
        Optional[bool],
        Field(
            alias='Rick Perry Endorsed',
            description="Endorsed by former Texas Governor Rick Perry"
        )
    ] = None
    miller: Annotated[
        Optional[bool],
        Field(
            alias='Sid Miller Endorsed',
            description="Endorsed by Texas Agriculture Commissioner Sid Miller"
        )
    ] = None
    patrick: Annotated[
        Optional[bool],
        Field(
            alias='Dan Patrick Endorsed',
            description="Endorsed by Texas Lieutenant Governor Dan Patrick"
        )
    ] = None

    # vote_percent: Optional[float] = None
    # win_or_made_runoff: Optional[bool] = None

    @model_validator(mode='before')
    def strip_blank_strings(cls, values):
        for k, v in values.items():
            if v == "":
                values[k] = None
        return values


ENDORSEMENTS = [CandidateEndorsements(**endorsement) for endorsement in ENDORSEMENT_DICT]


class CountyCandidateDetails(ElectionResultValidator):
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
    candidate_office_id: int = Field('OID')
    race_county_name: str
    race_id: int
    endorsement_id: Optional[int] = None
    endorsements: Optional[CandidateEndorsements] = None
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

    @model_validator(mode='after')
    def add_endorsement(self):
        # assuming endorsements is a list of all endorsements
        for endorsement in ENDORSEMENTS:

            if (self.candidate_first_name == endorsement.candidate_first_name and
                    self.candidate_last_name == endorsement.candidate_last_name):
                endorsement.candidate_id = self.candidate_id
                self.endorsements = endorsement
                break
        return self


class CountyRaceDetails(ElectionResultValidator):
    office_id: int = Field(alias='OID')
    office_name: str = Field(alias='ON')
    office_type: Optional[str] = None
    office_district_number: Optional[int] = None
    office_total_votes: int = Field(alias='T')
    county_id: Optional[int]
    county_name: str
    update_time: datetime
    candidates: Dict[str, CountyCandidateDetails]

    _set_office_type = model_validator(mode='before')(set_office_type)
    _set_district_number = model_validator(mode='before')(set_district_number)


class CountyTurnoutReport(ElectionResultValidator):
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


class CountyElectionDetails(ElectionResultValidator):
    id: int = None
    county_id: int
    county_name: str
    county_total_votes: int = Field(alias='TV')
    county_palette_color: str = Field(alias='C')
    update_time: datetime
    turnout_report_id: int
    county_turnout_report: CountyTurnoutReport
    county_races: Dict[str, CountyRaceDetails]


class StatewideRaceSummary(ElectionResultValidator):
    office_id: int = Field(alias='OID')
    office_name: str = Field(alias='ON')
    office_type: Optional[str] = None
    office_district_number: Optional[int] = None
    race_details_id: int
    county_candidates_id: int
    update_time: datetime
    statewide_summary: List[StatewideCandidateSummary]
    county_candidates: Optional[List[CountyCandidateDetails]] = None

    _set_office_type = model_validator(mode='before')(set_office_type)
    _set_district_number = model_validator(mode='before')(set_district_number)


class StatewideCandidateSummary(ElectionResultValidator):
    candidate_name: str = Field(alias='N')
    candidate_party: str = Field(alias='P')
    candidate_palette_color: str = Field(alias='C')
    candidate_total_votes: int = Field(alias='T')
    candidate_ballot_order: int = Field(alias='O')
    candidate_office_id: int
    race_summary_id: Optional[int] = None
    update_time: datetime


class OfficeElectionResult(ElectionResultValidator):
    office_id: int
    office_name: str
    office_type: Optional[str] = None
    office_district_number: Optional[int] = None
    candidates: List[CountyCandidateDetails]
    counties: List[CountyElectionDetails]
    update_time: datetime

    @property
    def all_precincts_reported(self):
        # Check if all precincts are reported in all counties
        return all(county.county_turnout_report.precincts_reporting == county.county_turnout_report.total_precincts for county in self.counties)

    @property
    def election_outcome(self):
        # Determine the election outcome based on the candidates' votes
        if not self.all_precincts_reported:
            return "Election results are not final."

        # Sort the candidates by their total votes in descending order
        sorted_candidates = sorted(self.candidates, key=lambda c: c.candidate_total_votes, reverse=True)

        # Check if any candidate has over 50% of the votes
        for candidate in sorted_candidates:
            if candidate.candidate_vote_percent > 50:
                return f"{candidate.candidate_name} won with over 50% of the votes."

        # If no candidate has over 50% of the votes, return the top two candidates
        top_two_candidates = sorted_candidates[:2]
        return f"No candidate has over 50% of the votes. The top two candidates are {top_two_candidates[0].candidate_name} and {top_two_candidates[1].candidate_name}."

    @property
    def turnout_reports(self):
        # Extract the turnout reports from each county
        return [county.county_turnout_report for county in self.counties]

    @turnout_reports.setter
    def turnout_reports(self, value):
        # This is a dummy setter, it doesn't actually change anything
        pass