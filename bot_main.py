from vkbottle.bot import Bot, Message
import os
from dotenv import load_dotenv, find_dotenv
from vkbottle import Keyboard, KeyboardButtonColor, Text

# Получаем токен
load_dotenv(find_dotenv())
token = (os.getenv('token_group_vk'))
bot = Bot(token=token)

@bot.on.message(text='Начать')
async def handle_message(message: Message):
    user_id = message.from_id
    await

bot.run_forever()