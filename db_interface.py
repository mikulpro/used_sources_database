import os
from pathlib import Path
import importlib.util
from sqlalchemy import String, create_engine, or_, and_, update, func, select
from sqlalchemy.orm import Session
import sqlalchemy.exc
import datetime
import models

Borrowing = module_to_import.Borrowing
Key = module_to_import.Key
Room = module_to_import.Room
RoomType = module_to_import.RoomType
Faculty = module_to_import.Faculty
AuthorizedPerson = module_to_import.AuthorizedPerson
Workplace = module_to_import.Workplace
Authorization = module_to_import.Authorization
AuthorizationOrigin = module_to_import.AuthorizationOrigin
User = module_to_import.User

# db utils hash_func
module_path = os.path.join(project_folder_path, 'sqlite', 'utils.py')
spec = importlib.util.spec_from_file_location('utils', module_path)
module_to_import = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module_to_import)
hash_func = module_to_import.hash_func


"""
Db:
    ROOMS
        get_all_floors(self) -> list[int]
        get_all_rooms(self) -> list[Room]
        get_rooms_by_floor(self, floor: int) -> list[Room]
        get_available_rooms_by_floor(self, floor: int, only_ordinary=True: bool) -> list[Room]
        get_rooms_availability_dict_by_floor(self, floor: int, only_ordinary_keys=True: bool) -> dict[str, List[Room]]
        search_rooms(self, expression: str, floor=None: int) -> list[Room]
        search_rooms_availability_dict_by_floor(self, expression: str, floor: int, only_ordinary_keys=True: bool) -> dict[str, List[Room]]
    
    KEYS
        get_all_keys(self) -> list[Key]
        get_borrowable_keys_by_floor(self, floor: int, only_ordinary=True: bool) -> list[Key]
    
    AUTHORIZATIONS
        get_all_authorizations(self) -> list[Authorization]
        get_valid_authorizations_for_room(self, room_id: int)-> list[Authorization]
        get_prioritized_authorizations_for_room(self, room_id: int) -> list[Authorization]
        search_authorizations(self, expression: str) -> list[Authorization]
        search_prioritized_authorizations_for_room(self, expression: str, room_id: int) -> list[Authorization]

        add_authorization(person_id: int, room_id: int, expiration: datetime, origin_id=1 : int) -> None
        invalidate_authorization(authorization_id: int) -> None
        invalidate_authorization_obj(authorization: Authorization) -> None
    
    BORROWINGS
        add_borrowing(self, int: key_id, int: borrower_id) -> None
        return_key(self, int: borrowing_id) -> None
        get_ongoing_borrowings(self) -> list[Borrowing]
    
    EXCEL GENERATING
        excel_dump(self) -> list[list[str]]
        # přidat časově omezený exel dump
    
    LOGIN SYSTEM
        get_user_by_username(username: str) -> User?
        add_user(username: str, password: str, is_superuser=False: bool) -> None
    
    AUTHORIZED PERSONS
        get_all_authorized_persons(self) -> list[AuthorizedPerson]
        search_authorized_persons(self, expression: str) -> list[AuthorizedPerson]
        
        add_person(self, firstname: str, surname: str, workplace_id=None: int) -> None
        update_person(self, person_id : int, **kwargs) -> None (firstname : str, surname: str, workplace_id : int) -> None
    
    
    ADMIN    
        ?update_authorization(...)
        ?add_key(...)
        ?update_key(..)
        ?add_room(...)
        ?update_room(...)
        
    SCREENS
        get_all_authorizations_screen(self)
"""


