from typing import Generator
import csv
from pathlib import Path
import itertools
from datetime import datetime

in_person_start_date = datetime.strptime('2024-02-20', '%Y-%m-%d')
def folder_early_vote_date(func):
    def wrapper(*args, **kwargs):
        data: list = [dict(x) for x in func(*args, **kwargs)]
        ev_dates: list = [
            x for x in
            enumerate(
                sorted(
                    list(
                        set(
                            [
                                x['VOTE_DATE'] for x in data if x['VOTING_METHOD'] == 'IN-PERSON'
                            ]
                        )
                    )
                ),
                start=1
            )
        ]
        for row in data:
            if row['VOTING_METHOD'] == 'IN-PERSON':
                matching_dates = [x[0] for x in ev_dates if x[1] == row['VOTE_DATE']]
                if matching_dates:
                    row['DAY_IN_EV'] = int(matching_dates[0])
                    if row['VOTE_DATE'] < in_person_start_date:
                        row['DAY_IN_EV'] = 1
            else:
                row['DAY_IN_EV'] = 0
            yield row
    return wrapper


def file_early_vote_date(func):
    def wrapper(*args, **kwargs):
        for row in func(*args, **kwargs):
            row['VOTE_DATE'] = datetime.strptime(args[0].stem, '%Y%m%d')
            yield row
    return wrapper


@file_early_vote_date
def read_csv_file(file: Path):
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


@folder_early_vote_date
def read_files_in_directory(directory: Path) -> list:
    files = directory.glob("*.csv")
    for file in files:
        records = read_csv_file(file)
        for record in records:
            yield record


