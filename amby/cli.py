#!/usr/bin/env python

import argparse
import sys
import time

import qhue
from qhue import QhueException

from amby.color import get_average_brightest_color, get_average_color
from amby.constants import SUCCESS_EXIT_CODE, FAILURE_EXIT_CODE
from amby.utils import rgb_to_xy, get_saved_username, save_username

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
    '--mode', '-m', choices=['average', 'luminance'], default='average',
    help='Specify the way the ambient color should be calculated. "average" calculates the average color of all pixels,'
         'while "luminance" averages the a given percentage of the brightest colors found (adjustable using '
         '--luminance-percentage).')
argument_parser.add_argument(
    '--luminance-percentage', '-l', type=float, default='10',
    help='Specify which percentage of brightest colors to average in luminance mode')


def stderr(*args, **kwargs):
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)


def prompt_create_username(bridge_address):
    choice = input(f'No username specified, do you want to create one now? [Y/n]: ')
    if choice.lower() not in {'', 'y', 'yes'}:
        return None

    try:
        return qhue.create_new_username(bridge_address)
    except QhueException as exception:
        stderr(f'Exception occurred while creating the username: {exception}')


def _main(arguments):
    username = arguments.username or get_saved_username()
    if not username:
        username = prompt_create_username(arguments.bridge_address)
        if username is None:
            return FAILURE_EXIT_CODE
        save_username(username)

    bridge = qhue.Bridge(arguments.bridge_address, username)

    def change_light_states(**kwargs):
        for light in arguments.lights:
            try:
                bridge.lights[light].state(**kwargs)
            except QhueException as exception:
                stderr(f'Exception occurred while controlling light #{light}: {exception}')

    # Create closures here so we don't have to constantly do useless string comparisons
    if arguments.mode == 'average':
        def calculate_color():
            return get_average_color(arguments.screen)
    else:
        def calculate_color():
            return get_average_brightest_color(arguments.screen, percentage=arguments.luminance_percentage)

    previous_color = None
    if not arguments.run_once:
        print(f'Running, press Ctrl+C to stop Amby.')
    try:
        while True:
            color = calculate_color()
            if color != previous_color:
                change_light_states(xy=rgb_to_xy(*color))
                previous_color = color

            if arguments.run_once:
                break

            time.sleep(arguments.interval)
    except KeyboardInterrupt:
        pass

    return SUCCESS_EXIT_CODE


def main():
    arguments = argument_parser.parse_args()
    argument_parser.exit(_main(arguments))
