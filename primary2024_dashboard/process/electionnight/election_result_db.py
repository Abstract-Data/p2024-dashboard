from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import sqlite3


""" LOCAL SQL LITE DATABASE CONNECTION """
conn = sqlite3.connect(f'{Path(__file__).parent / "p2024_results.db"}')

engine = create_engine(f'sqlite:///{Path(__file__).parent / "p2024_results.db"}')

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
