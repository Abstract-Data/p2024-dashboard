
from __future__ import annotations
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime
from pathlib import Path
import shutil
from rich.progress import Progress
from dataclasses import dataclass, field
from typing import ClassVar

DOWNLOAD_PATH = Path.home() / 'Downloads'  # Update this path
TEXAS_SOS_ELECTION_LIST_URL = "https://earlyvoting.texas-election.com/Elections/getElectionDetails.do"
# @dataclass
# class WebDriver:
#     download_directory: ClassVar[Path] = None
#     options: ClassVar[Options] = Options()
#     driver: webdriver.Chrome = None
#
#     @classmethod
#     def set_options(cls) -> Options:
#         cls.download_directory = DOWNLOAD_PATH if not cls.download_directory else Path(cls.download_directory)
#         prefs = {
#             'download.default_directory': str(cls.download_directory)
#         }
#         cls.options.add_experimental_option('prefs', prefs)
#         # options.headless = True  # hide GUI
#         cls.options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
#         cls.options.add_argument("start-maximized")  # ensure window is full-screen
#         return cls.options
#
#     @property
#     def DRIVER(self) -> webdriver.Chrome:
#         self.driver = webdriver.Chrome(options=self.set_options())
#         return self.driver
#
#
#
# @dataclass
# class SelectElection:
#     year: str
#     party: str = None
#     primary: bool = False
#     driver: ClassVar[WebDriver] = WebDriver()
#
#     @property
#     def _party(self) -> str | None:
#         if self.party:
#             if self.party.lower() in ["dem", "d", "democratic"]:
#                 self.party = "Democratic".upper()
#             elif self.party.lower() in ["rep", "r", "republican", "gop"]:
#                 self.party = "Republican".upper()
#             return self.party.upper()
#         else:
#             return None
#
#     def select_election(self) -> 'SelectElection':
#         driver = self.driver.DRIVER
#         driver.get(TEXAS_SOS_ELECTION_LIST_URL)
#         election_type_dropdown = Select(driver.find_elements(By.CLASS_NAME, value="form-control")[0])
#         sleep(2)
#         submit_button = driver.find_elements(By.XPATH, value="//button[text()='Submit']")[0]
#         _party_conditional = self.party if self.party else None
#         for election in election_type_dropdown.options:
#             if self.primary:
#                 _party_conditional = f"{self.primary} PRIMARY"
#             if self.year in election.text and _party_conditional in election.text:
#                 election_type_dropdown.select_by_visible_text(election.text)
#                 break
#         submit_button.click()
#         return self
#
#     def export_early_vote_lists(self) -> 'SelectElection':
#         driver = self.driver.DRIVER
#         early_vote_date_dropdown = Select(driver.find_element(By.ID, value="selectedDate"))
#         early_vote_dates = [x.text for x in early_vote_date_dropdown.options]
#
#         previous_day_totals = None
#         with Progress() as progress:
#             all_tasks = progress.add_task("Downloading Early Vote Data", total=len(early_vote_dates))
#
#             for ev_day in early_vote_dates:
#                 try:
#                     date_format = (datetime.strptime(ev_day, "%B %d,%Y").strftime("%Y%m%d"))
#                     task = progress.add_task(f"Downloading {date_format}", total=1)
#                     _dropdown = Select(driver.find_element(By.ID, value="selectedDate"))
#                     _dropdown.select_by_visible_text(ev_day)
#                     _submit = driver.find_element(By.XPATH, value="//button[text()='Submit']")
#                     _submit.click()
#                     sleep(.5)
#                     _day_totals = driver.find_elements(
#                         By.XPATH,
#                         value='//*[@id="electionsInfoForm"]/div/div[2]/div/div[3]/div/table/tbody/tr[255]')[0]
#                     if _day_totals.text == previous_day_totals:
#                         _go_back = driver.find_element(By.XPATH, value="//button[text()='Previous']")
#                         _go_back.click()
#
#                     else:
#                         _generate_report_button = driver.find_element(By.XPATH, value="//button[text()='Generate Statewide Report']")
#                         _generate_report_button.click()
#                         sleep(2)
#
#                         # Get list of files
#                         files = list(self.driver.download_directory.glob('*'))
#                         # Find downloaded file
#                         most_recent_file = max(files, key=lambda file: file.stat().st_mtime)
#                         sleep(1)
#                         # Rename and move file
#                         shutil.move(most_recent_file, file_path / f"{date_format}.csv")
#                         progress.update(task, completed=1)
#                         previous_day_totals = _day_totals.text
#                         _go_back = driver.find_element(By.XPATH, value="//button[text()='Previous']")
#                         _go_back.click()
#
#                 except ValueError:
#                     progress.update(all_tasks, total=(len(early_vote_dates) - 1))
#                     pass
#                 progress.update(all_tasks, advance=1)
#             progress.update(all_tasks, completed=1)
#
#         driver.quit()
#         return self
#
#
# texas = SelectElection("2024", "rep", primary=True)
# texas.select_election()

