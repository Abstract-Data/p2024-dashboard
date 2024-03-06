from primary2024_dashboard.process.earlyvote.ev_crosstabs import DailyTurnoutCrosstabs
from primary2024_dashboard.db_connect import SnowparkSession
from primary2024_dashboard.process.earlyvote.ev_process import LoadToSnowflake
# TODO: Republican Primary Score Turnout, Break Out By District
# TODO: Democrat Primary Score Turnout, Break Out By District

# snow = LoadToSnowflake()
# snow.load_current_election()
gop_ct = DailyTurnoutCrosstabs("rep", SnowparkSession)
# dem_ct = DailyTurnoutCrosstabs("dem", SnowparkSession)
gop_data = gop_ct.create_crosstabs()
# dem_data = dem_ct.create_crosstabs()
