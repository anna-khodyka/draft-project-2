# pylint: disable=R0903
# pylint: disable=C0412
# pylint: disable=R0902
# pylint: disable=W0703
# pylint: disable=R0201
# pylint: disable=E0402
# pylint: disable=E0602
# pylint: disable=W0401

"""
Classes that provides interaction between views and database for
contact book entities. Includes Mongo and Postgres interface.
Redis based LRU cache used
"""

import re
import sys
import os
from datetime import date
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from sqlalchemy import or_, update, delete, any_, func

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

if __package__ == "" or __package__ is None:
    from SQL_alchemy_classes import (
        Address,
        Contact,
        Email,
        Phone,
        run_sql
    )
else:
    from .SQL_alchemy_classes import *


class Contactbook(ABC):
    """
    Abstract class for Contactbook
    """

    @abstractmethod
    def __init__(self):
        """
        Abstract method
        """

    @abstractmethod
    def get_all_contacts(self, user_id):
        """
        Abstract method
        """

    @abstractmethod
    def get_contacts(self, user_id, key):
        """
        Abstract method
        """

    @abstractmethod
    def get_contact_details(self, contact_id):
        """
        Abstract method
        """

    @abstractmethod
    def get_birthday(self, user_id, period):
        """
        Abstract method
        """

    @abstractmethod
    def update_contact(self, contact_id, contact):
        """
        Abstract method
        """

    @abstractmethod
    def insert_contact(self, user_id, contact):
        """
        Abstract method
        """

    @abstractmethod
    def delete_contact(self, contact_id):
        """
        Abstract method
        """


class ContactbookPSQL(Contactbook):
    """
    ContactBook - class conained in self.contacts Contact entities.
    Self.session stored connection to DB

    """

    def __init__(self, pg_session=None):
        """
        Init class instance with connection to PostgreSQL
        :param pg_session pgsession
        """
        super().__init__()
        self.contacts = []
        self.session = pg_session

    def get_all_contacts(self, user_id):
        """
        Get all the contacts from postgres DB
        :return: list(ContactPSQL) or error
        """
        self.contacts = []
        try:
            result = (
                self.session.query(Contact.contact_id,
                                   Contact.user_id,
                                   Contact.name,
                                   Contact.birthday
                ).filter(Contact.user_id == user_id)
                .order_by(Contact.contact_id)
                .all()
            )
            for res in result:
                self.contacts.append(ContactPSQL(res))
            return self.contacts
        except Exception as error:
            return str(error)

    def get_contacts(self, user_id, key):
        """
        Find contacts in postgres DB searching them by key in fields name and phone
        :param key: str
        :return: list(ContactsPSQL) or error
        """
        self.contacts = []
        try:
            if key != "":
                result = (
                    self.session.query(
                        Contact.contact_id,
                        Contact.user_id,
                        Contact.name,
                        Contact.birthday,
                    )
                    .outerjoin(Phone)
                    .filter(Contact.user_id == user_id,
                            or_(func.lower(Contact.name).like(func.lower(f"%{key}%")),
                                func.lower(Phone.phone).like(func.lower(f"%{key}%")),
                        )
                    )
                    .distinct()
                    .order_by(Contact.contact_id)
                    .all()
                )
                for res in result:
                    self.contacts.append(ContactPSQL(res))
                return self.contacts
            return []
        except Exception as error:
            return str(error)

    def get_contact_details(self, contact_id):
        """
        Select all contact data from joined tables in PostgreSQL DB. Data selected by contact_id.
        :param contact_id: int
        :return: ContactDetails
        """
        try:
            contact = self.session.query(
                Contact.contact_id, Contact.user_id, Contact.name, Contact.birthday
            ).filter(Contact.contact_id == contact_id).first()
            phone = self.session.query(Phone.phone).filter(Phone.contact_id == contact_id)
            email = self.session.query(Email.email).filter(Email.contact_id == contact_id).first()
            address = self.session.query(Address).filter(Address.contact_id == contact_id).first()
            return ContactDetails(contact, phone, email, address)
        except Exception as error:
            return str(error)


    def get_birthday(self, user_id, period):
        """
        Select all contacts from PostgreSQL database with birthday date in period
        :param period: int
        :return: list(ContactPSQL) or error
        """
        try:
            days = [
                (datetime.now() + timedelta(days=i)).strftime("%m-%d")
                for i in range(1, period + 1)
            ]
            res_list = []
            result = (
                self.session.query(Contact.contact_id, Contact.user_id, Contact.name, Contact.birthday)
                .filter(Contact.user_id == user_id, Contact.birthday != None,
                    func.substr(func.to_char(Contact.birthday, "YYYY-mm-dd"), 6, 10).like(
                        any_(days)
                    )
                )
                .all()
            )
            print([res.name for res in result])
            for res in result:
                res_list.append(res)
            res_list = sorted(res_list, key=self.distance)
            bd_list = []
            for res in res_list:
                contact = ContactPSQL(res)
                contact.celebrate = res.birthday.strftime("%d.%m")
                bd_list.append(contact)
            return bd_list
        except Exception as error:
            return str(error)

    @staticmethod
    def distance(contact):
        """
        Key function for sorting contact list by birthday celebration
        :param contact: ContactPSQL
        :return: distance.days: int
        """
        try:
            test_date = date(
                date.today().year, contact.birthday.month, contact.birthday.day
            )
        except ValueError:
            # for 29 february case
            test_date = date(date.today().year, contact.birthday.month + 1, 1)
        if test_date < date.today():
            try:
                test_date = date(
                    date.today().year + 1, contact.birthday.month, contact.birthday.day
                )
            except ValueError:
                # for 29 february case
                test_date = date(date.today().year + 1, contact.birthday.month + 1, 1)
        distance = test_date - date.today()
        return distance.days


    def update_contact(self, contact_id, contact):
        """
        Update the contact in PostgreSQL DB, selected by contact_id with data from contact param
        :param contact_id: int
        :param contact: ContactDict
        :return: 0 or error
        """
        try:
            self.session.execute(
                update(
                    Contact,
                    values={
                        Contact.name: contact.name,
                        Contact.birthday: contact.birthday,
                    },
                ).filter(Contact.contact_id == contact_id)
            )
            self.session.commit()
            stmt = delete(Phone).where(Phone.contact_id == contact_id)
            self.session.execute(stmt)
            self.session.commit()
            if contact.phone != ['']:
                for phone_num in [phone_.strip() for phone_ in contact.phone]:
                    phone = Phone(contact_id=contact_id, phone=phone_num)
                    self.session.add(phone)
                    self.session.commit()
            stmt = delete(Address).where(Address.contact_id == contact_id)
            self.session.execute(stmt)
            self.session.commit()
            addr_set = {contact.zip, contact.country, contact.region, contact.city, contact.street, contact.house,
                        contact.apartment}
            if addr_set != {''}:
                address = Address(
                    zip=contact.zip,
                    country=contact.country,
                    region=contact.region,
                    city=contact.city,
                    street=contact.street,
                    house=contact.house,
                    apartment=contact.apartment,
                    contact_id=contact_id,
                )
                self.session.add(address)
                self.session.commit()
            stmt = delete(Email).where(Email.contact_id == contact_id)
            self.session.execute(stmt)
            self.session.commit()
            if contact.email:
                email = Email(email=contact.email, contact_id=contact_id)
                self.session.add(email)
                self.session.commit()
            return 0
        except Exception as error:
            self.session.rollback()
            return error

    def insert_contact(self, user_id, contact):
        """
        Insert new contact to PostgreSQL
        :param contact: ContactDict
        :return: 0 or error
        """
        try:
            contact_ = Contact(
                name=contact.name,
                created_at=date.today(),
                birthday=contact.birthday if contact.birthday else None,
                user_id=user_id
            )
            self.session.add(contact_)
            self.session.commit()
            if contact.phone != ['']:
                for phone_num in [phone_.strip() for phone_ in contact.phone]:
                    phone = Phone(contact_id=contact_.contact_id, phone=phone_num)
                    self.session.add(phone)
                    self.session.commit()
            addr_set = set([contact.zip,
                            contact.country,
                            contact.region,
                            contact.city,
                            contact.street,
                            contact.house,
                            contact.apartment])
            if addr_set != {''}:
                address = Address(
                    zip=contact.zip,
                    country=contact.country,
                    region=contact.region,
                    city=contact.city,
                    street=contact.street,
                    house=contact.house,
                    apartment=contact.apartment,
                    contact_id=contact_.contact_id,
                )
                self.session.add(address)
                self.session.commit()
            if contact.email:
                email = Email(email=contact.email, contact_id=contact_.contact_id)
                self.session.add(email)
                self.session.commit()
        except Exception as error:
            self.session.rollback()
            return error
        return 0


    def delete_contact(self, contact_id):
        """
        Delete record from Contact table and cascade deleting all the records
        from Phone, Email, Address tables. Contact identified by contact_id.
        :param id: int
        :return: 0 or error
        """
        sql_stmt = delete(Contact).where(Contact.contact_id == contact_id)
        return run_sql(self.session, sql_stmt)

