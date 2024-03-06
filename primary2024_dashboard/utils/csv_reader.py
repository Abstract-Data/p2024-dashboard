import csv
from pathlib import Path
from datetime import datetime
import os
from typing import Generator, Dict

# Set the start date for in-person voting for the cycle
in_person_start_date = datetime.strptime('2024-02-20', '%Y-%m-%d')


def file_include_date_modified(func):
    """
    Decorator to include the date modified for each row in the file.
    """
    def wrapper(*args, **kwargs):
        for row in func(*args, **kwargs):
            _date_modified = datetime.fromtimestamp(os.path.getmtime(args[0]))
            row['DATE_MODIFIED'] = datetime.fromtimestamp(os.path.getmtime(args[0])).strftime('%Y-%m-%d %H:%M:%S')
            yield row

    return wrapper


def file_include_date_added(func):
    """
    Decorator to include the date added for each row in the file.
    """
    def wrapper(*args, **kwargs):
        for row in func(*args, **kwargs):
            row['DATE_ADDED'] = datetime.fromtimestamp(os.path.getctime(args[0])).strftime('%Y-%m-%d %H:%M:%S')
            yield row

    return wrapper


def create_early_vote_date_count(data: list) -> list:
    """
    Function to create a list of unique dates from the data, sorted in ascending order.
    """
    date_list: list = [
        x for x in
        enumerate(
            sorted(
                list(
                    set(
                        data
                    )
                )
            ),
            start=1
        )
    ]
    return date_list


def folder_include_vote_date(func):
    """
    Decorator to include the vote date for each row in the file.
    """
    def wrapper(*args, **kwargs):
        data: list = [dict(x) for x in func(*args, **kwargs)]
        if data[0]['VOTE_DATE'].year == in_person_start_date.year:
            try:
                ev_dates = create_early_vote_date_count(
                    [
                        x['VOTE_DATE'] for x in data if
                        x['VOTING_METHOD'] == 'IN-PERSON'
                        and x['VOTE_DATE'] >= in_person_start_date
                    ]
                )
            except KeyError:
                raise KeyError(f"VOTE_METHOD not found in {data[0]['VOTE_DATE']} file.")
        else:
            ev_dates = create_early_vote_date_count(
                [
                    x['VOTE_DATE'] for x in data if x['VOTING_METHOD'] == 'IN-PERSON'
                ]
            )

        for row in data:
            if row['VOTING_METHOD'] == 'IN-PERSON':
                matching_dates = [
                    x[0] for x in ev_dates if x[1] == row['VOTE_DATE']
                ]  # Get the day number for the in-person vote
                if matching_dates:
                    row['DAY_IN_EV'] = int(matching_dates[0])  # Set the day they voted in person
                else:
                    row['DAY_IN_EV'] = 1
            else:
                row['DAY_IN_EV'] = 0  # Set the day they voted as 0 if not 'IN-PERSON' (Mail-in voters)
            yield row

    return wrapper


def file_include_vote_date(func):
    """
    Decorator to format the vote date for each row in the file to a datetime object.
    """
    def wrapper(*args, **kwargs):
        for row in func(*args, **kwargs):
            row['VOTE_DATE'] = datetime.strptime(args[0].stem, '%Y%m%d')
            row['YEAR'] = row['VOTE_DATE'].year
            yield row

    return wrapper


@file_include_date_added
@file_include_date_modified
@file_include_vote_date
def read_csv_file(file: Path) -> Generator[Dict, None, None]:
    """
    Function to read a CSV file and yield each row as a dictionary.
    """
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


@folder_include_vote_date
def read_files_in_directory(directory: Path, primary_party: str = None) -> list:
    """
    Function to read all CSV files in a directory and yield each row as a dictionary.
    """
    files = directory.glob("*.csv")
    for file in files:
        records = read_csv_file(file)
        for record in records:
            if primary_party:
                record['PRIMARY_VOTED_IN'] = primary_party
                yield record
            else:
                yield record
