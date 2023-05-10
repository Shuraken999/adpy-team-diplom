from vkbottle.bot import Bot, Message
import vk_main
import os
from dotenv import load_dotenv, find_dotenv
from vkbottle import Keyboard, KeyboardButtonColor, Text

from vkbottle.exception_factory import VKAPIError
from models import create_tables, User, BaseMan, Favorites
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Получаем токен
load_dotenv(find_dotenv())
token = (os.getenv('token_group'))
bot = Bot(token=token)

load_dotenv(find_dotenv())
DSN = (os.getenv('DSN'))

M_J_KEYBOARD = (
    Keyboard(one_time=False, inline=True)
    .add(Text("м"), color=KeyboardButtonColor.POSITIVE)
    .add(Text("ж"), color=KeyboardButtonColor.PRIMARY)
    .get_json()
)

SKIP_BUTTONS = (
    Keyboard(one_time=False, inline=True)
    .add(Text("Показать избранных"), color=KeyboardButtonColor.POSITIVE)
    .add(Text("Добавить в избранное"), color=KeyboardButtonColor.POSITIVE)
    .add(Text("Далее"), color=KeyboardButtonColor.PRIMARY)
    .get_json()
)

user_gender = {}


@bot.on.message(text='Привет')
async def handle_message(message: Message):
    await message.answer('😉 Отлично! Начинаем подбирать пару')
    user_id = message.from_id
    try:
        result = await vk_main.get_inf(user_id)
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
    await message.answer("Вы выбрали для поиска мужской пол", keyboard=(
    Keyboard(one_time=False, inline=True)
    .add(Text("Начать поиск!"), color=KeyboardButtonColor.PRIMARY)
    .get_json()
))


@bot.on.message(text='ж')
async def handle_female(message: Message):
    user_id = message.from_id
    user_gender[user_id] = 'ж'
    await message.answer("Вы выбрали для поиска женский пол", keyboard=(
    Keyboard(one_time=False, inline=True)
    .add(Text("Начать поиск!"), color=KeyboardButtonColor.PRIMARY)
    .get_json()
))

i = 0
m = 1


@bot.on.message(text='Добавить в избранное')
async def add_to_favorites_handler(message: Message):
    global i
    global m
    i -= 1
    user_id = message.from_id
    try:
        result = await vk_main.get_inf(user_id)
        user_gender_choice = user_gender.get(user_id)
        if user_gender_choice == None:
            await message.answer('Пожалуйста, сначала выберите пол, чтобы мы могли найти подходящую пару')
            return
        if user_gender_choice not in ['м', 'ж']:
            await message.answer('Выбранный пол недопустим. Пожалуйста, выберите мужской или женский пол.')
            return
        sex = 2 if user_gender_choice == 'м' else 1
        find = await vk_main.search(result.get('age'), sex, result.get('city'), i)
        await message.answer(f"Пользователь {find[0].get('first_name')} добавлен в избранное.")
        # Занесение данных в БД
        engine = create_engine(DSN)
        create_tables(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(BaseMan(id_base_man=find[0].get('id'),
                            first_name=find[0].get('first_name'),
                            last_name=find[0].get('last_name'),
                            link=find[0].get('link'),
                            photos=find[0].get('photos')
                            )
                    )
        session.add(User(id_user=m,
                         age=find[0].get('age'),
                         sex=find[0].get('sex'),
                         city=find[0].get('city')
                         )
                    )
        session.add(Favorites(user_id=m, man_id=find[0].get('id')))
        session.commit()
        session.close()

    except VKAPIError:
        await message.answer(f"Не удалось добавить в избранное{message.reply_message.from_id}")

    m += 1
    i += 1


@bot.on.message(text='Показать избранных')
async def show_favorites_handler(message: Message):
    engine = create_engine(DSN)
    Session = sessionmaker(bind=engine)
    session = Session()
    man = session.query(Favorites).filter(Favorites.user_id == m).subquery()  # Фильтрация избранных пользователя
    if man == 0:
        await message.answer("Список избранных пользователей пуст")
    else:
        # Выборка по одному избранному из таблицы всех сохраненных избранных
        for first_name, last_name, link, photos in \
            session.query(BaseMan.first_name, BaseMan.last_name, BaseMan.link, BaseMan.photos).join(man,
            BaseMan.id_base_man == man.c.man_id).all():
            await message.answer("Список избранных пользователей:\n" + f'{first_name} {last_name} {link} {photos}',
                                 keyboard=SKIP_BUTTONS)
    session.commit()
    session.close()


@bot.on.message(text='Начать поиск!')
async def start_searching(message: Message):
    global i
    await message.answer('Ищу пару...')
    user_id = message.from_id
    try:
        result = await vk_main.get_inf(user_id)
    except VKAPIError:
        await message.answer('Ваш профиль закрыт 😕\nОткройте профиль для работы бота.')
        return
    if result.get('age') == None or result.get('city') == None:
        await message.answer('У вашего профиля не заполнен возраст или город. Мы не можем найти вам пару 😕')
        return
    user_gender_choice = user_gender.get(user_id)
    if user_gender_choice == None:
        await message.answer('Пожалуйста, сначала выберите пол, чтобы мы могли найти подходящую пару')
        return
    if user_gender_choice not in ['м', 'ж']:
        await message.answer('Выбранный пол недопустим. Пожалуйста, выберите мужской или женский пол.')
        return
    sex = 2 if user_gender_choice == 'м' else 1
    find = await vk_main.search(result.get('age'), sex, result.get('city'), i)
    photos = find[0].get('photos')
    if message.reply_message:
        if photos:
            attachment = [f'photo{find[0].get("id")}_{photo_id}' for photo_id in photos]
        else:
            attachment = None
        await message.answer(
            f"{find[0].get('first_name')} {find[0].get('last_name')}.\n "
            f"Возраст: {find[0].get('age')}.\nCсылка на профиль: {find[0].get('link')}",
            reply_to=message.reply_message.from_id, attachment=attachment, keyboard=SKIP_BUTTONS)
    else:
        if photos:
            attachment = [f'photo{find[0].get("id")}_{photo_id}' for photo_id in photos]
        else:
            attachment = None
        await message.answer(
            f"{find[0].get('first_name')} {find[0].get('last_name')}.\n Возраст: {find[0].get('age')}."
            f"\nCсылка на профиль: {find[0].get('link')}",
            attachment=attachment, keyboard=SKIP_BUTTONS)
        i += 1


@bot.on.message(text='Далее')
async def skipping(message: Message):
    await start_searching(message)


bot.run_forever()
