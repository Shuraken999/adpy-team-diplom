import os
import asyncio
from pprint import pprint
from dotenv import load_dotenv, find_dotenv
from vkbottle import API
from datetime import datetime
from vkbottle.exception_factory import VKAPIError

load_dotenv(find_dotenv())
token = (os.getenv('token_vk'))
api = API(token=token)


async def get_inf(uid):
    user_info = await api.users.get(token=token, user_ids=uid, fields=['bdate, sex, city, screen_name'])
    user_info_dict = user_info[0].__dict__
    if user_info_dict.get('bdate') is not None:
        # Преобразование строки в объект даты
        if datetime.strptime(user_info_dict.get('bdate'), '%d.%m.%Y') == '2.7':
            age = 0
        else:
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
        'first_name': user_info_dict.get('first_name'),
        'last_name': user_info_dict.get('last_name'),
        'id': user_info_dict.get('id'),
        'link': f"https://vk.com/{user_info_dict.get('screen_name')}",
        'age': age,
        'sex': user_info_dict.get('sex').value,
        'city': city_id
    }
    return need_info


async def search(age, sex, city, offset=2, count=5):
    users = await api.users.search(sex=sex, city=city, age_from=age - 2, age_to=age + 2, offset=offset, count=count,)
    users_with_photos = []
    for user in users.items:
        try:
            user_info_dict = await get_inf(user.id)
            user_photos = await api.photos.get(owner_id=user.id, count=100,
                                               album_id='profile',
                                               extended=True)
            dict_ = {}
            list_photos = []
            for photo in user_photos.items:
                dict_[photo.id] = photo.likes.count
            sorted_photos = sorted(dict_.items(), key=lambda x: x[1], reverse=True)
            for top_photo in sorted_photos[:3]:
                list_photos.append(top_photo[0])
            dict_profile = {
                'photos': list_photos,
                'first_name': user_info_dict.get('first_name'),
                'last_name': user_info_dict.get('last_name'),
                'link': user_info_dict.get('link'),
                'id': user_info_dict.get('id'),
                'age': user_info_dict.get('age'),
                'sex': user_info_dict.get('sex'),
                'city': user_info_dict.get('city')
            }  # добавляем пользователя
            users_with_photos.append(dict_profile)
            await asyncio.sleep(1)  # задержка перед requests
        except VKAPIError:
            print(f"Skipping user {user.id}: profile is private")
    return users_with_photos


if __name__ == '__main__':
    pprint(asyncio.run(search(20, 2, 2,)))
