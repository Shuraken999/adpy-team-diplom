from sqlalchemy import create_engine
import json
from sqlalchemy.orm import sessionmaker

from models import create_tables, User, BaseMan, Favorites, Disregard
# from settings import DSN


engine = create_engine('postgresql://postgres:123456@localhost:5432/testkurs')

create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()

with open("bd.json", encoding='utf-8') as f:
    json_data = json.load(f)
for model in json_data:
    if model["model"] == 'user':
        us = User(name=model["fields"]["name"], surname=model["fields"]["surname"], age=model["fields"]["age"],
                  gender=model["fields"]["gender"], city=model["fields"]["city"])
        session.add(us)
    elif model["model"] == 'baseman':
        bm = BaseMan(name=model["fields"]["name"], surname=model["fields"]["surname"], link=model["fields"]["link"],
                     foto=model["fields"]["foto"])
        session.add(bm)
    elif model["model"] == 'favorites':
        fr = Favorites(user_id=model["fields"]["user"], man_id=model["fields"]["man"])
        session.add(fr)
    elif model["model"] == 'disregard':
        dg = Disregard(user_id=model["fields"]["user"], man_id=model["fields"]["man"])
        session.add(dg)

session.commit()
session.close()

