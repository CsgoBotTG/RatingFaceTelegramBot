import os
import cv2
import glob
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

        await bot.send_message(message.from_user.id, 'Finding in database...')
        for index, image_check_path in enumerate(glob.glob(f'{data_path}*.jpg')):
            image_check = cv2.imread(image_check_path)
            result = verify_in_photo(image, image_check, detector_backend_model, verify_model)

            print(image, image_check, result)
            if result['verified']:
                await bot.send_message(message.from_user.id, 'Found')

                area = result['facial_areas']['img1']
                x, y, w, h = area['x'], area['y'], area['w'], area['h']
                face = image[y:y+h, x:x+w]

                send_image(bot, message, face, "Face in your photo")
                send_image(bot, message, image_check, "Face in database")

                storage['founded_id'] = index
                break
        else:
            await bot.send_message(message.from_user.id, "Didn't find in database")

            index = len(os.listdir(data_path)) // 2
            storage['founded_id'] = index

            await bot.send_message(message.from_user.id, 'Saving...')
            cv2.imwrite(f'{data_path}{index}.jpg', image)
            with open(f'{data_path}{index}.txt', 'w') as file:
                file.write('5.0')
            await bot.send_message(message.from_user.id, 'Saved')

        with open(f"{data_path}{storage['founded_id']}.txt") as rating_file:
            ratings = list(map(float, rating_file.read().split()))

        await bot.send_message(message.from_user.id, f'<u>Rating</u> this face: {sum(ratings) / len(ratings)}', parse_mode=ParseMode.HTML)
        await bot.send_message(message.from_user.id, "Please rate this face from 0 to 10")
        await state.set_state(GetGrade.Grade)


    @dp.message(GetGrade.Grade)
    async def get_grade(message: Message):
        if message.content_type != 'text' or not message.text.isdigit() or not 0 <= int(message.text) <= 10:
            await bot.send_message(message.from_user.id, "It isn't grade from 0 to 10 man...")
        else:
            got_grade = float(message.text)
            await bot.send_message(message.from_user.id, 'Got your grade')

            with open(f"{data_path}{storage['founded_id']}.txt", 'r+') as rating_file:
                ratings_txt = rating_file.read()
                ratings = list(map(float, ratings_txt.split()))
                ratings.append(got_grade)
                avg_rating = sum(ratings) / len(ratings)

                rating_file.write(f' {got_grade}')
                await bot.send_message(message.from_user.id, f'Now <u>rating</u> of this face: {avg_rating}', parse_mode=ParseMode.HTML)


    # starting bot
    async def main():
        await bot.delete_webhook(drop_pending_updates=True)

        if to_log:
            info_bot = await bot.get_me()
            print(f"Starting bot {info_bot.first_name} with token {token} (aiogram). https://t.me/{info_bot.username} | @{info_bot.username}")

        await dp.start_polling(bot)

    asyncio.run(main())