class ContactAbstract(ABC):
    """
    Abstract class for Contact Entities
    """

    @abstractmethod
    def __init__(self):
        pass


class ContactPSQL(ContactAbstract):
    """
    Contact class initialized using SQLAlchemy query object
    """

    def __init__(self, contact):
        super().__init__()
        self.contact_id = contact.contact_id
        self.user_id = contact.user_id
        self.name = contact.name
        self.birthday = contact.birthday.strftime("%d.%m.%Y") if contact.birthday else None
        self.celebrate = ""


class ContactDetails(ContactPSQL):
    """
    Contact details class initialized using SQLAlchemy query object
    """

    def __init__(self, contact, phones, email, address):
        super().__init__(contact)
        self.phone = []
        for phone in phones:
            self.phone.append(phone.phone)
        self.email = email.email if email else ""
        self.zip = address.zip if address else ""
        self.country = address.country if address else ""
        self.region = address.region if address else ""
        self.city = address.city if address else ""
        self.street = address.street if address else ""
        self.house = address.house if address else ""
        self.apartment = address.apartment if address else ""
        self.celebrate = ""


class ContactDict(ContactAbstract):
    """
    Contact class initialized using  dictionary
    """

    def __init__(self, form_dict):
        super().__init__()
        self.contact_id = None
        self.name = form_dict["Name"]["value"]
        self.birthday = form_dict["Birthday"]["value"]
        self.created_at = datetime.today()
        self.phone = [
            phone_.strip() for phone_ in form_dict["Phone"]["value"].split(",")
        ]
        self.email = form_dict["Email"]["value"]
        self.zip = form_dict["ZIP"]["value"]
        self.country = form_dict["Country"]["value"]
        self.region = form_dict["Region"]["value"]
        self.city = form_dict["City"]["value"]
        self.street = form_dict["Street"]["value"]
        self.house = form_dict["House"]["value"]
        self.apartment = form_dict["Apartment"]["value"]
