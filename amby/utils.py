import os

import appdirs
import rgbxy

from amby.constants import APPLICATION_NAME, ENCODING

_color_converter = rgbxy.Converter()
_config_directory = appdirs.user_config_dir(APPLICATION_NAME)
_username_path = os.path.join(_config_directory, 'username.txt')


def rgb_to_xy(r, g, b):
    # Prevent DivisionByZero exception in rgbxy library:
    # https://github.com/benknight/hue-python-rgb-converter/issues/6
    r, g, b = tuple(max(component, 10 ** -3) for component in (r, g, b))
    return _color_converter.rgb_to_xy(r, g, b)


def get_saved_username():
    if not os.path.exists(_username_path):
        return None

    with open(_username_path, 'r', encoding=ENCODING) as file:
        # Strip trailing whitespace just in case the user decides to modify the file manually
        return file.read().strip()


def save_username(username):
    os.makedirs(_config_directory, exist_ok=True)
    with open(_username_path, 'w', encoding=ENCODING) as file:
        file.write(username)
