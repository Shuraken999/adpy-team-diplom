from sqlalchemy import Column, Integer, String, ForeignKey, BIGINT
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id_user = Column(Integer, primary_key=True)
    age = Column(Integer, unique=True)
    sex = Column(String(length=40), unique=True)
    city = Column(String(length=40), unique=True)

    def __str__(self):
        return f'{self.name}'


class Photo(Base):
    __tablename__ = "photo"

    id_photo = Column(BIGINT, primary_key=True)
    photo1 = Column(String(length=4000), unique=True)
    photo2 = Column(String(length=4000), unique=True)
    photo3 = Column(String(length=4000), unique=True)

    def __str__(self):
        return f'{self.title}'

class UserSearch(Base):
    __tablename__ = "usersearch"

    id_user_search = Column(Integer, primary_key=True)
    first_name = Column(String(length=40), unique=True)
    last_name = Column(String(length=40), unique=True)
    link = Column(String(length=4000), unique=True)
    age = Column(Integer, unique=True)
    sex = Column(String(length=40), unique=True)
    city = Column(String(length=40), unique=True)
    photo_id = Column(BIGINT, ForeignKey('photo.id_photo'), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id_user"), nullable=False)

    user = relationship(User, backref="usersearch")
    photo = relationship(Photo, backref="usersearch")

    def __str__(self):
        return f'{self.name}'

class SeeUser(Base):
    __tablename__ = "seeuser"

    id_see_user = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id_user"), nullable=False)

    user = relationship(User, backref="seeuser")

    def __str__(self):
        return f'{self.name}'
class BaseMan(Base):
    __tablename__ = "baseman"

    id_base_man = Column(Integer, primary_key=True)
    first_name = Column(String(length=40), unique=True)
    last_name = Column(String(length=40), unique=True)
    link = Column(String(length=4000), unique=True)
    photo_id = Column(BIGINT, ForeignKey('photo.id_photo'), nullable=False)

    photo = relationship(Photo, backref="baseman")

    def __str__(self):
        return f'{self.title}'


class Favorites(Base):
    __tablename__ = "favorites"

    id_favorit = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id_user"), nullable=False)
    man_id = Column(Integer, ForeignKey("baseman.id_base_man"), nullable=False)

    user = relationship(User, backref="favorites")
    baseman = relationship(BaseMan, backref="favorites")

    def __str__(self):
        return f'{self.title}'
# Зачистка и новое создание БД
def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
