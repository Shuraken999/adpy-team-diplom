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


    if user_info_dict.get('bdate') is not None:
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
        'name': user_info_dict.get('first_name'),
        'last_name': user_info_dict.get('last_name'),
        'id': user_info_dict.get('id'),
        'age': age,
        'sex': user_info_dict.get('sex').value,
        'city': city_id
    }
    return need_info


async def search(age, sex, city, offset=0, count=1):
    random = randint(0, 999)
    users = await api.users.search(sex=sex, city=city, age_from=age - 2, age_to=age + 2, count=count, offset=offset)
    users_with_photos = []
    for user in users.items:
        try:
            user_info = await api.users.get(token=token, user_ids=user.id, fields='bdate, sex, city, screen_name')
            user_info_dict = user_info[0].__dict__

            user_photos = await api.photos.get(owner_id=user.id, count=6,
                                               album_id='profile',
                                               extended=1)
            if user_info_dict.get('bdate') is not None:
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
            dict_ = {}
            list_photos = []
            for photo in user_photos.items:
                dict_[photo.id] = photo.likes.count
            sorted_photos = sorted(dict_.items(), key=lambda x: x[1], reverse=True)
            top_3_photos = sorted_photos[:3]
            for top_photo in top_3_photos:
                photo_top_3 = top_photo[0]
                list_photos.append(photo_top_3)
            dict_profile = {
                'photos': list_photos,
                'first_name': user_info_dict.get('first_name'),
                'last_name': user_info_dict.get('last_name'),
                'link': f"https://vk.com/{user_info_dict.get('screen_name')}",
                'id': user_info_dict.get('id'),
                'age': age,
                'sex': user_info_dict.get('sex').value,
                'city': city_id
            }  # добавляем пользователя
            users_with_photos.append(dict_profile)
            await asyncio.sleep(1)  # задержка перед requests
        except VKAPIError as e:
            print(f"Skipping user {user.id}: profile is private")
            continue
    return users_with_photos


if __name__ == '__main__':
    pprint(asyncio.run(search(20, 2, 2,)))
