from models import *
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
import datetime
import random

engine = create_engine("sqlite:///db.sqlite", echo=True, future=True)
Base.metadata.create_all(engine)
session = Session(engine)

# Faculties
# prf = Faculty(abbreviation="PřF", name="Přírodovědecká fakulta")
# fzp = Faculty(abbreviation="FŽP", name="Fakulta životního prostředí")
#
# session.add(prf)
# session.add(fzp)
# session.commit()
#
# a = session.query(Faculty).all()
#
# for i in a:
#     print(i.name)

# # RoomTypes
# with open("old/data/data_RoomTypes.csv") as f:
#     for row in f.readlines():
#         if row:
#             name = row.strip().split(';')[1]
#             print(name)
#             session.add(RoomType(name=name))
#
# # Rooms
# with open("old/data/data_Rooms.csv") as f:
#     for row in f.readlines():
#         if row:
#             data = row.strip().split(';')
#             name = data[1]
#             floor = data[2]
#             roomtype = data[3]
#             faculty = data[4]
#             print(name)
#             session.add(Room(name=name, floor=floor, type_id=roomtype, faculty_id=faculty))
#
# session.commit()

# Workplaces
# with open("old/data/data_Workplaces.csv") as f:
#     for row in f.readlines():
#         if row:
#             data = row.strip().split(';')
#             abbreviation = data[1]
#             name = data[2]
#             faculty = data[3]
#
#             workplace = Workplace(abbreviation=abbreviation, name=name, faculty_id=faculty)
#             session.add(workplace)
#             session.commit()


# AuthorizedPersons
# with open("old/data/data_Borrowers_new.csv") as f:
#     for row in f.readlines():
#         if row:
#             data = row.strip().split(';')
#             firstname = data[1]
#             surname = data[2]
#             workplace_abbr = data[3]
#
#             workplace = session.query(Workplace).filter(Workplace.abbreviation == workplace_abbr).one()
#             authperson = AuthorizedPerson(firstname=firstname, surname=surname, workplace=workplace)
#
#             session.add(authperson)
#     session.commit()

# a = session.query(AuthorizedPerson).all()
# print([i.workplace_id for i in a])
# print(len(a))
# session.execute(delete(AuthorizedPerson).where(AuthorizedPerson.id > 300))
# a = session.query(AuthorizedPerson).all()
# print(len(a))
# session.add(AuthorizationOrigin(name="admin"))
# session.commit()

# Sample keys
# room1 = session.query(Room).filter(Room.id == 17).one()
# room2 = session.query(Room).filter(Room.id == 5).one()
# room3 = session.query(Room).filter(Room.id == 4).one()
# room4 = session.query(Room).filter(Room.id == 3).one()
# room5 = session.query(Room).filter(Room.id == 2).one()
# room6 = session.query(Room).filter(Room.id == 1).one()
# room7 = session.query(Room).filter(Room.id == 81).one()
# room8 = session.query(Room).filter(Room.id == 80).one()
# room9 = session.query(Room).filter(Room.id == 34).one()
# room10 = session.query(Room).filter(Room.id == 200).one()
# rooms = session.query(Room).all()
#
# registration_number = 252514291
# for room in rooms:
#     key = Key(
#         registration_number=registration_number,
#         key_class=0,
#         room=room
#     )
#     session.add(key)
#     print(key.registration_number)
#     registration_number += 1
#
# session.commit()
#
# key1 = Key(registration_number=25251429, key_class=0, rooms=[room1])
# session.add(key1)
# key2 = Key(registration_number=25252429, key_class=0, rooms=[room2])
# session.add(key2)
# key3 = Key(registration_number=25243429, key_class=0, rooms=[room3])
# session.add(key3)
# key4 = Key(registration_number=25254429, key_class=0, rooms=[room4])
# session.add(key4)
# key5 = Key(registration_number=25255429, key_class=0, rooms=[room5])
# session.add(key5)
# key6 = Key(registration_number=25256429, key_class=0, rooms=[room6])
# session.add(key6)
# key7 = Key(registration_number=25257429, key_class=0, rooms=[room7])
# session.add(key7)
# key8 = Key(registration_number=25258429, key_class=0, rooms=[room8])
# session.add(key8)
# key9 = Key(registration_number=25259429, key_class=0, rooms=[room9])
# session.add(key9)
# key10 = Key(registration_number=252510429, key_class=0, rooms=[room10])
# session.add(key10)
#
# session.commit()

# a = session.query(Key).all()
# print([i.registration_number for i in a])

# Sample authorizations
# authorization1 = Authorization(borrower_id=23, expiration=(datetime.datetime.utcnow() + datetime.timedelta(days=100)), rooms=[room1, room2])
# session.add(authorization1)
# authorization2 = Authorization(borrower_id=24, expiration=(datetime.datetime.utcnow() + datetime.timedelta(days=100)), rooms=[room2, room6])
# session.add(authorization2)
# authorization3 = Authorization(borrower_id=25, expiration=(datetime.datetime.utcnow() + datetime.timedelta(days=100)), rooms=[room1])
# session.add(authorization3)
# authorization4 = Authorization(borrower_id=39, expiration=(datetime.datetime.utcnow() + datetime.timedelta(days=100)), rooms=[room8])
# session.add(authorization4)
# session.commit()

# persons = session.query(AuthorizedPerson).all()
# rooms = session.query(Room).all()
# for person in persons:
#     for i in range(random.randint(1, 10)):
#         room = random.choice(rooms)
#         a = Authorization(person=person, room=room, expiration=(datetime.datetime.utcnow() + datetime.timedelta(days=100)), origin_id=1)
#         session.add(a)
#
# authorizations = session.query(Authorization).all()
# for i in authorizations:
#     print(i)
#
# session.commit()

# a = Authorization(person_id=10, room_id=10,  expiration=(datetime.datetime.utcnow() + datetime.timedelta(days=100)), origin_id=2)
# session.add(a)
# a = Authorization(person_id=10, room_id=10,  expiration=(datetime.datetime.utcnow() - datetime.timedelta(days=100)), origin_id=2)
# session.add(a)
# a = Authorization(person_id=10, room_id=10,  expiration=(datetime.datetime.utcnow() - datetime.timedelta(days=100)), origin_id=1)
# session.add(a)
# session.commit()

