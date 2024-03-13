import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from sys import argv
from TelegramBotConfig import start_token

from TelegramBotStart import start_bot


def main():
    token = None
    try:
        index = argv.index('-token') + 1
        token = argv[index]
    except:
        print("Didn't find token")
        token = start_token

    start_bot(token=token, to_log=True)


if __name__ == '__main__':
    main()