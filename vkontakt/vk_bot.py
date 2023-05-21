import vk_main
import os
from dotenv import load_dotenv, find_dotenv
from vkbottle import Keyboard, KeyboardButtonColor, Text
from vkbottle.exception_factory import VKAPIError
from vkbottle.bot import Bot, Message
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import create_tables, User, BaseMan, Favorites, Photo


DSN = 'postgresql://postgres:123456@localhost:5432/test'

# Получаем токен
load_dotenv(find_dotenv())
token = (os.getenv('token_group'))
bot = Bot(token=token)

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

# engine = create_engine(DSN)
# create_tables(engine)
# Session = sessionmaker(bind=engine)


class UserMan:
    def __init__(self, id_user=None, age=None, sex=None, city=None, sex_pair=None):
        self.id_user = id_user
        self.age = age
        self.sex = sex
        self.city = city
        self.sex_pair = sex_pair

class ManSearch:
    def __init__(self, id_man=None, first_name=None, last_name=None, age=None, sex=None, city=None, link=None):
        self.id_man = id_man
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.sex = sex
        self.city = city
        self.link = link
        self.photos = {}


first_user = UserMan()
man_two = ManSearch()
user_gender = {}
i = 1


# async def add_user(user_id, age, sex, city):
#     session = Session()
#     session.add(User(id_user=user_id,
#                      age=age,
#                      sex=sex,
#                      city=city
#                      )
#                 )
#     session.commit()
#     session.close()


async def estimate_user(user_id, message: Message):
    try:
        result = await vk_main.get_inf(user_id)
    except VKAPIError:
        await message.answer('Ваш профиль закрыт 😕\nОткройте профиль для работы бота.')
        return
    if result.get('age') is None or result.get('sex') is None or result.get('city') is None:
        await message.answer('У вашего профиля не заполнен пол, возраст или город. Мы не можем найти вам пару 😕')
        return
    first_user.id_user = user_id
    first_user.age = result.get('age')
    first_user.sex = result.get('sex')
    first_user.city = result.get('city')
    return


@bot.on.message(text='Привет')
async def handle_message(message: Message):
    await message.answer('😉 Отлично! Начинаем подбирать пару')
    user_id = message.from_id
    await estimate_user(user_id, message)
    # await add_user(user_id, first_user.age, first_user.sex, first_user.city)
    await message.answer("Какого пола будем искать пару?", keyboard=M_J_KEYBOARD)


@bot.on.message(text='м')
async def handle_male(message: Message):
    first_user.sex_pair = 2
    await message.answer("Вы выбрали для поиска мужской пол",
                         keyboard=(Keyboard(one_time=False, inline=True)
                                   .add(Text("Начать поиск!"), color=KeyboardButtonColor.PRIMARY)
                                   .get_json()
                                   ))


@bot.on.message(text='ж')
async def handle_female(message: Message):
    first_user.sex_pair = 1
    await message.answer("Вы выбрали для поиска женский пол",
                         keyboard=(Keyboard(one_time=False, inline=True)
                                   .add(Text("Начать поиск!"), color=KeyboardButtonColor.PRIMARY)
                                   .get_json()
                                   ))


@bot.on.message(text='Начать поиск!')
async def start_searching(message: Message):
    global i
    i += 1
    await message.answer('Ищу пару...')
    find = await vk_main.search(first_user.age, first_user.sex_pair, first_user.city, i)
    man_two.id_man = find[0].get('id')
    man_two.first_name = find[0].get('first_name')
    man_two.last_name = find[0].get('last_name')
    man_two.link = find[0].get('link')
    man_two.age = find[0].get('age')
    man_two.sex = find[0].get('sex')
    man_two.city = find[0].get('first_name')
    man_two.photos = find[0].get('photos')

    if message.reply_message:
        if man_two.photos:
            attachment = [f'photo{man_two.id_man}_{photo_id}' for photo_id in man_two.photos]
        else:
            attachment = None
        await message.answer(
            f"{man_two.first_name} {man_two.last_name}.\n Возраст: {man_two.age}."
            f"\nСсылка на профиль: {man_two.link}",
            reply_to=message.reply_message.from_id, attachment=attachment, keyboard=SKIP_BUTTONS)
        return
    else:
        if man_two.photos:
            attachment = [f'photo{man_two.id_man}_{photo_id}' for photo_id in man_two.photos]
        else:
            attachment = None
        await message.answer(
            f"{man_two.first_name} {man_two.last_name}.\n Возраст: {man_two.age}."
            f"\nСсылка на профиль: {man_two.link}",
            attachment=attachment, keyboard=SKIP_BUTTONS)
        return



@bot.on.message(text='Добавить в избранное')
async def add_to_favorites_handler(message: Message):
    global i
    if man_two.first_name is not None:
        await message.answer(f"Пользователь {man_two.first_name} добавлен в избранное.")
        with open('favorits.txt', 'a') as f:
            f.write(f"{man_two.id_man} \n")

        # Занесение данных в БД
        # session = Session()
        #
        # session.add(BaseMan(id_base_man=find[0].get('id'),
        #                     first_name=find[0].get('first_name'),
        #                     last_name=find[0].get('last_name'),
        #                     link=find[0].get('link'),
        #                     photo_id=int(f'{find[0].get("id")}{user_id}')
        #                     )
        #             )
        # session.add(Photo(id_photo=int(f'{find[0].get("id")}{user_id}'),
        #                   photo1=find[0].get("photos")[0],
        #                   photo2=find[0].get("photos")[1],
        #                   photo3=find[0].get("photos")[2]
        #                   )
        #             )
        #
        # session.add(Favorites(user_id=user_id, man_id=find[0].get('id')))
        # session.commit()
        # session.close()
    else:
        await message.answer(f"Не удалось добавить в избранное")
    i += 1


@bot.on.message(text='Показать избранных')
async def show_favorites_handler(message: Message):
    with open('favorits.txt') as f:
        favorites = f.read().splitlines()
    if not favorites:
        await message.answer("Список избранных пользователей пуст")
        return
    else:
        profiles = [f"https://vk.com/id{user_id}" for user_id in favorites]
    await message.answer("Список избранных пользователей:\n" + "\n".join(profiles), keyboard=SKIP_BUTTONS)

#     session = Session()
#     user_man = session.query(Favorites).filter(Favorites.user_id == first_user.id_user).subquery()  # Фильтрация избранных пользователя
#     if man is None:
#         await message.answer("Список избранных пользователей пуст")
#     else:
#         # Выборка по одному избранному из таблицы всех сохраненных избранных
#         await message.answer("Список избранных пользователей:\n")
#
#         for first_name, last_name, link, phto1, photo2, photo3 in session.query(BaseMan.first_name, BaseMan.last_name, BaseMan.link, Photo.photo1, Photo.photo2, Photo.photo3)/
#         .join(user_man, BaseMan.id_base_man == user_man.c.man_id).join(Photo.id_photo == BaseMan.photo_id).all():
#             await message.answer(f'{first_name}, {last_name}, {link}, {photo1}, {photo2}, {photo3} ')
#         await message.answer(keyboard=SKIP_BUTTONS)
#     session.commit()
#     session.close()

@bot.on.message(text='Далее')
async def skipping(message: Message):
    await start_searching(message)

bot.run_forever()
