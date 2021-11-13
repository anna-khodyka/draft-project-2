"""
Base class for Notebook entity and its realisations
for mongo and Postgres DataBases
"""

# pylint: disable=W0614
# pylint: disable=R0903
# pylint: disable=W0703
# pylint: disable=W0401
# pylint: disable=E0402
# pylint: disable=R0801

from datetime import datetime
from datetime import date
import re
import sys
import os
from abc import ABC, abstractmethod
from sqlalchemy import or_, update, delete


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
if __package__ == "" or __package__ is None:
    from SQL_alchemy_classes import *
else:
    from .SQL_alchemy_classes import *


class Notebook(ABC):
    """
    Base class fore Notebook entity
    """

    @abstractmethod
    def __init__(self):
        """
        Abstract method
        """

    @abstractmethod
    def get_all_notes(self, user_id):
        """
        Abstract method
        """

    @abstractmethod
    def get_notes(self, user_id, keyword):
        """
        Abstract method
        """

    @abstractmethod
    def get_note_by_id(self, note_id):
        """
        Abstract method
        """

    @abstractmethod
    def update_note(self, note_id, keywords, text):
        """
        Abstract method
        """

    @abstractmethod
    def insert_note(self, user_id, keywords, text):
        """
        Abstract method
        """

    @abstractmethod
    def delete_note(self, note_id):
        """
        Abstract method
        """



class NotebookPSQL(Notebook):
    """
    Class Notebook that operates with Postgres
    """

    def __init__(self, session=None):
        super().__init__()
        self.session = session
        self.notes = []

    def get_all_notes(self, user_id):
        """
        Find all the notes in DB
        :return: list of NotePSQL
        """
        self.notes = []
        result = (
            self.session.query(
                Note.note_id, Note.user_id, Note.text, Note.created_at
            ).filter(Note.user_id == user_id).order_by(Note.note_id).all()
        )
        for res in result:
            tags = self.session.query(
                Tag.tag
            ).join(TagsAndNotes).filter(TagsAndNotes.note_id == res.note_id).all()
            note = NotePSQL(res)
            note.tags = [tag_.tag for tag_ in tags]
            self.notes.append(note)
        return self.notes

    def get_notes(self, user_id, keyword):
        """
        Select from DB Notes find by keyword for fields text, keywords
        :param keyword: str
        :return: list of NotePSQL
        """
        self.notes = []
        if keyword != "":

            result = (
                self.session.query(
                    Note.note_id, Note.user_id, Note.text, Note.created_at
                ).outerjoin(TagsAndNotes).outerjoin(Tag).filter(Note.user_id == user_id,
                                                                or_(
                                                                    func.lower(Tag.tag).like(func.lower(f"%{keyword}%")),
                                                                    func.lower(Note.text).like(func.lower(f"%{keyword}%")),
                                                                )
                                                                ).distinct()
                    .order_by(Note.note_id)
                    .all()
            )
            for res in result:
                tags = self.session.query(
                    Tag.tag
                ).join(TagsAndNotes).filter(TagsAndNotes.note_id == res.note_id).all()
                note = NotePSQL(res)
                note.tags = [tag_.tag for tag_ in tags]
                self.notes.append(note)
            return self.notes
        return []

    def get_notes_by_tag(self, user_id, tag):
        """
        Select from DB Notes find by keyword for fields text, keywords
        :param keyword: str
        :return: list of NotePSQL
        """
        self.notes = []
        if tag:

            result = self.session.query(
                Note.note_id, Note.user_id, Note.text, Note.created_at
            ).outerjoin(TagsAndNotes).outerjoin(Tag
                                                ).filter(Note.user_id == user_id,
                                                         Tag.tag == tag
                                                         ).distinct().order_by(Note.note_id).all()

            for res in result:
                tags = self.session.query(
                    Tag.tag
                ).join(TagsAndNotes).filter(TagsAndNotes.note_id == res.note_id).all()
                note = NotePSQL(res)
                note.tags = [tag_.tag for tag_ in tags]
                self.notes.append(note)
            return self.notes
        return []

    def get_note_by_id(self, note_id):
        """
        Select from DB Note by given note_id
        :param note_id: int
        :return: NotePSQL
        """
        result = (
            self.session.query(
                Note.note_id, Note.user_id, Note.text, Note.created_at
            ).filter(Note.note_id == note_id).first()
        )
        if result:
            tags = self.session.query(
                Tag.tag, Tag.tag_id
            ).join(TagsAndNotes).filter(TagsAndNotes.note_id == result.note_id).all()
            note = NotePSQL(result)
            tag_lst = []
            for tag_ in tags:
                tag_lst.append(tag_)
            res = NotePSQL(result)
            res.tags = tags
            return res
        return None

    def get_all_tags(self, user_id):
        result = (
            self.session.query(
                Tag.tag, Tag.tag_id
            ).filter(Tag.user_id == user_id).all()
        )
        return result

    def create_tag(self, user_id, note_id, tag):
        if len(tag.strip())!=0:
            try:
                if self.session.query(Tag.tag).filter(Tag.tag==tag, Tag.user_id == user_id).first() is None:
                    print("TRY TO CREATE TAG - ENTER CLASS METHOD")
                    tag = Tag(tag=tag, user_id=user_id)
                    self.session.add(tag)
                    self.session.commit()
                    print("COMMIT")
                return 0
            except Exception as error:
                print(f"ERROR: {error}")
                return str(error)
        return 0

    def update_note(self, note_id, tags, text):
        """
        Update Note selected by note_id with new keywords and text
        :param note_id: int
        :param keywords: str
        :param text: str
        :return: 0 if OK or error otherwise
        """
        try:
            self.session.execute(
                update(Note, values={Note.text: text}).filter(
                    Note.note_id == note_id
                )
            )
            sql_stmt = delete(TagsAndNotes).where(TagsAndNotes.note_id == note_id)
            run_sql(self.session, sql_stmt)
            if tags:
                for tag in tags:
                    tag_and_note = TagsAndNotes(note_id=note_id, tag_id=int(tag))
                    self.session.add(tag_and_note)
            self.session.commit()
            return 0
        except Exception as error:
            self.session.rollback()
            return error

    def insert_note(self, user_id, tags, text):
        """
        Insert new Note to DB
        :param keywords: str
        :param text: str
        :return: 0 if OK or error otherwise
        """
        try:
            note = Note(user_id=user_id, created_at=date.today(), text=text)
            self.session.add(note)
            self.session.commit()
            for tag in tags:
                tag_and_note = TagsAndNotes(note_id=note.note_id, tag_id=int(tag))
                self.session.add(tag_and_note)
            self.session.commit()
            return 0
        except Exception as error:
            self.session.rollback()
            return error

    def delete_note(self, note_id):
        """
        Delete Note from DB by note_id
        :param note_id: int
        :return: 0 if OK or exception otherwise
        """
        sql_stmt = delete(Note).where(Note.note_id == note_id)
        return run_sql(self.session, sql_stmt)

class NoteAbstract(ABC):
    """
    Abstract Note class
    """

    @abstractmethod
    def __init__(self):
        self.note_id = None
        self.created_at = None
        self.text = None
        self.user_id = None


class NotePSQL(NoteAbstract):
    """
    Class Notes initialized from SQLAlchemy query
    """

    def __init__(self, note):
        super().__init__()
        self.note_id = note.note_id
        self.created_at = note.created_at
        self.text = note.text
        self.user_id = note.user_id
