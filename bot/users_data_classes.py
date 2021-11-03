"""
Class responsible for interaction between flask app and database concerning User_ entity
"""

# pylint: disable=W0614
# pylint: disable=R0903
# pylint: disable=W0703
# pylint: disable=W0401
# pylint: disable=E0402
# pylint: disable=R0801

import sys
import os
from abc import ABC, abstractmethod
from sqlalchemy import delete


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
if __package__ == "" or __package__ is None:
    from SQL_alchemy_classes import *
else:
    from .SQL_alchemy_classes import *


class ApplicationUser(ABC):
    """
    Abstract Flask App User
    """

    @abstractmethod
    def __init__(self):
        """
        Abstract method
        """

    @abstractmethod
    def get_user(self, user_login):
        """
        Abstract method
        """

    @abstractmethod
    def insert_user(self, name, user_login, password):
        """
        Abstract method
        """

    @abstractmethod
    def delete_user(self, user_login):
        """
        Abstract method
        """


class AppUserMongo(ApplicationUser):
    """
    Class App User with mongo DB connection
    """

    def __init__(self, user_db):
        """
        Init class instance
        :param user_db: mongo collection
        """
        super().__init__()
        self.user_db = user_db

    def get_user(self, user_login):
        """
        Select User from mongo collection by login
        :param user_login: str
        :return: UserMongo
        """
        res = self.user_db.find_one({"login": user_login})
        if res is not None:
            user = UserMongo(res)
            return user
        return res

    def insert_user(self, name, user_login, password):
        """
        Insert new User to mongo collection
        :param name: str
        :param user_login: str
        :param password: hashed with secret key str
        :return: str
        """

        try:
            res = self.get_user(user_login)
            if res == [] or res is None:
                self.user_db.insert_one(
                    {"user_name": name, "login": user_login, "password": password}
                )
                return None
            return f"User with login [{user_login}] already exist"
        except Exception as error:
            return f"Some problem: {str(error)}"

    def delete_user(self, user_login):
        """
        Delete User from mongo collection
        :param user_login: str
        :return: 0 or error
        """
        try:
            self.user_db.delete_one({"login": user_login})
            return 0
        except Exception as error:
            return error


class AppUserPSQL(ApplicationUser):
    """
    App User with postgres connection
    """

    def __init__(self, session=None):
        """
        Init User instance
        :param session: pgdbsession
        """
        super().__init__()
        self.session = session

    def get_user(self, user_login):
        """
        Select User from table User_ by given login
        :param login: str
        :return: UserPSQL
        """
        res = (
            self.session.query(User_.id, User_.username, User_.login, User_.password)
            .filter(User_.login == user_login)
            .first()
        )
        if res is None:
            return res
        return UserPSQL(res)

    def insert_user(self, name, user_login, password):
        """
        Insert new User to User_ table
        :param name: str
        :param user_login: str
        :param password: str hashed with secret key
        :return: str
        """
        res = self.get_user(user_login)
        if res is None:
            try:
                user = User_(
                    username=name,
                    login=user_login,
                    password=password,
                )
                self.session.add(user)
                self.session.commit()
                return None
            except Exception as error:
                return f"Could not append user list due to the problem: {str(error)}"
            finally:
                self.session.rollback()
        else:
            return f"User with login [{user_login}] already exist"

    def delete_user(self, user_login):
        """
        Delete User from User_ by login
        :param user_login:
        :return:
        """
        stmt = delete(User_).where(User_.login == user_login)
        return run_sql(self.session, stmt)


class UserAbstract(ABC):
    """
    Abstract class for User
    """

    @abstractmethod
    def __init__(self):
        pass


class UserMongo(UserAbstract):
    """
    User initialized with mongo cursor
    """

    def __init__(self, json):
        """
        User initialization
        :param json:
        """
        super().__init__()
        self.user_id = json["_id"]
        self.user_name = json["user_name"]
        self.login = json["login"]
        self.password = json["password"]


class UserPSQL(UserAbstract):
    """
    User initialized with SQLAlchemy query obj
    """

    def __init__(self, query_obj):
        """
        User initialization
        :param result:
        """
        super().__init__()
        self.user_id = query_obj.id
        self.user_name = query_obj.username
        self.login = query_obj.login
        self.password = query_obj.password
