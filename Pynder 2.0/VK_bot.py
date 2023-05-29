from vk_main import search, get_inf
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

engine = create_engine(DSN)
create_tables(engine)
Session = sessionmaker(bind=engine)


class Man:
    def __init__(self, id_man=None, first_name=None, last_name=None, age=None, sex=None, city=None, link=None, sex_pair=None):
        self.id_man = id_man
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.sex = sex
        self.city = city
        self.link = link
        self.sex_pair = sex_pair
        self.photos = {}


user = Man()
man = Man()
i = 1


async def add_user(user_id, age, sex, city):
    session = Session()
    session.add(User(id_user=user_id,
                     age=age,
                     sex=sex,
                     city=city
                     )
                )
    session.commit()
    session.close()





@bot.on.message(text='Привет')
async def handle_message(message: Message):
    await message.answer('😉 Отлично! Начинаем подбирать пару')
    user_id = message.from_id
    try:
        result = await get_inf(user_id)

    except VKAPIError:
        await message.answer('Ваш профиль закрыт 😕\nОткройте профиль для работы бота.')
        return
    if result.get('age') is None or result.get('sex') is None or result.get('city') is None:
        await message.answer('У вашего профиля не заполнен пол, возраст или город. Мы не можем найти вам пару 😕')
        return
    user.id_man = user_id
    user.age = result.get('age')
    user.sex = result.get('sex')
    user.city = result.get('city')
    await add_user(user_id, user.age, user.sex, user.city)
    await message.answer("Какого пола будем искать пару?", keyboard=M_J_KEYBOARD)


@bot.on.message(text='м')
async def handle_male(message: Message):
    user.sex_pair = 2
    await message.answer("Вы выбрали для поиска мужской пол",
                         keyboard=(Keyboard(one_time=False, inline=True)
                                   .add(Text("Начать поиск!"), color=KeyboardButtonColor.PRIMARY)
                                   .get_json()
                                   ))


@bot.on.message(text='ж')
async def handle_female(message: Message):
    user.sex_pair = 1
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
    find = await search(user.age, user.sex_pair, user.city, i)
    man.id_man = find[0].get('id')
    man.first_name = find[0].get('first_name')
    man.last_name = find[0].get('last_name')
    man.link = find[0].get('link')
    man.age = find[0].get('age')
    man.sex = find[0].get('sex')
    man.city = find[0].get('first_name')
    man.photos = find[0].get('photos')

    if message.reply_message:
        if man.photos:
            attachment = [f'photo{man.id_man}_{photo_id}' for photo_id in man.photos]
        else:
            attachment = None
        await message.answer(
            f"{man.first_name} {man.last_name}.\n Возраст: {man.age}."
            f"\nСсылка на профиль: {man.link}",
            reply_to=message.reply_message.from_id, attachment=attachment, keyboard=SKIP_BUTTONS)
        return
    else:
        if man.photos:
            attachment = [f'photo{man.id_man}_{photo_id}' for photo_id in man.photos]
        else:
            attachment = None
        await message.answer(
            f"{man.first_name} {man.last_name}.\n Возраст: {man.age}."
            f"\nСсылка на профиль: {man.link}",
            attachment=attachment, keyboard=SKIP_BUTTONS)
        return


@bot.on.message(text='Добавить в избранное')
async def add_to_favorites_handler(message: Message):
    if man.first_name is not None and man.last_name is not None:
        # Занесение данных в БД
        session = Session()
        print(man.photos)
        if len(man.photos) == 3:
            photo1 = f'https://vk.com/photo{man.id_man}_{man.photos[0]}'
            photo2 = f'https://vk.com/photo{man.id_man}_{man.photos[1]}'
            photo3 = f'https://vk.com/photo{man.id_man}_{man.photos[2]}'
        elif len(man.photos) == 2:
            photo1 = f'https://vk.com/photo{man.id_man}_{man.photos[0]}'
            photo2 = f'https://vk.com/photo{man.id_man}_{man.photos[1]}'
            photo3 = f'https://vk.com/photo{man.id_man}_{man.photos[1]}'
        else:
            photo1 = f'https://vk.com/photo{man.id_man}_{man.photos[0]}'
            photo2 = f'https://vk.com/photo{man.id_man}_{man.photos[0]}'
            photo3 = f'https://vk.com/photo{man.id_man}_{man.photos[0]}'
        session.add(BaseMan(id_base_man=man.id_man,
                            first_name=man.first_name,
                            last_name=man.last_name,
                            link=man.link,
                            photo_id=int(f'{man.id_man}{user.id_man}')
                            )
                    )
        session.add(Photo(id_photo=int(f'{man.id_man}{user.id_man}'),
                          photo1=photo1,
                          photo2=photo2,
                          photo3=photo3,
                          )
                    )
        await message.answer(f"Пользователь {man.first_name} добавлен в избранное.")
        session.add(Favorites(user_id=user.id_man, man_id=man.id_man))
        session.commit()
        session.close()
    else:
        await message.answer(f"Не удалось добавить в избранное")


@bot.on.message(text='Показать избранных')
async def show_favorites_handler(message: Message):
    session = Session()
    user_man = session.query(Favorites).filter(Favorites.user_id == user.id_man).subquery()  # Фильтрация избранных пользователя
    if user_man is None:
        await message.answer("Список избранных пользователей пуст")
    else:
        # Выборка по одному избранному из таблицы всех сохраненных избранных
        await message.answer("Список избранных пользователей:\n")
        for first_name, last_name, link, photo1, photo2, photo3 in \
                session.query(BaseMan.first_name, BaseMan.last_name,
                              BaseMan.link, Photo.photo1, Photo.photo2, Photo.photo3).join(Photo,
                              BaseMan.photo_id == Photo.id_photo).all():
            await message.answer(f'{first_name} {last_name}\nСсылка на профиль: {link}\nФото:\n{photo1}\n{photo2}\n{photo3}')
        await message.answer(keyboard=SKIP_BUTTONS)
    session.commit()
    session.close()


@bot.on.message(text='Далее')
async def skipping(message: Message):
    await start_searching(message)

bot.run_forever()
