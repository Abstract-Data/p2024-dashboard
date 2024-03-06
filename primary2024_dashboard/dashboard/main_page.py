from primary2024_dashboard.db_connect import SnowparkSession
import streamlit as st
from primary2024_dashboard.process.earlyvote import define
import httpx
import pandas as pd
import matplotlib.pyplot as plt
import asyncio


BASE_API_URL = 'http://127.0.0.1:8000'
PARTY_API_URL = BASE_API_URL + "/2024/primary/earlyvote/party/{party}"
DISTRICT_LIST_API_URL = BASE_API_URL + "/districts"
API_HEADER = {'X-API-KEY': 'fSSjyHUiklxdOr-EHDZ7bYk2nvWnp-wflCOu8yzx210'}
plt.style.use('dark_background')


async def get_district_data():
    async with httpx.AsyncClient() as client:
        DISTRICT_SENATE = await client.get(DISTRICT_LIST_API_URL + '/state/senate', headers=API_HEADER)
        DISTRICT_HOUSE = await client.get(DISTRICT_LIST_API_URL + '/state/house', headers=API_HEADER)
        DISTRICT_COUNTIES = await client.get(DISTRICT_LIST_API_URL + '/counties', headers=API_HEADER)
        return DISTRICT_SENATE, DISTRICT_HOUSE, DISTRICT_COUNTIES
# DISTRICT_SENATE = requests.get(DISTRICT_LIST_API_URL + '/state/senate', headers=API_HEADER).content
# DISTRICT_HOUSE = requests.get(DISTRICT_LIST_API_URL + '/state/house', headers=API_HEADER).content
# DISTRICT_COUNTIES = requests.get(DISTRICT_LIST_API_URL + '/counties', headers=API_HEADER).content

DISTRICT_SENATE, DISTRICT_HOUSE, DISTRICT_COUNTIES = asyncio.run(get_district_data())

st.set_page_config(
    layout="wide",
    page_title="2024 Texas Republican Primary",
    page_icon=":bar_chart:"
)

st.title("2024 Texas Primary Dashboard")


class PartyData:

    def __init__(self, party: str):
        self.party = party
        self.title = 'Republican' if party == 'rep' else 'Democratic'
        self.current = requests.get(PARTY_API_URL.format(party=party), headers=API_HEADER)

    def to_df(self, data: requests.Response) -> pd.DataFrame:
        return pd.DataFrame.from_records(data.json())


rep = PartyData('rep')
dem = PartyData('dem')

rep_df = rep.to_df(rep.current)
dem_df = dem.to_df(dem.current)

# Create a dropdown for the user to Select House District, Senate District, or County
choice = st.selectbox(
    'Select House District, Senate District, or County',
    options=['House District', 'Senate District', 'County'],
    index=None)

if choice == 'County':
    choice_col = define.COUNTY_COL.lower()
    choice_option = st.selectbox(
        label='Select House District',
        options=DISTRICT_COUNTIES,
        key='county',
        index=None
    )
elif choice == 'House District':
    choice_col = "hd"
    choice_option = st.selectbox(
        label='Select House District',
        options=DISTRICT_HOUSE,
        key='house',
        index=None
    )
elif choice == 'Senate District':
    choice_col = "sd"
    choice_option = st.selectbox(
        label='Select Senate District',
        options=DISTRICT_SENATE,
        key='senate',
        index=None
    )
else:
    choice_col = None
    choice_option = None


def party_overview_container(party: PartyData):

    # Adjust the tables to reflect the user's choice
    if choice and choice_option:
        if choice == 'County':
            st.write(f"## {party.title} Overview for {choice_option.title()} {choice}")
        else:
            st.write(f"## {party.title} Overview for {choice.title()} {choice_option}")
        df = pd.DataFrame.from_records(party.current)

        formatted_count = df.count()

        total_mail_in = df[
            (define.VOTE_METHOD_COL.lower() == 'MAIL-IN')
            &
            (choice_col == choice_option) & (define.YEAR_COL.lower() == 2024)].count()

        total_in_person = df[
            (define.VOTE_METHOD_COL.lower() == 'IN-PERSON')
            &
            (choice_col == choice_option) & (define.YEAR_COL.lower() == 2024)].count()
    else:
        st.write(f"## {party.title} Overview")
        df = pd.DataFrame.from_records(party.current)
        df = df[df[define.YEAR_COL.lower() == 2024]]
        formatted_count = df.count()
        total_mail_in = df[define.VOTE_METHOD_COL.lower() == 'MAIL-IN'].count()
        total_in_person = df[define.VOTE_METHOD_COL.lower() == 'IN-PERSON'].count()

    scorecard_container = st.container()
    by_day_container = st.container()
    with scorecard_container:
        scorecard_col1, scorecard_col2, scorecard_col3 = st.columns(3)
        with scorecard_col1:
            st.metric(
                "Total Voters",
                f"{formatted_count:,}")
        with scorecard_col2:
            st.metric(
                "Mail-in Ballots",
                f"{total_mail_in:,}"
            )
        with scorecard_col3:
            st.metric(
                "In-Person Voters",
                f"{total_in_person:,}"
            )

    with (by_day_container):
        st.subheader("Voter Turnout by Day")
        st.write("""
        This section shows the number of voters who have cast ballots each day of early voting.
        """)
        by_day_column, graphing_column = st.columns([1, 1], gap="small")
        by_age_column, graphing_age_column = st.columns([1, 1], gap="small")
        with by_day_column:
            st.write("Raw Totals by Day")

            byDay_ct = pd.crosstab(
                df[define.DAY_IN_EV_COL],
                df[define.YEAR_COL])
            st.dataframe(byDay_ct, use_container_width=False)

        with graphing_column:
            st.write("Graph of Voter Turnout by Day")
            fig, ax = plt.subplots()
            ax.set_facecolor('#0F1116')
            fig.background = '#0F1116'
            byDay_line = byDay_ct.plot(ax=ax, kind='line', xlabel="Day", ylabel="Voter Count")
            st.pyplot(fig, use_container_width=True)

        with by_age_column:
            st.write("Raw Totals by Age Group")

            byAge_ct = pd.crosstab(
                df[define.AGE_RANGE_COL],
                df[define.YEAR_COL])
            # Place 'Unknown' at the top of the DataFrame
            byAge_ct = byAge_ct.reindex(index=['Unknown', '18-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75-84', '85+'])
            st.dataframe(byAge_ct, use_container_width=False)

        with graphing_age_column:
            st.write("Graph of Voter Turnout by Age Group")
            fig, ax = plt.subplots()
            ax.set_facecolor('#0F1116')
            fig.background = '#0F1116'
            byAge_line = byAge_ct.plot(ax=ax, kind='line', xlabel="Age Range", ylabel="Voter Count")
            st.pyplot(fig, use_container_width=True)


rep_tab, dem_tab = st.tabs(["Republican", "Democrat"])

with rep_tab:
    party_overview_container(rep)

with dem_tab:
    party_overview_container(dem)
