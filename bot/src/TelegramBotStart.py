import asyncio

from TelegramBotNames import *

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

def start_bot(
        token: str,
        to_log: bool = True
    ) -> None:
    """
    Starting bot with your token

    :param token: Your token. Could get in @BotFather.
    :param to_log: Bool. Printing bot's token and address.
    """

    bot = Bot(token)
    dp = Dispatcher()

    storage = {
        'first_message': True,
        'image': None
    }

    @dp.message(Command(commands=['start', 'help']))
    async def start(message: Message):
        if storage['first_message']:
            await bot.send_animation(message.from_user.id, "https://media1.tenor.com/m/5hKPyupKGWMAAAAC/robot-hello.gif")
            await bot.send_message(message.from_user.id, f"Hello, {message.from_user.first_name}! I'm BOT that working on Deepface and Tensorflow!\n<a href='{github_link}'><b><u>Github</u></b></a>", parse_mode=ParseMode.HTML)

            storage['first_message'] = False
        
        await bot.send_message(message.from_user.id, start_message)


    # starting bot
    async def main():
        await bot.delete_webhook(drop_pending_updates=True)

        if to_log:
            info_bot = await bot.get_me()
            print(f"Starting bot {info_bot.first_name} with token {token} (aiogram). https://t.me/{info_bot.username} | @{info_bot.username}")

        await dp.start_polling(bot)
    
    asyncio.run(main())