import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from vkbottle import Keyboard, KeyboardButtonColor, Text, API

load_dotenv(find_dotenv())
token = (os.getenv('token_vk'))
api = API(token=token)

async def get_inf(uid):
    user_info = await api.users.get(token=token, user_ids=uid, fields='bdate, sex, screen_name, city')
    user_info_dict = user_info[0].__dict__

    bdate = user_info_dict.get('bdate')
    sex = user_info_dict.get('sex')
    screen_name = user_info_dict.get('screen_name')
    city = user_info_dict.get('city').title

if __name__ == '__main__':
    asyncio.run(get_inf(1))