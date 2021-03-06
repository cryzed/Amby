import os

import appdirs

_ENCODING = 'UTF-8'
_APPLICATION_NAME = 'amby'
_config_directory = appdirs.user_config_dir(_APPLICATION_NAME)
_username_path = os.path.join(_config_directory, 'username.txt')


def get_saved_username():
    if not os.path.exists(_username_path):
        return None

    with open(_username_path, encoding=_ENCODING) as file:
        # Strip trailing whitespace just in case the user decides to modify the file manually
        return file.read().strip()


def save_username(username):
    os.makedirs(_config_directory, exist_ok=True)
    with open(_username_path, 'w', encoding=_ENCODING) as file:
        file.write(username)
