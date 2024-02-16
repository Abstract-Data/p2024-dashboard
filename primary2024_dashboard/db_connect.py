from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlite3

conn = sqlite3.connect('p2024_results.db')

Base = declarative_base()

engine = create_engine('sqlite:///p2024_results.db')
Session = sessionmaker(bind=engine)

