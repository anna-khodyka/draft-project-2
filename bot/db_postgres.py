# pylint: disable=W0614
# pylint: disable=W0401
# pylint: disable=E0402

"""
Connection to Postgres
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
if __package__ == "" or __package__ is None:
    from SQL_alchemy_classes import *
else:
    from .SQL_alchemy_classes import *

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USERNAME = os.environ.get("DB_USERNAME", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "12345")
DATA_BASE = os.environ.get("DATA_BASE", "/contact_book")

engine = create_engine(
    "postgresql+psycopg2://"+DB_USERNAME+":"+DB_PASSWORD+"@"+DB_HOST + DATA_BASE, echo=True
)
DBSession = sessionmaker(bind=engine)
Base.metadata.bind = engine
pgsession = DBSession()
