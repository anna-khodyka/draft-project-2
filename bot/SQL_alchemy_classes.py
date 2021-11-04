"""
Define SQLAlchemy ORM classes for Contact-book and Notebook entities
"""

# pylint: disable=R0903
# pylint: disable=C0103
# pylint: disable=W0703

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    func,
    UniqueConstraint,
    Date,
    LargeBinary,
    BIGINT,
    Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Contact(Base):
    """
    Table Contact stored base data for contact.
    Other data stored in joined tables Email, Phones_, Address

    """

    __tablename__ = "contact"
    contact_id = Column(
        Integer,
        primary_key=True,
    )
    name = Column(String(50), nullable=False)
    created_at = Column(Date, server_default=func.now(), nullable=False)
    birthday = Column(Date, nullable=True)
    user_id = Column(
        Integer,
        ForeignKey("user_.id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    __table_args__ = (UniqueConstraint("name", "birthday", name="uc_1"),)


class Phone(Base):
    """
    Table Phone stored phones for contacts in table Contact
    """

    __tablename__ = "phone"
    phone_id = Column(
        Integer,
        primary_key=True,
    )
    phone = Column(String(15), nullable=True)
    contact_id = Column(
        Integer,
        ForeignKey("contact.contact_id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    contact = relationship("Contact")
    __table_args__ = (UniqueConstraint("phone", name="up_1"),)


class Email(Base):
    """
    Table Email stored email addresses for contacts in table Contact
    """

    __tablename__ = "email"
    email_id = Column(
        Integer,
        primary_key=True,
    )
    email = Column(String(50), nullable=True)
    contact_id = Column(
        Integer,
        ForeignKey("contact.contact_id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    contact = relationship("Contact")
    __table_args__ = (UniqueConstraint("email", name="ue_1"),)


class Address(Base):
    """
    Table Address stored addresses for contacts in table Contact
    """

    __tablename__ = "address"
    address_id = Column(
        Integer,
        primary_key=True,
    )
    zip = Column(String(10), default="")
    country = Column(String(50), default="")
    region = Column(String(50), default="")
    city = Column(String(40), default="")
    street = Column(String(50), default="")
    house = Column(String(5), default="")
    apartment = Column(String(5), default="")
    contact_id = Column(
        Integer,
        ForeignKey("contact.contact_id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    contact = relationship("Contact")


class Note(Base):
    """
    Table Note
    """

    __tablename__ = "note"
    note_id = Column(
        Integer,
        primary_key=True,
    )
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    text = Column(Text())
    user_id = Column(
        Integer,
        ForeignKey("user_.id", onupdate="CASCADE", ondelete="CASCADE"),
    )


class Tag(Base):
    __tablename__ = "tag"

    tag_id = Column(
        Integer,
        primary_key=True,
    )
    tag = Column(String(20))
    user_id = Column(
        Integer,
        ForeignKey("user_.id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    note = relationship("TagsAndNotes")

class TagsAndNotes(Base):
    __tablename__ = 'tags_and_notes'
    tag_id = Column(ForeignKey('tag.tag_id'), primary_key=True)
    note_id = Column(ForeignKey('note.note_id'), primary_key=True)
    note = relationship("Note")




class User_(Base):
    """
    Table for Flask user
    """

    __tablename__ = "user_"
    id = Column(
        Integer,
        primary_key=True,
    )
    username = Column(String(50))
    login = Column(String(50))
    password = Column(String(150))
    __table_args__ = (UniqueConstraint("login", name="ul_1"),)


class File(Base):
    __tablename__ = "file"

    file_id = Column(
        Integer,
        primary_key=True,
    )
    user_id = Column(Integer, ForeignKey("user_.id", onupdate="CASCADE", ondelete="CASCADE"))
    name = Column(String(50))
    file_date = Column(Date, nullable=False)
    file_length = Column(BIGINT, nullable=False)
    file_type = Column(String(20), nullable=False)
    file = Column(LargeBinary, nullable=False)
    __table_args__ = (UniqueConstraint("name", "user_id", name="uf_1"),)


def run_sql(session, sql_stmt):
    """
    Do wide shared in classes SQL session routine
    :param session: pgdb session
    :param sql_stmt: str
    :return: o or error
    """
    try:
        session.execute(sql_stmt)
        session.commit()
        return 0
    except Exception as error:
        session.rollback()
        return error
