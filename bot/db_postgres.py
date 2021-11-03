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

POSTGRES_DB = os.environ.get("BD_HOST", "localhost")
engine = create_engine(
    "postgresql+psycopg2://postgres:1234@" + POSTGRES_DB + "/contact_book", echo=True
)
DBSession = sessionmaker(bind=engine)
Base.metadata.bind = engine
pgsession = DBSession()
