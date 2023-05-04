import os
from dotenv import load_dotenv, find_dotenv
import vk_api
from pprint import pprint
from datetime import datetime


def user_data(user_id):
    users = session.method('users.get', {'user_id': user_id,
                                         'fields': 'bdate, sex, screen_name, city'} )
    photos = session.method('photos.get', {'user_id': user_id,
                                           'count': 6,
                                           'album_id': 'profile',
                                           'extended': 1})
    vk_sizes = {'s': 1, 'm': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'x': 7, 'y': 8, 'z': 9, 'w': 10}
    dict1 = {}
    for photo in photos['items']:
        likes = photo['likes']['count']
        size = max(photo['sizes'], key=lambda s: vk_sizes[s['type']])
        url1 = size['url']
        dict1[url1] = likes
    sorted_photos = sorted(dict1.items(), key=lambda x: x[1], reverse=True)
    top_3_photos = sorted_photos[:3]
    for user in users:
        profile_link = f"https://vk.com/{user['screen_name']}"
        first_name = user['first_name']
        last_name = user['last_name']
        try:
            city = user['city']['title']
        except KeyError:
            city = 'город не указан'
        date_time = datetime.today()
        date = date_time.date()
        age = user['bdate']
        datetime_obj = datetime.strptime(age, '%d.%m.%Y').date()
        result_date = date - datetime_obj
        date_year = result_date / 365
        if user['sex'] == 2:
            sex = 'мужской'
        else:
            sex = 'женский'
        dict = {
            'user_photo': top_3_photos,
            'name': first_name,
            'last_name': last_name,
            'city': city,
            'sex': sex,
            'human_age': date_year.days,
            'profile_link': profile_link
        }


        return dict

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    token = (os.getenv('token_vk'))
    session = vk_api.VkApi(token=token)
    pprint(user_data('154186755'))