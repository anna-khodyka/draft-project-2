"""
Testing the databases connections
"""

#pylint: disable=W0614
#pylint: disable=W0611
#pylint: disable=W0401
#pylint: disable=C0413

import sys
import unittest
import pytest
sys.path.append('../')
from db_mongo import *
from db_postgres import *


def test_connect_to_postgres():
    """
    Testing ability to connect with Postgres
    """
    assert pgsession is not None
    assert pgsession.query(User_.id).first() is not None
    assert pgsession.query(Contact.name).first is not None
    assert pgsession.query(Note.note_id).first() is not None
    assert pgsession.query(Address.city).first() is not None
    assert pgsession.query(Phone.phone).first() is not None
    assert pgsession.query(Text.text).first() is not None
    assert pgsession.query(Email.email).first() is not None

def test_connect_to_mongo():
    """
    Testing ability to connect with MongoDB
    """
    assert contact_db is not None
    assert counter_db is not None
    assert user_db is not None
    assert note_db is not None
    assert contact_db.find_one() is not None
    assert counter_db.find_one() is not None
    assert user_db.find_one() is not None
    assert note_db.find_one() is not None
