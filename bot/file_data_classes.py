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


extensions_ = {
    'images' :  ('JPEG', 'PNG', 'JPG', 'SVG', 'TIFF', 'GIF', 'PSD', 'CDR'),
    'video' :  ('AVI', 'MP4', 'MOV', 'MKV'),
    'documents' :  ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX', 'PDF', 'XLS', 'DOCX', 'CSV'),
    'music': ('MP3', 'OGG', 'WAV', 'AMR'),
    'archives':  ('ZIP', 'GZ', 'TAR'),
    'python': ('PY', ),
    'executable': ('EXE', 'MSI', 'DLL'),
    'WEB': ("CSS", "HTML", "JSON","JS"),
    'data': ("PKL",)    }


class FileFolder(ABC):
    """
    Base class fore File folder entity
    """

    @abstractmethod
    def __init__(self):
        """
        Abstract method
        """

    @abstractmethod
    def get_all_file_names(self, user_id):
        """
        Abstract method
        """

    @abstractmethod
    def get_files(self, user_id, keyword):
        """
        Abstract method
        """

    @abstractmethod
    def get_file_by_id(self, file_id):
        """
        Abstract method
        """

    @abstractmethod
    def update_file(self, file_id, file):
        """
        Abstract method
        """

    @abstractmethod
    def insert_file(self, user_id, file):
        """
        Abstract method
        """

    @abstractmethod
    def delete_file(self, file_id):
        """
        Abstract method
        """

class FileFolderPSQL(FileFolder):


    def __init__(self, pgsession):
        self.session = pgsession

    def get_all_file_names(self, user_id, file_type):
        self.files = []
        result = (
            self.session.query(
                File.file_id, File.file_type, File.name, File.user_id, File.file_date, File.file_length
            ).filter(File.user_id == user_id).order_by(File.file_type, File.name)
        )
        if file_type:
            result = result.filter(File.file_type == file_type)
        for res in result.all():
            self.files.append(FilePSQL(res))
        return self.files


    def get_files(self, user_id, keyword):
        self.files = []
        result = (
            self.session.query(
                File.file_id, File.file_type, File.name, File.user_id, File.file_date, File.file_length
            ).filter(File.user_id == user_id, func.lower(File.name).like(func.lower(f"%{keyword}%")))
                     .order_by(File.file_type, File.name).all()
        )
        for res in result:
            self.files.append(FilePSQL(res))
        return self.files

    def number_of_files(self, user_id):
        result = (
            self.session.query(File.user_id).filter(File.user_id == user_id).count()
        )
        return result

    def get_types(self, user_id):
        result = (
            self.session.query(File.file_type).filter(File.user_id == user_id).distinct(File.file_type).all()
        )
        return [res.file_type for res in result]

    def get_file_by_id(self, file_id):
        result = (
            self.session.query(
                File.file_id, File.file_type, File.name, File.user_id, File.file_date, File.file_length, File.file
            ).filter(File.file_id == file_id).first()
        )
        if result:
            file = FilePSQL(result)
            file.file = result.file
            return file
        return None


    def update_file(self, file_id, file):
        try:
            length = len(file)
            self.session.execute(
                update(File, values={File.file: file}).filter(
                    File.file_id == file_id
                )
            )
            self.session.commit()
            return 0
        except Exception as error:
            self.session.rollback()
            return error


    def insert_file(self, user_id, file, max_size, total_file, used_file):
        try:
            file_type = 'Other'
            content=file.read()
            size = len(content)
            size_mb = round(size/1024/1024,2)
            if size_mb > max_size:
                raise ValueError(f'File size exceed the limit: {size_mb} vs {max_size} ')
            if used_file > total_file:
                raise ValueError(f'User exceed the limit on number of files: {used_file} vs {total_file} ')
            ext = file.filename.rsplit('.', 1)[1].lower()
            for key in extensions_.keys():
                if ext.upper() in extensions_[key]:
                    file_type = key.capitalize()
            file = File(
                user_id=user_id,
                name=file.filename,
                file_date=datetime.now(),
                file_length=size,
                file_type=file_type,
                file=content
            )
            self.session.add(file)
            self.session.commit()
            return 0
        except Exception as error:
            self.session.rollback()
            return error


    def delete_file(self, file_id):
        sql_stmt = delete(File).where(File.file_id == file_id)
        return run_sql(self.session, sql_stmt)


class FilePSQL():

    def __init__(self, query_object):
        self.file_id = query_object.file_id
        self.user_id = query_object.user_id
        self.name = query_object.name
        self.file_date = query_object.file_date
        self.file_length = round(query_object.file_length/1024/1024, 2)
        self.file_type = query_object.file_type