class Db:

    def __init__(self, db_path="sqlite:///db.sqlite"):
        self.db_path: String = db_path
        self.session: Session = None
        self.new_session()

    def new_session(self):
        engine = create_engine(self.db_path, future=True)
        self.session = Session(engine)

    def commit_session(self):
        self.session.commit()

    # ALL PURPOSE
    def get_all_floors(self):
        result = self.session.query(Room.floor).distinct(Room.floor).order_by(Room.floor).all()
        return [i[0] for i in result]

    def get_all_rooms(self):
        return self.session.query(Room).all()

    def get_rooms_by_floor(self, floor):
        rooms = self.session.query(Room).filter(Room.floor == floor).order_by(Room.borrowings_count.desc()).all()
        return rooms

    def get_all_keys(self):
        return self.session.query(Key).all()

    def get_borrowable_keys_by_floor(self, floor, only_ordinary =True):
        q = self.session.query(Key).\
            except_(self.session.query(Key).join(Borrowing).filter(Borrowing.returned == None)).\
            join(Room).filter(Room.floor == floor).\
            order_by(Room.borrowings_count.desc())
        if only_ordinary:
            q = q.filter(Key.key_class == 0)
        keys = q.all()
        return keys

    def get_available_rooms_by_floor(self, floor, only_ordinary=True):
        q_unavailable_rooms = self.session.query(Room).join(Key).join(Borrowing).filter(Borrowing.returned == None)
        q = self.session.query(Room).\
            filter(Room.floor==floor). \
            except_(q_unavailable_rooms).join(Key).\
            order_by(Room.borrowings_count.desc())
        if only_ordinary:
            q = q.filter(Key.key_class == 0)
        rooms = q.all()
        return rooms


    def get_rooms_availability_dict_by_floor(self, floor, only_ordinary_keys=True):
        q_unavailable_rooms = self.session.query(Room).join(Key).join(Borrowing). \
            filter(Borrowing.returned == None, Room.floor == floor)
        if only_ordinary_keys:
            q_unavailable_rooms = q_unavailable_rooms.filter(Key.key_class == 0)
        q_available_rooms = self.session.query(Room). \
            filter(Room.floor == floor). \
            except_(q_unavailable_rooms).join(Key). \
            order_by(Room.borrowings_count.desc())
        if only_ordinary_keys:
            q_available_rooms = q_available_rooms.filter(Key.key_class == 0)

        available_rooms = q_available_rooms.all()
        unavailable_rooms = q_unavailable_rooms.order_by(Room.borrowings_count.desc()).all()
        return {"available": available_rooms, "unavailable": unavailable_rooms}

    def search_rooms_availability_dict_by_floor(self, expression, floor, only_ordinary_keys=True):
        q_unavailable_rooms = self.session.query(Room).join(Key).join(Borrowing). \
            filter(Borrowing.returned == None, Room.floor == floor, Room.name.like(f"%{expression}%"))
        if only_ordinary_keys:
            q_unavailable_rooms = q_unavailable_rooms.filter(Key.key_class == 0)
        q_available_rooms = self.session.query(Room). \
            filter(Room.floor == floor, Room.name.like(f"%{expression}%")). \
            except_(q_unavailable_rooms).join(Key). \
            order_by(Room.borrowings_count.desc())
        if only_ordinary_keys:
            q_available_rooms = q_available_rooms.filter(Key.key_class == 0)

        available_rooms = q_available_rooms.all()
        unavailable_rooms = q_unavailable_rooms.order_by(Room.borrowings_count.desc()).all()
        return {"available": available_rooms, "unavailable": unavailable_rooms}

    def get_valid_authorizations_for_room(self, room_id):
        authorizations = self.session.query(Authorization).join(Authorization.room).filter(
            Room.id == room_id, Authorization.expiration > datetime.datetime.utcnow()
        ).all()
        return sorted(authorizations, key=lambda authorization: len(authorization.borrowings))

    def get_prioritized_authorizations_for_room(self, room_id):
        q = self.session.query(Authorization, func.rank().over(
        order_by=(func.count(Borrowing.id).desc(), Authorization.origin_id.desc(), Authorization.expiration.desc()))). \
            join(Authorization.room, Authorization.person). \
            filter(Room.id == room_id, Authorization.expiration > datetime.datetime.utcnow()). \
            join(Authorization.borrowings, isouter=True).\
            group_by(AuthorizedPerson.id)
        """
            RAW QUERY:
            SELECT *, RANK() OVER (ORDER BY COUNT(b.id) DESC, a.origin_id DESC, a.expiration DESC)
            FROM authorizations a 
            INNER JOIN authorized_persons ap ON a.person_id == ap.id
            LEFT JOIN borrowings b ON a.id == b.authorization_id 
            WHERE DATE('now') < a.expiration AND a.room_id == 10
            GROUP BY ap.id 
        """
        prioritized_authorizations = [i[0] for i in q.all()]
        return prioritized_authorizations

    def search_prioritized_authorizations_for_room(self, expression, room_id):
        q = self.session.query(Authorization, func.rank().over(
        order_by=(func.count(Borrowing.id).desc(), Authorization.origin_id.desc(), Authorization.expiration.desc()))). \
            join(Authorization.room, Authorization.person). \
            filter(Room.id == room_id, Authorization.expiration > datetime.datetime.utcnow()). \
            join(Authorization.borrowings, isouter=True).\
            group_by(AuthorizedPerson.id)

        # SEARCHING
        words = expression.split(' ')
        if len(words) == 1:
            q = q.filter(
            or_(AuthorizedPerson.firstname.like(f"{words[0]}%"),
                AuthorizedPerson.surname.like(f"{words[0]}%")
                ))

        elif len(words) == 2:
            q = q.filter(
                or_(
                    and_(AuthorizedPerson.firstname.like(f"{words[0]}%"),
                         AuthorizedPerson.surname.like(f"{words[1]}%"),
                         ),
                    and_(AuthorizedPerson.firstname.like(f"{words[1]}%"),
                         AuthorizedPerson.surname.like(f"{words[0]}%"),
                         ),
                ))

        prioritized_authorizations = [i[0] for i in q.all()]
        return prioritized_authorizations



    # KEY BORROWING
    def add_borrowing(self, key_id, authorization_id):
        borrowing = Borrowing(key_id=key_id, authorization_id=authorization_id)
        self.session.add(borrowing)
        authorization = self.session.query(Authorization).filter(Authorization.id == authorization_id).one()
        authorization.room.increment_borrowings_count()
        self.session.commit()

    def return_key(self, borrowing_id):
        borrowing = self.session.query(Borrowing).filter(Borrowing.id == borrowing_id).one()
        borrowing.return_key()
        self.session.commit()

    def get_ongoing_borrowings(self):
        return self.session.query(Borrowing).filter(Borrowing.returned.is_(None)).order_by(Borrowing.borrowed).all()

    # EXCEL GENERATING
    def excel_dump(self):
        # [borrowed: date, time, key, borrower name, return: date, time]
        data = []
        borrowings = self.session.query(Borrowing).all()
        for borrowing in borrowings:
            row = [
                borrowing.borrowed.strftime("%d.%m.%Y"),
                borrowing.borrowed.strftime("%H:%M"),
                str(borrowing.key.registration_number),
                borrowing.authorization.person.get_full_name(),
            ]
            if borrowing.returned:
                row.extend([
                    borrowing.returned.strftime("%d.%m.%Y"),
                    borrowing.returned.strftime("%H:%M"),
                ])
            else:
                row.extend([
                    "",
                    ""
                ])

            data.append(row)

        return data

    # LOGIN SYSTEM
    def add_user(self, username, password, is_superuser=False):
        password_hash = hash_func(password)
        user = User(username=username, password=password_hash, is_superuser=is_superuser)
        try:
            self.session.add(user)
            self.session.commit()
        except sqlalchemy.exc.IntegrityError:
            raise Exception("Uživatel s tímto uživatelským jménem již existuje!")

    def get_user_by_username(self, username):
        user = self.session.query(User).filter(User.username == username).one_or_none()
        return user

    # ADMIN
    def add_authorization(self, person_id, room_id, expiration, origin_id=1):
        authorization = Authorization(
            person_id=person_id,
            room_id=room_id,
            expiration=expiration,
            origin_id=origin_id
        )
        self.session.add(authorization)
        self.session.commit()

    def invalidate_authorization(self, authorization_id):
        authorization = self.session.query(Authorization).filter(Authorization.id == authorization_id).one()
        authorization.invalidate()
        self.session.commit()

    def invalidate_authorization_obj(self, authorization):
        authorization.invalidate()
        self.session.commit()

    def add_person(self, firstname, surname, workplace_id=None):
        person = AuthorizedPerson(
            firstname=firstname,
            surname=surname,
            workplace_id=workplace_id
        )
        self.session.add(person)
        self.session.commit()

    def update_person(self, person_id, **kwargs):
        self.session.execute(
            update(AuthorizedPerson)
            .where(AuthorizedPerson.id == person_id)
            .values(kwargs)
        )
        self.session.commit()

    def search_authorizations(self, expression):
        words = expression.split(" ")

        if len(words) == 1:
            result_q = self.session.query(Authorization).join(AuthorizedPerson).filter(
                or_(AuthorizedPerson.firstname.like(f"{words[0]}%"),
                    AuthorizedPerson.surname.like(f"{words[0]}%")
                    ))
        elif len(words) == 2:
            result_q = self.session.query(Authorization).join(AuthorizedPerson).filter(
                or_(
                    and_(AuthorizedPerson.firstname.like(f"{words[0]}%"),
                         AuthorizedPerson.surname.like(f"{words[1]}%"),
                         ),
                    and_(AuthorizedPerson.firstname.like(f"{words[1]}%"),
                         AuthorizedPerson.surname.like(f"{words[0]}%"),
                         ),
                ))
        else:
            return []

        return result_q.order_by(AuthorizedPerson.surname).all()

    def search_authorized_persons(self, expression):
        words = expression.split(" ")

        if len(words) == 1:
            result_q = self.session.query(AuthorizedPerson).filter(
                or_(AuthorizedPerson.firstname.like(f"{words[0]}%"),
                    AuthorizedPerson.surname.like(f"{words[0]}%")
                    ))
        elif len(words) == 2:
            result_q = self.session.query(AuthorizedPerson).filter(
                or_(
                    and_(AuthorizedPerson.firstname.like(f"{words[0]}%"),
                         AuthorizedPerson.surname.like(f"{words[1]}%"),
                         ),
                    and_(AuthorizedPerson.firstname.like(f"{words[1]}%"),
                         AuthorizedPerson.surname.like(f"{words[0]}%"),
                         ),
                ))
        else:
            return []

        return result_q.order_by(AuthorizedPerson.surname).all()

    def search_rooms(self, expression, floor=None):
        rooms_q = self.session.query(Room).filter(Room.name.like(f"%{expression}%")).order_by(Room.name)
        if floor:
            rooms_q = rooms_q.filter(Room.floor == floor)
        return rooms_q.all()

    def get_all_authorizations(self):
        return self.session.query(Authorization).filter(Authorization.origin_id==1).all()
    def get_all_authorized_persons(self):
        return self.session.query(AuthorizedPerson).all()

    """
        SCREENS
            Selecty přímo pro obrazovky
    """
    def get_all_authorizations_screen(self):
        s = select(
            Authorization.id,
            AuthorizedPerson.firstname,
            AuthorizedPerson.surname,
            AuthorizationOrigin.name,
            Authorization.created,
            Authorization.expiration,
            Room.name).\
            filter(Authorization.expiration > datetime.datetime.utcnow()).\
            join(Authorization.origin).join(Authorization.person).join(Authorization.room)

        result = self.session.execute(s).all()
        return result

