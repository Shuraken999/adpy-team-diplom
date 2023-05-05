from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id_user = Column(Integer, primary_key=True)
    name = Column(String(length=40), unique=True)
    surname = Column(String(length=40), unique=True)
    age = Column(Integer)
    gender = Column(String(length=40), unique=True)
    city = Column(String(length=40), unique=True)

    def __str__(self):
        return f'{self.name}'


class BaseMan(Base):
    __tablename__ = "baseman"

    id_base_man = Column(Integer, primary_key=True)
    name = Column(String(length=40), unique=True)
    surname = Column(String(length=40), unique=True)
    link = Column(String(length=4000), unique=True)
    foto = Column(String(length=4000), unique=True)

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
        return f'{self.name}'


class Disregard(Base):
    __tablename__ = "disregard"

    id_disregard = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id_user"), nullable=False)
    man_id = Column(Integer, ForeignKey("baseman.id_base_man"), nullable=False)

    user = relationship(User, backref="disregard")
    baseman = relationship(BaseMan, backref="disregard")


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
