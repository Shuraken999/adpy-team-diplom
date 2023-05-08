from sqlalchemy import create_engine
import json
from sqlalchemy.orm import sessionmaker

from models import create_tables, User, BaseMan, Favorites, Disregard
from settings import DSN

# Подключение к БД
engine = create_engine(DSN)
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()

with open("bd.json", encoding='utf-8') as f:
    json_data = json.load(f)

# Занесение данных в БД временно из json-файла
for model in json_data:
    if model["model"] == 'user':
        us = User(name=model["fields"]["name"], surname=model["fields"]["surname"], age=model["fields"]["age"],
                  gender=model["fields"]["gender"], city=model["fields"]["city"])
        session.add(us)
    elif model["model"] == 'baseman':
        bm = BaseMan(name=model["fields"]["name"], surname=model["fields"]["surname"], link=model["fields"]["link"],
                     foto1=model["fields"]["foto1"], foto2=model["fields"]["foto2"], foto3=model["fields"]["foto3"])
        session.add(bm)
    elif model["model"] == 'favorites':
        fr = Favorites(user_id=model["fields"]["user"], man_id=model["fields"]["man"])
        session.add(fr)
    elif model["model"] == 'disregard':
        dg = Disregard(user_id=model["fields"]["user"], man_id=model["fields"]["man"])
        session.add(dg)

user_id = input('Введите идентификатор пользователя: ')  # Ввод id пользователя для получения списка избранных
man = session.query(Favorites).filter(Favorites.user_id == user_id).subquery()  # Фильтрация избранных пользователя
# Выборка по одному избранному из таблицы всех сохраненных избранных
for name, surname, link, foto1, foto2, foto3 in \
        session.query(BaseMan.name, BaseMan.surname, BaseMan.link, BaseMan.foto1, BaseMan.foto2, BaseMan.foto3).\
        join(man, BaseMan.id_base_man == man.c.man_id).all():

    print(f' {name} {name} {link} {foto1} {foto2} {foto3}')

session.commit()
session.close()

