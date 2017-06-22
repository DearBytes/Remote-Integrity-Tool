#!/usr/bin/env python
# Copyright (C) 2017 DearBytes B.V. - All Rights Reserved
import os
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


DATABASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(DATABASE_PATH, '/data/integrity.db')

engine = create_engine('sqlite:///' + DATABASE_PATH)

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Model(object):

    def to_anonymous_object(self):
        """
        Convert the current model properties to an anonymous object
        This is to prevent the data from not being able to be accesses outside of the main thread it was created in
        :return: Object containing all keys and values that the current model does
        :rtype: object
        """
        return type('', (object,), self.to_dict())()

    def to_dict(self):
        """
        Convert the current model properties to a dict
        :return: Dict containing all keys and values that the current model does
        :rtype: dict
        """
        return dict(((key, getattr(self, key)) for key in self.__mapper__.columns.keys()))

    def values(self):
        """
        Get all values in the current row as a list
        :return: List containing all values that the current model does
        :rtype: list
        """
        return list(((getattr(self, key)) for key in self.keys()))

    @classmethod
    def keys(cls):
        """
        Get all keys in the current row as a list
        :return: List containing all keys that the current model does
        :rtype: list
        """
        return cls.__mapper__.columns.keys()

    def delete(self):
        """
        Delete the current row
        :return:
        """
        session.delete(self)

    def __iter__(self):
        values = vars(self)
        for attr in self.__mapper__.columns.keys():
            if attr in values:
                yield [attr, values[attr]]

    @classmethod
    def as_list(cls):
        """
        Get all results as a list
        :return: List
        """
        return list(cls)

    @classmethod
    def query(cls):
        """
        Get a new reference to query
        :return:
        """
        return session.query(cls)


class Server(Model, Base):
    __tablename__ = "servers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    @classmethod
    def get(cls, name):
        """
        Get the first instance of a server by name
        :param name: Name of the server
        :type name: str
        :return: Server if found, else None
        :rtype: models.Server
        """
        return session.query(cls).filter(cls.name == name).one_or_none()

    @classmethod
    def exists(cls, name):
        """
        Check if the server exists in the database
        :param name: Name of the server
        :return: Returns true if the server exists
        :rtype: bool
        """
        return cls.get(name=name) is not None

    @classmethod
    def create(cls, name):
        """
        Create a new
        :param name:
        :return: Instance of the server
        :rtype: models.Server
        """
        server = cls(name=name)
        session.add(server)
        return server

    def get_related_checksum(self, path, checksum):
        """
        Get a related checksum by certain criteria
        :param checksum: Checksum of the file
        :param path: Path to the file
        :type checksum: str
        :type path: str
        :return: Returns a checksum if one is found, otherwise None
        """
        for row in self.checksums:
            if row.path == path and row.checksum == checksum:
                return row


class Checksum(Model, Base):
    __tablename__ = "checksums"
    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    checksum = Column(String(128), nullable=False)

    server = relationship(Server, backref="checksums")
    server_id = Column(Integer, ForeignKey("servers.id"), index=True, nullable=False)

    @classmethod
    def create(cls, path, checksum, server):
        """
        Create a new record and return it
        :param path: Path to the file
        :param checksum: File checksum
        :param server: Related server ID
        :type path: str
        :type checksum: str
        :type server: models.Server
        :return: Returns the record that was just added
        """
        record = cls(path=path, checksum=checksum, server=server)
        session.add(record)
        return record


class Event(Model, Base):
    FILE_ADDED = 1
    FILE_REMOVED = 2
    FILE_MODIFIED = 3

    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    event = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    checksum = relationship(Checksum)
    checksum_id = Column(Integer, ForeignKey("checksums.id"), index=True, nullable=False)

    @classmethod
    def create(cls, event, description, checksum):
        """
        Create a new event and store it in the database
        :param event: What type of event was it (constant)
        :param description: Description of the event
        :param checksum: What checksum was it related to
        :type event: int
        :type description: str
        :type checksum: models.Checksum
        :return: Returns the instance of the event
        """
        record = cls(event=event, description=description, checksum=checksum, timestamp=datetime.now())
        session.add(record)
        return record


def create_database():
    """"
    Create a new database or overwrite the existing one
    :return: None
    """
    Base.metadata.create_all(engine)


def database_exists():
    """
    Check if the database exists
    :return: True if the database exists
    :rtype: bool
    """
    return os.path.exists(DATABASE_PATH)
