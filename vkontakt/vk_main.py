import os
import asyncio
from pprint import pprint
from dotenv import load_dotenv, find_dotenv
from vkbottle import Keyboard, KeyboardButtonColor, Text, API
from datetime import datetime
from vkbottle.exception_factory import VKAPIError
from random import randint


load_dotenv(find_dotenv())
token = (os.getenv('token_vk'))
api = API(token=token)


async def get_inf(uid):
    user_info = await api.users.get(token=token, user_ids=uid, fields='bdate, sex, city')
    user_info_dict = user_info[0].__dict__

    if user_info_dict.get('bdate') != None:
        # Преобразование строки в объект даты
        bdate = datetime.strptime(user_info_dict.get('bdate'), '%d.%m.%Y')
        # Получение текущей даты
        today = datetime.today()
        # Вычисление возраста в годах
        age = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
    else:
        age = None

    if user_info_dict.get('city') is not None:
        city_id = user_info_dict.get('city').id
    else:
        city_id = None
    need_info = {
        'id': user_info_dict.get('id'),
        'age': age,
        'sex': user_info_dict.get('sex').value,
        'city': city_id
    }
    return need_info


async def search(age, sex, city, offset):
    users = await api.users.search(sex=sex, city=city, age_from=age-2, age_to=age+2, count=1, offset=offset)
    users_with_photos = []
    for user in users.items:
        try:
            user_info = await get_inf(user.id)
            user_photos = await api.photos.get(owner_id=user.id, album_id='profile', count=3)
            user_info['photos'] = [photo.id for photo in user_photos.items]
            # добавляем имя пользователя
            user_info['first_name'] = (await api.users.get(user_ids=user_info.get('id'), fields='status'))[0].first_name
            # добавляем фамилию пользователя
            user_info['last_name'] = (await api.users.get(user_ids=user_info.get('id'), fields='status'))[0].last_name
            user_info['link'] = f"https://vk.com/" \
            f"{(await api.users.get(user_ids=user_info.get('id'), fields='screen_name'))[0].screen_name}"
            users_with_photos.append(user_info)
            await asyncio.sleep(1)  # задержка перед requests
        except VKAPIError as e:
            print(f"Skipping user {user.id}: profile is private")
            continue
    return users_with_photos

if __name__ == '__main__':
    pprint(asyncio.run(search(20, 2, 2, 1)))
