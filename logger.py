from typing import NoReturn
from termcolor import colored

def log(message: str, color: str) -> NoReturn:
    print(colored('[LOG]', color), message)


def warning_msg(message: str) -> NoReturn:
    print(colored('[WARNING]', 'yellow'), message)


def start_msg(message: str = None) -> NoReturn:
    print(colored('[START]', 'green'), message)


def complete_msg(message: str = None) -> NoReturn:
    print(colored('[COMPLETE]', 'green'), message)


def error_msg(message: str) -> str:
    '''Pass to Exception(error_msg...)'''

    return colored(f'[ERROR]: {message}', 'red')