# options = Options()
# # Set the default download directory
# prefs = {'download.default_directory': str(DOWNLOAD_PATH)}
# options.add_experimental_option('prefs', prefs)
# # options.headless = True  # hide GUI
# options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
# options.add_argument("start-maximized")  # ensure window is full-screen

# Set up a webdriver instance
# driver = webdriver.Chrome(options=options)

# Navigate to the webpage
# driver.get(TEXAS_SOS_ELECTION_LIST_URL)

# Define the year and title you're looking for
# year = "2024"
# title = "Republican Primary".upper()


file_path = Path(__file__).parents[1] / "data" / "earlyvote_days" / "2024" / "primary"


def build_webdriver(browser_download_path: Path = DOWNLOAD_PATH):
    options = Options()
    # Set the default download directory
    prefs = {'download.default_directory': str(browser_download_path)}
    options.add_experimental_option('prefs', prefs)
    # options.headless = True  # hide GUI
    options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
    options.add_argument("start-maximized")  # ensure window is full-screen

    # Set up a webdriver instance
    driver = webdriver.Chrome(options=options)
    return driver


test_driver = build_webdriver()


def select_election(year: str, election_type: str, driver: webdriver.Chrome = test_driver):

    download_path = Path(__file__).parents[1] / "data" / "earlyvote_days"
    download_path = download_path / year

    if "primary" in election_type.lower():
        download_path = download_path / "primary"

    if "republican" in election_type.lower():
        download_path = download_path / "rep"
    elif "democratic" in election_type.lower():
        download_path = download_path / "dem"
    else:
        pass

    # Navigate to the webpage
    driver.get(TEXAS_SOS_ELECTION_LIST_URL)
    sleep(1)

    # Locate the dropdown element
    election_type_dropdown = Select(driver.find_elements(By.CLASS_NAME, value="form-control")[0])
    submit_button = driver.find_elements(By.XPATH, value="//button[text()='Submit']")[0]

    # Iterate over the options and select the one that matches your criteria
    for option in election_type_dropdown.options:
        if year in option.text and election_type.upper() in option.text:
            election_type_dropdown.select_by_visible_text(option.text)
            break
    submit_button.click()

    return download_path


def export_early_vote_lists(folder_to_download_to, driver: webdriver.Chrome = test_driver):
    early_vote_date_dropdown = Select(driver.find_element(By.ID, value="selectedDate"))
    early_vote_dates = iter([x.text for x in early_vote_date_dropdown.options])

    previous_day_totals = None

    for ev_day in early_vote_dates:
        try:
            date_format = (datetime.strptime(ev_day, "%B %d,%Y").strftime("%Y%m%d"))
            _dropdown = Select(driver.find_element(By.ID, value="selectedDate"))
            _dropdown.select_by_visible_text(ev_day)
            _submit = driver.find_element(By.XPATH, value="//button[text()='Submit']")
            _submit.click()
            sleep(.5)
            _day_totals = driver.find_elements(
                By.XPATH,
                value='//*[@id="electionsInfoForm"]/div/div[2]/div/div[3]/div/table/tbody/tr[255]')[0]
            if _day_totals.text == previous_day_totals:
                _go_back = driver.find_element(By.XPATH, value="//button[text()='Previous']")
                _go_back.click()

            else:
                _generate_report_button = driver.find_element(By.XPATH, value="//button[text()='Generate Statewide Report']")
                _generate_report_button.click()
                sleep(5)

                # Get list of files
                files = list(DOWNLOAD_PATH.glob('*'))
                # Find downloaded file
                most_recent_file = max(files, key=lambda file: file.stat().st_mtime)
                sleep(.5)
                # Rename and move file
                shutil.move(most_recent_file, folder_to_download_to / f"{date_format}.csv")
                previous_day_totals = _day_totals.text
                _go_back = driver.find_element(By.XPATH, value="//button[text()='Previous']")
                _go_back.click()

        except ValueError:
            pass
        except StopIteration:
            driver.quit()

    print("Done!")


export_early_vote_lists(
    select_election("2024", "Republican Primary")
)

export_early_vote_lists(
    select_election("2024", "Democratic Primary")
)
