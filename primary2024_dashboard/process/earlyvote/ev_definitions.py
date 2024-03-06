DB_VOTERFILE_TABLE = 'VEP2024.VOTERFILE'
DB_ELECTIONHISTORY_TABLE = 'VEP2024.ELECTIONHISTORY'
DB_FULL_UNION_TABLE = "ELECTIONHISTORY_TX.P2024_UNION"
VOTERID_COL = 'VUID'
YEAR_COL = 'YEAR'
VOTE_DATE_COL = 'VOTE_DATE'
VOTE_METHOD_COL = 'VOTE_METHOD'
DAY_IN_EV_COL = 'DAY_IN_EV'
AGE_RANGE_COL = 'AGE_RANGE'
PRIMARY_VOTED_IN = 'PRIMARY_VOTED_IN'
REGISTRATION_DATE_COL = 'EDR'
COUNTY_COL = 'COUNTY'
HOUSE_DISTRICT_COL = 'STATE_LEGISLATIVE_LOWER'
SENATE_DISTRICT_COL = 'STATE_LEGISLATIVE_UPPER'
SD_COL = 'SD'
HD_COL = 'HD'
CD_COL = 'CD'
VEP_REGISTRATION_COL = 'VEP_REGISTRATION'
PRIMARY_COUNT_REP = 'PRIMARY_COUNT_REP'
PRIMARY_COUNT_DEM = 'PRIMARY_COUNT_DEM'
DISTRICT_COLS = [SD_COL, HD_COL, CD_COL]
PARTY_TO_COUNT = [VOTERID_COL, PRIMARY_COUNT_REP, PRIMARY_COUNT_DEM]
PARTY_TO_COMPARE = [('PERCENT_DEM', PRIMARY_COUNT_DEM), ('PERCENT_REP', PRIMARY_COUNT_REP)]
CONDENSED_COLS = [COUNTY_COL, DAY_IN_EV_COL, VOTE_DATE_COL, VOTE_METHOD_COL, VOTERID_COL, SD_COL, HD_COL, CD_COL,
                  AGE_RANGE_COL, REGISTRATION_DATE_COL, VEP_REGISTRATION_COL, PRIMARY_COUNT_DEM, PRIMARY_COUNT_REP,
                  VEP_REGISTRATION_COL, YEAR_COL]

MAKE_NULL_LIST = [
    'general_count',
    'primary_count',
    PRIMARY_COUNT_DEM,
    PRIMARY_COUNT_REP,
    'primary_percent_dem',
    'general_percent_dem',
    'primary_percent_rep',
    'general_percent_rep',
    'age'
]
