import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from vkbottle import Keyboard, KeyboardButtonColor, Text, API
from datetime import datetime

load_dotenv(find_dotenv())
token = (os.getenv('token_vk'))
api = API(token=token)

async def get_inf(uid):
    user_info = await api.users.get(token=token, user_ids=uid, fields='bdate, sex, city')
    user_info_dict = user_info[0].__dict__
    # Преобразование строки в объект даты
    bdate = datetime.strptime(user_info_dict.get('bdate'), '%d.%m.%Y')

    # Получение текущей даты
    today = datetime.today()

    # Вычисление возраста в годах
    age = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
    need_info = {
        'bdate': age,
        'sex': user_info_dict.get('sex').value,
        'city': user_info_dict.get('city').id
    }
    return need_info
    # bdate = user_info_dict.get('bdate')
    # sex = user_info_dict.get('sex')
    # screen_name = user_info_dict.get('screen_name')
    # city = user_info_dict.get('city').title
    # print(bdate, sex, city)

async def searcher(bdate, sex, city):
    users = await api.users.search()

if __name__ == '__main__':
    asyncio.run(get_inf(1))