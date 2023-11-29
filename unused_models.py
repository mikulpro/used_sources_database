import os
import datetime
from pathlib import Path
import importlib.util

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship


main_folder_path = Path(__file__).resolve().parent
project_folder_path = main_folder_path.parent

# db_interface
module_path = os.path.join(project_folder_path, 'sqlite', 'utils.py')
spec = importlib.util.spec_from_file_location('utils', module_path)
module_to_import = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module_to_import)
hash_func = module_to_import.hash_func


Base = declarative_base()


class Borrowing(Base):
    __tablename__ = "borrowings"

    id = Column(Integer, primary_key=True)
    key_id = Column(Integer, ForeignKey("keys.id"), nullable=False)
    key = relationship("Key", back_populates="borrowings")
    authorization_id = Column(Integer, ForeignKey("authorizations.id"), nullable=False)
    authorization = relationship("Authorization", back_populates="borrowings")
    borrowed = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    returned = Column(DateTime(timezone=True), nullable=True)

    def return_key(self):
        if self.returned is not None:
            raise Exception(f"Borrowing (id:{self.id}): Klíč byl již vrácen!")
        self.returned = datetime.datetime.utcnow()

    def __repr__(self):
        return f"Borrowing(id={self.id}, key_id={self.key_id}, authorization_id={self.authorization_id}, " \
               f"borrowed={self.borrowed}, returned={self.returned})"


class Key(Base):
    __tablename__ = "keys"

    id = Column(Integer, primary_key=True)
    registration_number = Column(Integer, nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    room = relationship("Room", back_populates="keys")
    key_class = Column(Integer, default=0)
    borrowings = relationship("Borrowing", back_populates="key")

    def is_borrowed(self):
        for borrowing in self.borrowings:
            if not borrowing.returned:
                return True
        return False

    def get_room_name(self):
        return self.room.name

    def __repr__(self):
        return f"Key(id={self.id}, registration_number={self.registration_number}, " \
               f"room_id={self.room_id}, key_class={self.key_class})"


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    name = Column(String(8), nullable=False, unique=True)
    floor = Column(Integer, nullable=False)
    type_id = Column(Integer, ForeignKey("room_types.id"))
    type = relationship("RoomType")
    faculty_id = Column(Integer, ForeignKey("faculties.id"))
    faculty = relationship("Faculty")
    authorizations = relationship("Authorization", back_populates="room")
    keys = relationship("Key", back_populates="room")
    borrowings_count = Column(Integer, nullable=False, default=0)

    def get_ordinary_key(self):
        for key in self.keys:
            if key.key_class == 0:
                return key

    def get_borrowable_key(self):
        for key in self.keys:
            if key.key_class == 0:
                if not key.is_borrowed():
                    return key

    def increment_borrowings_count(self):
        if not self.borrowings_count:
            self.borrowings_count = 0
        self.borrowings_count += 1

    def __repr__(self):
        return f"Room(id={self.id}, name={self.name}, floor={self.floor}, " \
               f"type_id={self.type_id}, faculty_id={self.faculty_id}, borrowings_count={self.borrowings_count})"


class RoomType(Base):
    __tablename__ = "room_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)

    def __repr__(self):
        return f"RoomType(id={self.id}, name={self.name})"


class Faculty(Base):
    __tablename__ = "faculties"

    id = Column(Integer, primary_key=True)
    abbreviation = Column(String(4), nullable=False, unique=True)
    name = Column(String(64), nullable=False, unique=True)

    def __repr__(self):
        return f"Faculty(id={self.id}, abbreviation={self.abbreviation}, name={self.name})"


class AuthorizedPerson(Base):
    __tablename__ = "authorized_persons"

    id = Column(Integer, primary_key=True)
    firstname = Column(String(64), nullable=False)
    surname = Column(String(64), nullable=False)
    workplace_id = Column(Integer, ForeignKey("workplaces.id"))
    workplace = relationship("Workplace")
    created = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    authorizations = relationship("Authorization", back_populates="person")
    #borrowings = relationship("Borrowing", secondary='authorizations', viewonly=True)

    def get_full_name(self):
        return self.firstname + " " + self.surname

    def __repr__(self):
        return f"AuthorizedPerson(id={self.id}, firstname={self.firstname}, surname={self.surname}, " \
               f"workplace_id={self.workplace_id}, created={self.created})"


class Workplace(Base):
    __tablename__ = "workplaces"

    id = Column(Integer, primary_key=True)
    abbreviation = Column(String(8), nullable=False, unique=True)
    name = Column(String(64), nullable=False, unique=True)
    faculty_id = Column(Integer, ForeignKey("faculties.id"))
    faculty = relationship("Faculty")

    def __repr__(self):
        return f"Workplace(id={self.id}, abbreviation={self.abbreviation}, name={self.name}, " \
               f"faculty_id={self.faculty_id})"


class Authorization(Base):
    __tablename__ = "authorizations"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("authorized_persons.id"))
    person = relationship("AuthorizedPerson")
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    room = relationship("Room", back_populates="authorizations")
    created = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    expiration = Column(DateTime(timezone=True), nullable=False)
    origin_id = Column(Integer, ForeignKey("authorization_origins.id"), nullable=False)
    origin = relationship("AuthorizationOrigin")
    borrowings = relationship("Borrowing", back_populates="authorization")


    def invalidate(self):
        self.expiration = datetime.datetime.utcnow()

    def is_valid(self):
        if self.expiration > datetime.datetime.utcnow():
            return True
        else:
            return False

    def __repr__(self):
        return f"Authorization(id={self.id}, person_id={self.person_id}, room_id={self.room_id}, " \
               f"created={self.created}, expiration={self.expiration}, origin_id={self.origin_id})"


class AuthorizationOrigin(Base):
    __tablename__ = "authorization_origins"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)

    def __repr__(self):
        return f"AuthorizationOrigin(id={self.id}, name={self.name})"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String)
    is_superuser = Column(Boolean, nullable=False, default=False)

    def check_password(self, password):
        if hash_func(password) == self.password:
            return True
        else:
            return False

    def __repr__(self):
        return f"User(username={self.username})"
