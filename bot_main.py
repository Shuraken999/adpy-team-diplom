from vkbottle.bot import Bot, Message
import os
from dotenv import load_dotenv, find_dotenv
from vkbottle import Keyboard, KeyboardButtonColor, Text
from vkontakt import metods
from vkbottle.exception_factory import VKAPIError

# Получаем токен
load_dotenv(find_dotenv())
token = (os.getenv('token_group_vk'))
bot = Bot(token=token)

M_J_KEYBOARD = (
    Keyboard(one_time=False, inline=True)
    .add(Text("м"), color=KeyboardButtonColor.POSITIVE)
    .add(Text("ж"), color=KeyboardButtonColor.PRIMARY)
    .get_json()
)

SKIP_BUTTONS = (
    Keyboard(one_time=False, inline=True)
    .add(Text("👎"), color=KeyboardButtonColor.NEGATIVE)
    .add(Text("💕"), color=KeyboardButtonColor.POSITIVE)
    .add(Text("вперёд"), color=KeyboardButtonColor.PRIMARY)
    .get_json()
)

user_gender = {}

@bot.on.message(text='Начать')
async def handle_message(message: Message):
    await message.answer('😉 Отлично!')
    user_id = message.from_id
    try:
        result = await metods.get_inf(user_id)
    except VKAPIError:
        await message.answer('Ваш профиль закрыт 😕\nОткройте профлиль для работы бота.')
        return
    if result.get('age') == None or result.get('sex') == None or result.get('city') == None:
        await message.answer('У вашего профиля не заполнен пол, возраст или город. Мы не можем найти вам пару 😕')
        return
    await message.answer("Какого пола будем искать пару?", keyboard=M_J_KEYBOARD)

@bot.on.message(text='м')
async def handle_male(message: Message):
    user_id = message.from_id
    user_gender[user_id] = "м"
    await message.answer("Вы выбрали мужской пол", keyboard=(
    Keyboard(one_time=False, inline=True)
    .add(Text("Начать поиск!"), color=KeyboardButtonColor.PRIMARY)
    .get_json()
))

@bot.on.message(text='ж')
async def handle_female(message: Message):
    user_id = message.from_id
    user_gender[user_id] = "ж"
    await message.answer("Вы выбрали женский пол", keyboard=(
    Keyboard(one_time=False, inline=True)
    .add(Text("Начать поиск!"), color=KeyboardButtonColor.PRIMARY)
    .get_json()
))

i = 0

@bot.on.message(text='Начать поиск!')
async def start_searching(message: Message):
    global i
    await message.answer('Ищу пару...')
    user_id = message.from_id
    try:
        result = await metods.get_inf(user_id)
    except VKAPIError as e:
        await message.answer('Ваш профиль закрыт 😕\nОткройте профлиль для работы бота.')
        return
    if result.get('age') == None or result.get('sex') == None or result.get('city') == None:
        await message.answer('У вашего профиля не заполнен пол, возраст или город. Мы не можем найти вам пару 😕')
        return
    find = await metods.search(result.get('age'), result.get('sex'), result.get('city'), i)
    photos = find[0].get('photos')
    if photos:
        attachment = [f'photo{find[0].get("id")}_{photo_id}' for photo_id in photos]  # формируем список ссылок на фотографии
        print(attachment)
        await message.answer(f"{find[0].get('first_name')} {find[0].get('last_name')}. Возраст: {find[0].get('age')}.\nСтатус: {find[0].get('status')}", attachment=attachment, keyboard=SKIP_BUTTONS)
    else:
        await message.answer(f"{find[0].get('first_name')} {find[0].get('last_name')}. Возраст: {find[0].get('age')}.\nСтатус: {find[0].get('status')}", keyboard=SKIP_BUTTONS)
    i+=1

@bot.on.message(text='вперёд')
async def skipping(message: Message):
    await start_searching(message)

bot.run_forever()