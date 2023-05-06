from vkbottle.bot import Bot, Message
import os, asyncio
from dotenv import load_dotenv, find_dotenv
from vkbottle import Keyboard, KeyboardButtonColor, Text

load_dotenv(find_dotenv())
token = (os.getenv('token_group_vk'))
bot = Bot(token=token)

attachment = ['photo390537959_457250343', 'photo390537959_457250140']
# Simplest way of generating keyboard is non-builder interface
# Use <.row()> to add row
# Use <.add(Action(...), COLOR)> to add button to the last row
# Use <.get_json()> to make keyboard sendable
KEYBOARD_STANDARD = Keyboard(one_time=True, inline=False)
KEYBOARD_STANDARD.add(Text("Button 1"), color=KeyboardButtonColor.POSITIVE)
KEYBOARD_STANDARD.add(Text("Button 2"))
KEYBOARD_STANDARD.row()
KEYBOARD_STANDARD.add(Text("Button 3"))
KEYBOARD_STANDARD = KEYBOARD_STANDARD.get_json()  # type: ignore

# add and row methods returns the instance of Keyboard
# so, you can use it as builder
KEYBOARD_WITH_BUILDER = (
    Keyboard(one_time=False, inline=True)
    .add(Text("👎"), color=KeyboardButtonColor.NEGATIVE)
    .add(Text("💕"), color=KeyboardButtonColor.POSITIVE)
    .add(Text("вперёд"), color=KeyboardButtonColor.PRIMARY)
    .get_json()
)

# Schema is another way to create keyboard
# all fields except of color are read as action fields
KEYBOARD_WITH_SCHEMA = (
    Keyboard(one_time=True, inline=False)
    .schema(
        [
            [
                {"label": "Button 1", "type": "text", "color": "positive"},
                {"label": "Button 2", "type": "text"},
            ],
            [{"label": "Button 3", "type": "text"}],
        ]
    )
    .get_json()
)

@bot.on.message(text='lol')
async def hi_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    await message.answer("р {}".format(users_info[0].first_name))

@bot.on.message()
async def send_keyboard(message):
    await message.answer("Типо человек бла бла", keyboard=KEYBOARD_WITH_BUILDER, attachment=attachment)

bot.run_forever()