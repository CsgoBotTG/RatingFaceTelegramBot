import os

from sys import argv
from TelegramBotConfig import start_token
from TelegramBotStart import start_bot

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def main():
    os.system('cls')

    try:
        index = argv.index('-token') + 1
        token = argv[index]
    except Exception as err:
        print("Didn't find token")
        token = start_token

    start_bot(token=token, to_log=True)
