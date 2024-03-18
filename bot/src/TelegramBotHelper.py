import cv2
import numpy as np

from aiogram import Bot
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.input_file import BufferedInputFile


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


async def send_image(
        bot: Bot,
        message: Message,
        image: np.ndarray,
        caption: str = None
    ):
    """
    Send image

    :param bot: aiogram.Bot. Bot to get image
    :param message: aiogram.types.Messsage. To get chat id
    :param image: np.ndarray. Image what sent
    :param caption: str | None. String with image sended

    :raturn: None
    """

    _, image_bytes = cv2.imencode('.jpg', image)
    image_to_send = BufferedInputFile(image_bytes.tobytes(), 'image.jpg')

    await bot.send_photo(message.from_user.id, image_to_send, caption=caption)


def border_resize(
        x: int, y: int, w: int, h: int,
        pxx: int,
        pxy: int,
        image_shape: tuple
    ) -> tuple:
    """
    Resizing border of image without get out of his shape

    :param x, y, w, h: ints. Border
    :param pxx: int. Count of pixels, how many pixels add to weight
    :param pxx: int. Count of pixels, how many pixels add to height
    :param image_shape: tuple. Size of this image

    :return: tuple. New border
    """

    for i in range(pxx):
        if w < image_shape[0] - x - 1:
            if x > 0:
                x -= 1
                w += 2
            else:
                w += 1

    for i in range(pxy):
        if h < image_shape[1] - y - 1:
            if y > 0:
                y -= 1
                h += 2
            else:
                h += 1

    return x, y, w, h


rate_txt = [
    ['0'],
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['10']
]
buttons_rate_menu = [[InlineKeyboardButton(text=text, callback_data=text) for text in list_text]
                    for list_text in rate_txt]
rate_menu = InlineKeyboardMarkup(inline_keyboard=buttons_rate_menu)
