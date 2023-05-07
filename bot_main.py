from vkbottle.bot import Bot, Message
import os
from dotenv import load_dotenv, find_dotenv
from vkbottle import Keyboard, KeyboardButtonColor, Text
from vkontakt import metods

# Получаем токен
load_dotenv(find_dotenv())
token = (os.getenv('token_group_vk'))
bot = Bot(token=token)

@bot.on.message(text='Начать')
async def handle_message(message: Message):
    await message.answer('😉 Отлично! \nВыполняю поиск пары...')
    user_id = message.from_id
    result = await metods.get_inf(user_id)
    await message.answer(result)

bot.run_forever()