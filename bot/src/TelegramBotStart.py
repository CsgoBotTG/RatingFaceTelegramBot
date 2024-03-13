import os
import cv2
import asyncio

from TelegramBotConfig import *
from DeepFaceFunctions import *
from TelegramBotHelper import *

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
        'founded_id': None
    }

    @dp.message(Command(commands=['start', 'help']))
    async def start(message: Message):
        if storage['first_message']:
            print(f'First message by {message.from_user.first_name} | {message.from_user.id}')

            await bot.send_animation(message.from_user.id, "https://media1.tenor.com/m/5hKPyupKGWMAAAAC/robot-hello.gif")
            await bot.send_message(message.from_user.id, f"Hello, {message.from_user.first_name}! I'm BOT that working on Deepface and Tensorflow!\n<a href='{github_link}'><b><u>Github</u></b></a>", parse_mode=ParseMode.HTML)

            storage['first_message'] = False

        await bot.send_message(message.from_user.id, start_message)


    # get image
    @dp.message(F.photo)
    async def get_image(message: Message, state: FSMContext):
        image = await get_image_from_message(bot, message)
        await bot.send_message(message.from_user.id, 'Got image')

        for index in range(len(os.listdir(data_path)) // 2):
            image_check_path = f'{data_path}{index}.jpg'
            image_check = cv2.imread(image_check_path)

            result = verify_in_photo(image, image_check, detector_backend_model, verify_model)

            if result['verified']:

                area = result['facial_areas']['img1']
                x, y, w, h = area['x'], area['y'], area['w'], area['h']

                face = image[y:y+h, x:x+w]

                send_image(bot, message, face, "Face in your photo")
                send_image(bot, message, image_check, "Face in database")

                storage['founded_id'] = index
                break
        else:
            await bot.send_message(message.from_user.id, "Didn't find in database")
            
            face = get_face_from_photo(image, detector_backend_model)
            send_image(bot, message, face, 'Founded face')

            index = len(os.listdir(data_path)) // 2
            storage['founded_id'] = index

            await bot.send_message(message.from_user.id, 'Saving...')
            cv2.imwrite(f'{data_path}{index}.jpg', face)
            with open(f'{data_path}{index}.txt', 'w') as file:
                file.write('5.0')
            await bot.send_message(message.from_user.id, 'Saved')

        rating = None
        with open(f"{data_path}{storage['founded_id']}.txt") as rating_file:
            rating = float(rating_file.read())

        await bot.send_message(message.from_user.id, f'<u>Rating</u> this face: {rating}', parse_mode=ParseMode.HTML)
        await state.set_state(GetGrade.Grade)


    # starting bot
    async def main():
        await bot.delete_webhook(drop_pending_updates=True)

        if to_log:
            info_bot = await bot.get_me()
            print(f"Starting bot {info_bot.first_name} with token {token} (aiogram). https://t.me/{info_bot.username} | @{info_bot.username}")

        await dp.start_polling(bot)

    asyncio.run(main())