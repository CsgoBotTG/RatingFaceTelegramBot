import os
import glob
import asyncio

from TelegramBotConfig import *
from DeepFaceFunctions import *
from TelegramBotHelper import *

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


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
    }

    @dp.message(Command(commands=['start', 'help']))
    async def start(message: Message):
        if storage['first_message']:
            print(f'First message by {message.from_user.first_name} | {message.from_user.id}')

            await bot.send_animation(message.from_user.id, "https://media1.tenor.com/m/5hKPyupKGWMAAAAC/robot-hello.gif")
            await bot.send_message(message.from_user.id, f"Hello, {message.from_user.first_name}! " \
                                   + "I'm BOT that working on Deepface and Tensorflow!" \
                                   + f"\n<a href='{github_link}'><b><u>Github</u></b></a>", parse_mode=ParseMode.HTML)

            storage['first_message'] = False

        await bot.send_message(message.from_user.id, start_message)

    # get image
    @dp.message(F.photo)
    async def get_image(message: Message):
        image = await get_image_from_message(bot, message)
        await bot.send_message(message.from_user.id, 'Got image')
        find_message = await bot.send_message(message.from_user.id, 'Finding in database...')
        asyncio.sleep(3)

        index = None
        for index_image_check, image_check_path in enumerate(glob.glob(f'{main_path}/{data_path}*.jpg')):
            image_check = cv2.imread(image_check_path)
            result = verify_in_photo(image, image_check, detector_backend_model, verify_model)

            if result['verified']:
                await bot.edit_message_text('Found in database', message.from_user.id, find_message.message_id)

                area = result['facial_areas']['img1']
                x, y, w, h = area['x'], area['y'], area['w'], area['h']
                x, y, w, h = border_resize(x, y, w, h, 50, 50, image.shape)

                face = image[y:y+h, x:x+w]

                send_image(bot, message, face, "Face in your photo")
                send_image(bot, message, image_check, "Face in database")

                index = index_image_check

                break
        else:
            await bot.edit_message_text("Didn't find in database", message.from_user.id, find_message.message_id)

            index = len(os.listdir(f'{main_path}/{data_path}')) // 2

            face_obj = faces_in_photo(image, detector_backend_model)[0]
            face_area = face_obj['facial_area']
            x, y, w, h = face_area['x'], face_area['y'], face_area['w'], face_area['h']
            x, y, w, h = border_resize(x, y, w, h, 50, 50, image.shape)

            face = image[y:y+h, x:x+w]
            send_image(bot, message, face, 'Founded face')

            saving_message = await bot.send_message(message.from_user.id, 'Saving...')
            cv2.imwrite(f'{main_path}/{data_path}{index}.jpg', face)
            with open(f'{main_path}/{data_path}{index}.txt', 'w') as file:
                file.write('5.0')
            await bot.edit_message_text('Saved', message.from_user.id, saving_message.message_id)

        with open(f"{main_path}/{data_path}{index}.txt") as rating_file:
            ratings = list(map(float, rating_file.read().split()))

        rate_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Rate this face", callback_data=f"RateFace{index}")]])
        rate_message = await bot.send_message(message.from_user.id, f'<u>Rating</u> this face: {sum(ratings) / len(ratings)}', parse_mode=ParseMode.HTML, reply_markup=rate_button)
        storage[rate_message.message_id] = index

    @dp.callback_query(F.data.startswith("RateFace"))
    async def get_grade(callback_query: CallbackQuery):
        await callback_query.message.edit_text(f"Rate this face!", reply_markup=rate_menu)

    @dp.callback_query(F.data.in_([str(i) for i in range(11)]))
    async def set_grade(callback_query: CallbackQuery):
        got_grade = float(callback_query.data)

        with open(f"{main_path}/{data_path}{storage[callback_query.message.message_id]}.txt", 'r+') as rating_file:
            ratings = list(map(float, rating_file.read().split()))
            rating_file.write(f' {got_grade}')

        await callback_query.message.edit_text(f"Your grade: {got_grade}\nNow his rating: {(got_grade + sum(ratings)) / (1 + len(ratings))}")

    # starting bot
    async def main():
        await bot.delete_webhook(drop_pending_updates=True)

        if to_log:
            info_bot = await bot.get_me()
            print(f"Starting bot {info_bot.first_name} with token {token} (aiogram)")
            print(f"https://t.me/{info_bot.username} | @{info_bot.username}")

        await dp.start_polling(bot)

    asyncio.run(main())
