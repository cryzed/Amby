import argparse
import atexit
import sys
import time

import qhue
from qhue import QhueException

from amby.config import get_saved_username, save_username
from amby.constants import NON_MODIFIABLE_STATES, PHILIPS_MAX_BRIGHTNESS, PHILIPS_MIN_BRIGHTNESS
from amby.core import get_average_color, get_pixel_data, get_relative_luminance, rgb_to_xy

SUCCESS_EXIT_CODE = 0
FAILURE_EXIT_CODE = 1

argument_parser = argparse.ArgumentParser()
argument_parser.add_argument('bridge_address', help='The domain or IP address of the Philips Hue Bridge')
argument_parser.add_argument(
    'lights', nargs='+',
    help='Specify the indices of the lights that should be controlled (1, 2, ..., n)')
argument_parser.add_argument(
    '--username', '-u',
    help='Override the username used to authenticate with the Philips Hue Bridge. If this argument is omitted and no'
         "username was created previously, you'll be prompted to create a new one")
argument_parser.add_argument(
    '--screen', '-s', type=int, help='Specify which screen should be used (1 ... n). Defaults to the primary screen')
argument_parser.add_argument(
    '--interval', '-i', type=float, default=0.1,
    help='The interval to wait before calculating and setting the ambient color again')
argument_parser.add_argument('--run-once', '-o', action='store_true', help='Set the ambient color once and exit')
argument_parser.add_argument(
    '--change-brightness', '-b', action='store_true',
    help='Adjust brightness of lights based on the luminance of the calculated ambient color')
argument_parser.add_argument(
    '--min-brightness', '-m', type=float, default=0, help='Minimum brightness in percent')
argument_parser.add_argument(
    '--max-brightness', '-M', type=float, default=100, help='Maximum brightness in percent')
argument_parser.add_argument('--enable', '-e', action='store_true', help='Enable disabled lights')
argument_parser.add_argument('--restore-state', '-r', action='store_true', help='Restore initial state of lights')


def stderr(*args, **kwargs):
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)


def prompt_create_username(bridge_address):
    choice = input('No username specified, do you want to create one now? [Y/n]: ')
    if choice.lower() in {'', 'y', 'yes'}:
        try:
            return qhue.create_new_username(bridge_address)
        except QhueException as exception:
            stderr(f'Exception occurred while creating the username: {exception}')


def change_light_state(bridge, light, state):
    for key in NON_MODIFIABLE_STATES:
        if key in state:
            del state[key]

    try:
        bridge.lights[light].state(**state)
    except QhueException as exception:
        stderr(f'Exception occurred while controlling light #{light}: {exception}')


def main_(arguments):
    username = arguments.username or get_saved_username()
    if not username:
        username = prompt_create_username(arguments.bridge_address)
        if not username:
            return FAILURE_EXIT_CODE
        save_username(username)
    bridge = qhue.Bridge(arguments.bridge_address, username)

    initial_states = {}
    for light in arguments.lights:
        state = bridge.lights[light]()['state']
        initial_states[light] = state
        if arguments.enable and not state['on']:
            bridge.lights[light].state(on=True)

    if arguments.restore_state:
        def restore_state():
            for light, state in initial_states.items():
                change_light_state(bridge, light, state)

        atexit.register(restore_state)

    previous_color = None
    min_brightness = max(PHILIPS_MIN_BRIGHTNESS, int(round(arguments.min_brightness / 100 * PHILIPS_MAX_BRIGHTNESS)))
    max_brightness = min(PHILIPS_MAX_BRIGHTNESS, int(round(arguments.max_brightness / 100 * PHILIPS_MAX_BRIGHTNESS)))
    if not arguments.run_once:
        print(f'Running, press Ctrl+C to stop Amby.')

    try:
        while True:
            data = get_pixel_data(arguments.screen)
            color = get_average_color(data)
            if color != previous_color:
                state = {'xy': rgb_to_xy(color)}
                if arguments.change_brightness:
                    state['bri'] = max(min_brightness, int(round(get_relative_luminance(color) * max_brightness)))

                for light in arguments.lights:
                    change_light_state(bridge, light, state)

            if arguments.run_once:
                break

            time.sleep(arguments.interval)
    except KeyboardInterrupt:
        pass

    return SUCCESS_EXIT_CODE


def main():
    arguments = argument_parser.parse_args()
    argument_parser.exit(main_(arguments))
