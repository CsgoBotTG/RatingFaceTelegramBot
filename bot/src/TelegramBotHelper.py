import cv2
import requests
import numpy as np

from aiogram import Bot
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup

async def get_image_from_message(
        bot: Bot, 
        message: Message
    ) -> np.ndarray:
    """
    Get image from message

    :param bot: aiogram.Bot. Bot to get image
    :param message: aiogram.types.Messsage. To get image from message

    :return: np.ndarray. Image
    """

    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    file_bytes = await bot.download_file(file_path)
    file_bytes_arr = np.frombuffer(file_bytes.read(), np.uint8)
    file = cv2.imdecode(file_bytes_arr, cv2.IMREAD_COLOR)

    return np.array(file)


def send_image(
        bot: Bot, 
        message: Message, 
        image: np.ndarray, 
        caption: str = None
    ) -> bool:
    """
    Send image in return

    :param bot: aiogram.Bot. to send image
    :param message: aiogram.types.Message. to get chat id
    :param image: np.ndarray. to send image
    :param caption: str. caption of string

    :return: bool. Result
    """

    image = cv2.imencode('.jpg', image)[1].tostring()
    url = f"https://api.telegram.org/bot{bot.token}/sendPhoto"

    data = {'chat_id': message.from_user.id}
    if not caption is None:
        data['caption'] = caption

    result = requests.post(url, data=data, files={'photo': image})
    return result.json()['ok']

rate_txt = [
    ['0'],
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['10']
]
buttons_rate_menu = [[InlineKeyboardButton(text=text, callback_data=text) for text in list_text] for list_text in rate_txt]
rate_menu = InlineKeyboardMarkup(inline_keyboard=buttons_rate_menu)